from config import WEBHOOK_URL, TOKEN, PATH
from models.model import Category, Product, Cart, User, DoesNotExist
from keyboards import START_KB
from telebot.types import (ReplyKeyboardMarkup, Update, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from flask import Flask, request, abort
from bot import TGBot
from flask_restful import Api
from admin.resources import *

app = Flask(__name__)
bot = TGBot(token=TOKEN)
api = Api(app)

api.add_resource(Categories, "/categories")
api.add_resource(Products, "/products")


@app.route(f'/{PATH}', methods=['POST'])
def webhook():
    """
    Function process webhook call
    """
    if request.headers.get('content-type') == 'application/json':

        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''

    else:
        abort(403)


@bot.message_handler(commands=["start"])
def start(message):
    txt = "Hello!"

    try:
        User.objects.get(telegram_id=str(message.from_user.id))
    except DoesNotExist:
        User(telegram_id=str(message.from_user.id)).save()

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [KeyboardButton(button_name) for button_name in START_KB.values()]
    kb.add(*buttons)

    bot.send_message(message.chat.id, txt, reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == START_KB["categories"])
def get_roots(message):
    bot.root_categories(message)


@bot.message_handler(func=lambda message: message.text == START_KB["cabinet"])
def get_cabinet(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Історія замовлень", switch_inline_query_current_chat="history"))
    bot.send_message(message.chat.id, "Особистий кабінет", reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == START_KB["cart"])
def get_cart(message):
    bot.send_cart(message.from_user.id)


@bot.callback_query_handler(func=lambda call: True if "category" in call.data else False)
def get_categories(call):
    bot.send_subcategories(call)


@bot.callback_query_handler(func=lambda call: True if "product" in call.data else False)
def add_to_cart(call):
    cart = Cart.get_or_create_cart(user_id=call.from_user.id)
    cart.add_product_to_cart(product_id=call.data.replace("product", ""))
    bot.send_message(call.from_user.id, "Товар додано в кошик!")


@bot.callback_query_handler(func=lambda call: True if "back" in call.data else False)
def back(call):
    category = Category.objects.get(id=call.data.replace("back", ""))
    if category.is_root:
        bot.root_categories(call.message, going_back=True)
    else:
        bot.send_subcategories(call)


@bot.callback_query_handler(func=lambda call: True if "delete" in call.data else False)
def delete_from_cart(call):
    product = Product.objects.get(id=call.data.replace("delete", ""))
    cart = Cart.get_or_create_cart(user_id=call.from_user.id)
    cart.delete_product_from_cart(product)
    bot.edit_message_caption(caption="Товар видалено з кошика!",  chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: True if "order" in call.data else False)
def make_order(call):
    cart = Cart.get_or_create_cart(user_id=call.from_user.id)
    products = cart.get_cart_products()
    if products:
        bot.send_message(call.message.chat.id,
                         f"Дякуюємо, {call.from_user.first_name}! Менеджер зв'яжеться з вами для підтвердження доставки.")
        bot.send_message(chat_id=438422378, text=f"{call.from_user.first_name} {call.from_user.last_name} зробив замовлення:")
        for product in products:
            bot.send_message(chat_id=438422378, text=product.title)
            cart.archive_product(product)
    else:
        bot.send_message(call.message.chat.id, "Кошик порожній!")


@bot.inline_handler(func=lambda query: "history" not in query.query)
def get_products(query):
    bot.send_products(query)


@bot.inline_handler(func=lambda query: "history" in query.query)
def get_products(query):
    bot.send_cart_history(query)


if __name__ == "__main__":

    import time
    print("Started")
    bot.remove_webhook()
    # bot.polling()
    time.sleep(1)
    bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=open("nginx-selfsigned.crt", "r")
    )

    app.run(host="127.0.0.1", port=5000, debug=True)