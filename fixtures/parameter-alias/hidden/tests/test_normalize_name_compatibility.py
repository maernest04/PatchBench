from names import normalize_name


def test_normalize_name_retains_uppercase_keyword():
    assert normalize_name("  Ada Lovelace  ", uppercase=True) == "ADA LOVELACE"
