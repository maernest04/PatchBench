import json

from user_store import UserStore


store = UserStore()
observations = []

store.create_user(42, "Ada")
observations.append({"operation": "get_user", "result": store.get_user(42)})
observations.append({"operation": "delete_user", "result": store.delete_user(42)})
observations.append({"operation": "get_user", "result": store.get_user(42)})

print(json.dumps(observations, sort_keys=True))
