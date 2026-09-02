class ProductCatalog:
    def __init__(self):
        self._products = [
            {"sku": "A1", "name": "Adapter"},
            {"sku": "B2", "name": "Battery"},
            {"sku": "C3", "name": "Cable"},
        ]

    def list_products(self):
        return list(self._products)
