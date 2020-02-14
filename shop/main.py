from bot import TGBot
from config import TOKEN, WEBHOOK_URL, PATH
from models.model import Product, Cart, User, DoesNotExist
from keyboards import START_KB
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, Update)
from flask import Flask, request, abort

bot = TGBot(token=TOKEN)

app = Flask(__name__)


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
    # txt = Texts.objects(text_type="Greetings").get()
    txt = "Hello!"

    try:
        User.objects.get(telegram_id=str(message.from_user.id))
    except DoesNotExist:
        User(telegram_id=str(message.from_user.id)).save()

    kb = ReplyKeyboardMarkup()
    buttons = [KeyboardButton(button_name) for button_name in START_KB.values()]
    kb.add(*buttons)

    bot.send_message(message.chat.id, txt, reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == START_KB["categories"])
def get_roots(message):
    bot.root_categories(message.chat.id)


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
            cart.delete_product_from_cart(product)
    else:
        bot.send_message(call.message.chat.id, "Кошик порожній!")


@bot.inline_handler(func=lambda query: True)
def get_products(query):
    bot.send_products(query)


if __name__ == "__main__":
    # bot.polling()
    import time
    print("Started")
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=open("nginx-selfsigned.crt", "r")
    )

    app.run(host="127.0.0.1", port=5000, debug=True)