from product_catalog import ProductCatalog


def test_lists_requested_page():
    products = ProductCatalog().list_page(2, 2)

    assert products == [{"sku": "C3", "name": "Cable"}]


def test_out_of_range_page_is_empty():
    assert ProductCatalog().list_page(3, 2) == []
