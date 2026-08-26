import json

from user_directory import UserDirectory


directory = UserDirectory()
observations = []
for email in ("ada@example.com", "missing@example.com"):
    try:
        observations.append({"email": email, "result": directory.lookup(email)})
    except Exception as error:
        observations.append({"email": email, "error": type(error).__name__})
print(json.dumps(observations, sort_keys=True))
