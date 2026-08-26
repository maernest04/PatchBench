from pricing import PriceCalculator


def test_calculator_total():
    assert PriceCalculator().total(20, 3, discount=0.25) == 45
