import json

from profile_service import ProfileService


print(json.dumps(ProfileService().create_profile("u-1", "Ada Lovelace"), sort_keys=True))
