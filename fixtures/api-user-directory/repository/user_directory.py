class UserDirectory:
    def __init__(self):
        self._users = {
            "ada@example.com": {"email": "ada@example.com", "name": "Ada Lovelace"},
            "grace@example.com": {"email": "grace@example.com", "name": "Grace Hopper"},
        }

    def lookup(self, email):
        return self._users.get(email)
