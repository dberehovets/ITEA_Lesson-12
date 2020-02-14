from mongoengine import *
connect("shop")


class User(Document):
    STATES = (
        ('products', "products"),
        ('categories', "categories")
    )
    telegram_id = StringField(max_length=32, required=True, unique=True)
    username = StringField(max_length=128)
    fullname = StringField(max_length=256)
    phone_number = StringField(max_length=20)
    state = StringField(choices=STATES)
    email = EmailField()
    address = StringField(max_length=256)


class Cart(Document):
    user = ReferenceField(User)
    is_archived = BooleanField(default=False)

    @classmethod
    def get_or_create_cart(cls, user_id):
        user = User.objects.get(telegram_id=str(user_id))

        try:
            return cls.objects.get(user=user, is_archived=False)
        except DoesNotExist:
            return cls.objects.create(user=user)

    def get_cart_products(self):
        products = []
        cart_products = CartProduct.objects(cart=self)
        for cart_product in cart_products:
            products.append(cart_product.product)
        return products

    def add_product_to_cart(self, product_id):

        CartProduct(cart=self, product=Product.objects.get(id=product_id)).save()

    def delete_product_from_cart(self, product):
        CartProduct.objects(cart=self, product=product).first().delete()

    # TO DO
    # Overthink
    # def get_sum(self):
    #     return CartProduct.objects.filter(cart=self).sum()


class CartProduct(Document):
    cart = ReferenceField(Cart)
    product = ReferenceField("Product")


class Attributes(EmbeddedDocument):
    height = FloatField()
    weight = FloatField()
    width = FloatField()


class Category(Document):
    title = StringField(min_length=1, max_length=255, required=True)
    description = StringField(max_length=4096)
    subcategories = ListField(ReferenceField("self"))
    parent = ReferenceField("self")
    is_root = BooleanField(default=False)

    @classmethod
    def create(cls, **kwargs):
        kwargs["subcategories"] = []
        if kwargs.get("parent"):
            kwargs["is_root"] = False
        return cls(**kwargs).save()

    def is_parent(self):
        return bool(self.parent)

    def add_subcategory(self, cat_obj):
        cat_obj.parent = self
        cat_obj.save()

        self.subcategories.append(cat_obj)
        self.save()

    def get_products(self):
        return Product.objects(category=self)

    def __str__(self):
        return self.title


class Product(Document):
    title = StringField(min_length=1, max_length=255, required=True)
    article = StringField(max_length=32)
    description = StringField(max_length=4096, required=True)
    price = IntField(required=True, min_value=0)
    in_stock = IntField(min_value=0, default=0)
    discount_price = IntField(min_value=1)
    attributes = EmbeddedDocumentField(Attributes)
    extra_data = StringField(max_length=4096)
    category = ReferenceField(Category, required=True)
    image = StringField(required=True)

    def get_price(self):
        return self.price if not self.discount_price else self.discount_price


class Texts(Document):
    TEXT_TYPES = (
        ("Greeting", "Greeting"),
        ("News", "News")
    )

    text_type = StringField(choices=TEXT_TYPES)
    body = StringField(max_length=2048)


if __name__ == "__main__":
    # cart = Cart.objects.first()
    # print(cart.get_cart().item_frequencies('product'))

    ## Creation #
    # category_dict = {
    #     'title': "root3",
    #     'description': "root3 desc",
    #     'is_root': True
    # }
    #
    # root_cat = Category.create(**category_dict)

    # for i in range(5):
    #     category_dict = {
    #         'title': f"category{i}",
    #         'description': f"category{i} description",
    #     }
    #     sub_cat = Category(**category_dict)
    #     root_cat.add_subcategory(sub_cat)
    ## End ###.

    # cats = Category.objects(is_root=True)
    #
    # for cat in cats:
    #     print(cat)
    #
    #     if cat.subcategories:
    #         for sub in cat.subcategories:
    #             print(f"Parent is {sub.parent}")
    #             print(f"sub cat - {sub}")

    #ITEMS FREQUENCIES
    # user = User(telegram_id="12345").save()
    #
    # cart = Cart.objects.first()
    #
    # products = []

    # for i in range(10):
    #     # title, article, category, price
    # prod = {
    #     'title': f"title1",
    #     'article': f"article1",
    #     'category': Category.objects.get(id="5e385585c53984f8ec4f63c1"),
    #     'price': 111,
    #     'image': "https://www.i-foto-graf.com/_pu/1/37961787.jpg"
    # }
    # product = Product.objects.create(**prod)
    # cart.add_product_to_cart(product)
    category = Category.objects.get(title="Комп'ютери")
    Product(title='Apple iMac 27"',
            description='Экран 27" IPS Retina (5120x2880), 5K LED, глянцевый / Intel Core i5 (3.0 ГГц) / RAM 16 ГБ / '
                    'SSD 256 ГБ / AMD Radeon Pro 570X, 4 ГБ / Ethernet 10/100/1000 / Wi-Fi 802.11 a/b/g/n/ac / '
                    'Bluetooth 4.2 / macOS Mojave / 650x516x203 мм, 9.44 кг / белый',
            price=74339,
            category=category,
            image="https://i.citrus.ua/uploads/content/product-photos/topchiy/March-2019/imac_01.jpg").save()

    Product(title='Acer Aspire C24-865',
            description='Екран 23.8" (1920x1080) Full HD IPS / Intel Core i3-8130U (2.2 - 3.4 ГГц) / RAM 8 ГБ / SSD 256 ГБ '
                    '/ Intel UHD Graphics 620 / без ОД / LAN / Wi-Fi / Bluetooth / кардридер / веб-камера / '
                    'Endless OS / 4 кг / сірий / клавіатура + миша',
            price=15999,
            category=category,
            image="https://img.moyo.ua/img/products/4285/32_600.jpg").save()

    Product(title='Everest Home 4070',
            description='Intel Core i3-9100F (3.6 - 4.2 ГГц) / RAM 8 ГБ / HDD 1 ТБ / nVidia GeForce GTX 1050 Ti, 4 ГБ / '
                    'Без ОД / LAN / без ОС',
            price=11699,
            category=category,
            image="https://i2.rozetka.ua/goods/10879158/everest_home_4070_9414_images_10879158147._S.jpg").save()

    category = Category.objects.get(title="Ноутбуки")
    Product(title='Apple MacBook Pro 16"',
            description='Экран 16" IPS (3072x1920), глянцевый / Intel Core i7-9750H (2.6 - 4.5 ГГц) / RAM 16 ГБ / '
                    'SSD 512 ГБ / AMD Radeon Pro 5300M, 4 ГБ / без ОД / Wi-Fi / Bluetooth / веб-камера / '
                    'macOS Catalina / 2.0 кг / серый космос',
            price=65445,
            category=category,
            image="https://www.apple.com/v/macbook-pro-16/b/images/meta/og__csakh451i0eq_large.png?201912040308").save()

    Product(title='HP Pavilion Gaming 15-cx0027ua',
            description='Екран 15.6" IPS (1920x1080) Full HD, матовий / Intel Core i5-8300H (2.3 — 4.0 ГГц) / RAM 8 ГБ / '
                    'SSD 256 ГБ / nVidia GeForce GTX 1050 Ti, 4 ГБ / без ОД / LAN / Wi-Fi / Bluetooth 4.2 / '
                    'вебкамера / DOS / 2.22 кг / сірий',
            price=18999,
            category=category,
            image="https://i2.rozetka.ua/goods/14633000/hp_pavilion_15_8kq92ea_images_14633000997.jpg").save()

    Product(title='Lenovo IdeaPad 330S-15IKB',
            description='Екран 15.6" IPS (1920x1080) Full HD, глянсовий з антивідблисковим покриттям / Intel Core i5-8250U '
                    '(1.6 - 3.4 ГГц) / RAM 6 ГБ / HDD 1 ТБ / nVidia GeForce GTX 1050, 4 ГБ / без ОД / Wi-Fi / '
                    'Bluetooth / веб-камера / Windows 10 Home 64bit / 1.87 кг / сірий',
            price=16999,
            category=category,
            image="https://i.citrus.ua/imgcache/size_500/uploads/shop/4/e/4eec78060b8b1e26ccca185d3cd2a7a2.jpg").save()

