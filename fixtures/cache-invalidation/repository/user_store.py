class UserStore:
    def __init__(self):
        self._users = {}
        self.database_reads = 0

    def create_user(self, user_id, name):
        self._users[user_id] = {"id": user_id, "name": name}

    def get_user(self, user_id):
        self.database_reads += 1
        return self._users.get(user_id)

    def delete_user(self, user_id):
        return self._users.pop(user_id, None) is not None
