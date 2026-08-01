from __future__ import annotations

from models import Session


class SessionStore:
    def __init__(self, sessions: list[Session] | None = None) -> None:
        self._sessions: dict[str, Session] = {
            session.session_id: session for session in (sessions or [])
        }

    def add_session(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def get_session(self, session_id: str) -> Session:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Unknown session: {session_id}") from exc
