class SessionStore:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id, user_id, expires_at):
        self.sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "expires_at": expires_at,
        }

    def get_session(self, session_id, now):
        raise NotImplementedError
