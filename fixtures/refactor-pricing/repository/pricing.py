def calculate_total(unit_price, quantity, discount=0):
    subtotal = unit_price * quantity
    return subtotal - (subtotal * discount)
