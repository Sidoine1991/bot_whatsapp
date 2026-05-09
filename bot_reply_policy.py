"""
Politique de réponse automatique : éviter que le bot réponde à votre place lorsque vous
avez pris la main dans une conversation 1:1. Détection via les messages sortants (fromMe).

Variables d’environnement :
- BOT_AUTO_REPLY : true/false — désactiver toute réponse auto (défaut : true).

Prise en main (recommandé) :
- BOT_OWNER_HANDOFF_HOURS : après que vous ayez écrit à un contact (hors groupes), le bot
  ne répond plus à ce contact pendant N heures (défaut : 24). La fenêtre repart à zéro
  à chaque nouveau message sortant de votre part vers ce contact. Mettre 0 pour désactiver.

Pauses courtes optionnelles (complément) :
- BOT_SUPPRESS_SECONDS_AFTER_OWNER_OUTGOING : pause globale de N secondes après tout envoi.
- BOT_SUPPRESS_PER_CHAT_SECONDS : pause courte par contact (secondes).

Note : les groupes (@g.us) ne déclenchent pas la prise en main par contact ; seule une
pause globale éventuelle s’applique encore après un envoi dans un groupe.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Tuple

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_last_owner_outgoing_monotonic: float = 0.0
_last_owner_outgoing_by_chat: dict[str, float] = {}
_owner_handoff_walltime_by_chat: dict[str, float] = {}


def chat_key(phone_or_jid: str | None) -> str:
    """Identifiant conversation stable (chiffres du contact), quel que soit le suffixe JID."""
    if not phone_or_jid:
        return ""
    s = str(phone_or_jid).strip().split("/")[0]
    if "@" in s:
        s = s.split("@", 1)[0]
    return "".join(c for c in s if c.isdigit())


def normalize_whatsapp_jid(phone_or_jid: str | None) -> str:
    """JID courant pour logs / affichage."""
    digits = chat_key(phone_or_jid)
    if digits:
        return f"{digits}@s.whatsapp.net"
    return (phone_or_jid or "").strip()


def _is_group_jid(remote_jid: str | None) -> bool:
    return "@g.us" in (remote_jid or "").lower()


def _truthy_env(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _int_env(name: str, default: int = 0) -> int:
    try:
        return max(0, int(os.getenv(name, str(default)).strip()))
    except ValueError:
        return default


def _handoff_hours() -> float:
    """Heures de silence bot par contact après un message sortant (défaut 24). 0 = désactivé."""
    try:
        v = float(os.getenv("BOT_OWNER_HANDOFF_HOURS", "24").strip())
        return max(0.0, v)
    except ValueError:
        return 24.0


def record_owner_outgoing(remote_jid: str | None) -> None:
    """Appeler quand l’API signale un message envoyé par vous (fromMe)."""
    if not remote_jid or "@broadcast" in remote_jid:
        return
    key = chat_key(remote_jid)
    if not key:
        return
    now_mono = time.monotonic()
    now_wall = time.time()
    is_group = _is_group_jid(remote_jid)

    with _lock:
        global _last_owner_outgoing_monotonic
        _last_owner_outgoing_monotonic = now_mono

        if not is_group:
            _last_owner_outgoing_by_chat[key] = now_mono
            _owner_handoff_walltime_by_chat[key] = now_wall
            _prune_handoff_unlocked(now_wall)

        if len(_last_owner_outgoing_by_chat) > 2000:
            cutoff = now_mono - 3600.0
            dead = [k for k, t in _last_owner_outgoing_by_chat.items() if t < cutoff]
            for k in dead[:1000]:
                del _last_owner_outgoing_by_chat[k]


def _prune_handoff_unlocked(now_wall: float) -> None:
    hh = _handoff_hours()
    if hh <= 0:
        return
    max_age = hh * 3600.0 * 2
    stale = [k for k, t in _owner_handoff_walltime_by_chat.items() if now_wall - t > max_age]
    for k in stale[:500]:
        del _owner_handoff_walltime_by_chat[k]


def should_auto_reply_inbound(remote_jid: str | None) -> Tuple[bool, str]:
    """
    Indique si le bot doit répondre à un message entrant.
    Retourne (True, "") ou (False, raison courte pour les logs).
    """
    if not _truthy_env("BOT_AUTO_REPLY", "true"):
        return False, "BOT_AUTO_REPLY désactivé"

    ck = chat_key(remote_jid) if remote_jid else ""
    now_mono = time.monotonic()
    now_wall = time.time()

    with _lock:
        hh = _handoff_hours()
        if (
            hh > 0
            and remote_jid
            and ck
            and not _is_group_jid(remote_jid)
        ):
            last_wall = _owner_handoff_walltime_by_chat.get(ck, 0.0)
            if last_wall > 0:
                elapsed = now_wall - last_wall
                window = hh * 3600.0
                if elapsed < window:
                    remain_h = (window - elapsed) / 3600.0
                    return (
                        False,
                        f"vous avez pris cette conversation en main — bot en pause pour ce contact "
                        f"(encore ~{remain_h:.1f} h / réglez BOT_OWNER_HANDOFF_HOURS)",
                    )

        global_sec = _int_env("BOT_SUPPRESS_SECONDS_AFTER_OWNER_OUTGOING", 0)
        if global_sec > 0 and _last_owner_outgoing_monotonic:
            elapsed = now_mono - _last_owner_outgoing_monotonic
            if elapsed < global_sec:
                return (
                    False,
                    f"pause globale ({global_sec}s après un envoi depuis votre compte, "
                    f"reste ~{int(global_sec - elapsed)}s)",
                )

        chat_sec = _int_env("BOT_SUPPRESS_PER_CHAT_SECONDS", 0)
        if chat_sec > 0 and remote_jid and ck and not _is_group_jid(remote_jid):
            last = _last_owner_outgoing_by_chat.get(ck, 0.0)
            if last:
                elapsed = now_mono - last
                if elapsed < chat_sec:
                    return (
                        False,
                        f"pause courte sur ce contact ({chat_sec}s, reste ~{int(chat_sec - elapsed)}s)",
                    )

    return True, ""
