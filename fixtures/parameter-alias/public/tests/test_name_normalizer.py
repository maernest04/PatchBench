from names import NameNormalizer


def test_normalizer_can_return_uppercase_name():
    assert NameNormalizer().normalize("  Ada Lovelace  ", upper=True) == "ADA LOVELACE"
