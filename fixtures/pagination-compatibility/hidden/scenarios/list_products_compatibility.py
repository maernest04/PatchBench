import json

from product_catalog import ProductCatalog


print(json.dumps(ProductCatalog().list_products(), sort_keys=True))
