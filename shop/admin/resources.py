from flask_restful import Resource
from models.model import Category, Product
from admin.schema import CategorySchema, ProductSchema
from flask import jsonify, request


class Categories(Resource):
    def get(self):
        categories = Category.objects()

        return CategorySchema().dump(
            categories,
            many=True
        )

    def post(self):
        err = CategorySchema().validate(request.json)

        if err:
            return err

        category = Category.create(**request.get_json())

        category.reload()
        return CategorySchema().dump(category)

    def put(self):
        category = Category.objects.get(id=request.get_json()["id"])
        category.update(**request.get_json())
        category.reload()
        return CategorySchema().dump(category)

    def delete(self):
        category = Category.objects(id=request.get_json()["id"])
        category.delete()
        return CategorySchema().dump(category)


class Products(Resource):
    def get(self, category_id):
        category = Category.objects.get(id=category_id)
        products = category.get_products()

        return ProductSchema().dump(
            products,
            many=True
        )

    def post(self, category_id):
        err = ProductSchema().validate(request.json)

        if err:
            return err

        prod_data = request.get_json()
        prod_data["category"] = Category.objects.get(id=category_id)

        product = Product(**prod_data).save()

        product.reload()
        return ProductSchema().dump(product)

    def put(self):
        product = Product.objects.get(id=request.get_json()["id"])
        product.update(**request.get_json())
        product.reload()
        return ProductSchema().dump(product)

    def delete(self):
        product = Product.objects.get(id=request.get_json()["id"])
        product.delete()
        return ProductSchema().dump(product)