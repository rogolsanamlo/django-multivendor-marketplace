class CompareStoreProduct:

    def __init__(self, request):
        self.session = request.session

        compare_store_product = self.session.get(
            'compare_store_product'
        )

        if not compare_store_product:
            compare_store_product =self.session['compare_store_product'] = []


        self.compare_store_product = compare_store_product

        self.count = len(
            self.compare_store_product
        )

    def __iter__(self):
        compare_store_product = (
            self.compare_store_product.copy()
        )

        for item in compare_store_product:
            yield item

    def add(self, store_product_id):
        store_product_id = int(
            store_product_id
        )

        if store_product_id not in self.compare_store_product:
            self.compare_store_product.append(
                store_product_id
            )

        self.count = len(
            self.compare_store_product
        )

        self.session.modified = True

    def remove(self, store_product_id):
        store_product_id = int(
            store_product_id
        )

        if store_product_id in self.compare_store_product:
            self.compare_store_product.remove(
                store_product_id
            )

        self.count = len(
            self.compare_store_product
        )

        self.session.modified = True

    def clear(self):
        if 'compare_store_product' in self.session:
            del self.session['compare_store_product']
            self.session.modified = True

        self.compare_store_product = []
        self.count = 0