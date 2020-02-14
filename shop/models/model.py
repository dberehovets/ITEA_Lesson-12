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
    category = Category.objects.get(title="Велика побутова техніка")
    Product(title='Вбудована посудомийна машина BOSCH',
            description='Повногабаритна (60 см)/ 1.02/290 кВт/ч',
            price=8599,
            category=category,
            image="https://i2.rozetka.ua/goods/4689897/bosch_smv24ax00k_images_4689897824.jpg").save()

    Product(title='Піч для піци HENDI Basic 2/40 VETRO',
            description="Двокамерна піч HENDI Basic 2/40 VETRO призначена для одночасного приготування 2 рум'яних піц "
                        "або коржів діаметром 30 см. Випічка пропікається до хрусткої скоринки рівномірно завдяки "
                        "розміщеним зверху та знизу тенам.",
            price=26520,
            category=category,
            image="https://i2.rozetka.ua/goods/10295302/hendi_basic_2_40_vetro_images_10295302419.jpg").save()


    category = Category.objects.get(title="Догляд та прибирання")
    Product(title='Праска Bosch TDA3026110',
            description='CeraniumGlissée Pro / 160 г/мин / З парою / Алюміній',
            price=1299,
            category=category,
            image="https://hotline.ua/img/tx/216/2165101215.jpg").save()

    Product(title='Швейна машина MINERVA M832B',
            description='Електромеханічна / Напівавтомат / Словаччина',
            price=3299,
            category=category,
            image="https://www.швейные-машинки.com.ua/3808-max_default/minerva-m-832-b.jpg").save()

    Product(title='Робот-пилосос ECOVACS DEEBOT OZMO 610',
            description='Тип прибирання -- Суха + волога',
            price=6399,
            category=category,
            image="https://hotline.ua/img/tx/220/2200206465.jpg").save()

    category = Category.objects.get(title="Сантехніка")
    Product(title='Унітаз VILLEROY&BOCH',
            description='Підвісний під інсталяцію',
            price=6950,
            category=category,
            image="https://i1.rozetka.ua/goods/1842464/6743734_images_1842464283.jpg").save()

    Product(title='Набір змішувачів для ванни',
            description='Набір 3 в 1 / Урізний / Настінний',
            price=2900,
            category=category,
            image="https://i1.rozetka.ua/goods/13291465/copy_imprese_horak_510170670_5d4bea759f53f_images_13291465702.jpg").save()


