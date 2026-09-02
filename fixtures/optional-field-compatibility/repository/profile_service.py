class ProfileService:
    def create_profile(self, user_id, name):
        return {"id": user_id, "name": name}
