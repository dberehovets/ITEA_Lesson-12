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
    article = StringField(max_length=32, required=True)
    description = StringField(max_length=4096)
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


# if __name__ == "__main__":
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

