from profile_service import ProfileService


def test_includes_provided_nickname():
    profile = ProfileService().create_profile("u-1", "Ada Lovelace", "Ada")

    assert profile == {"id": "u-1", "name": "Ada Lovelace", "nickname": "Ada"}
