# Pricing refactor

Introduce a `PriceCalculator` class with a `total(unit_price, quantity, discount=0)` method. Preserve the existing `calculate_total` function for callers that still use it.
