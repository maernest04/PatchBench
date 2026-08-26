import json

from pricing import calculate_total


print(json.dumps([calculate_total(20, 3), calculate_total(20, 3, discount=0.25)]))
