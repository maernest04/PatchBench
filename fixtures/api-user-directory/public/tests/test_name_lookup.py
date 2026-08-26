from user_directory import UserDirectory


def test_finds_user_by_name():
    user = UserDirectory().find_by_name("Grace Hopper")

    assert user == {"email": "grace@example.com", "name": "Grace Hopper"}
