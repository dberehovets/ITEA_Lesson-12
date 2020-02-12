from bot import TGBot
from shop.config import TOKEN
from shop.models.model import Texts, Category, Product, Cart
from shop.keyboards import START_KB, CATEGORIES_KB
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           InlineQueryResultArticle, InputTextMessageContent)

bot = TGBot(token=TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    # txt = Texts.objects(text_type="Greetings").get()
    txt = "Hello!"

    kb = ReplyKeyboardMarkup()
    buttons = [KeyboardButton(button_name) for button_name in START_KB.values()]
    kb.add(*buttons)

    bot.send_message(message.chat.id, txt, reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == START_KB["categories"])
def get_roots(message):
    bot.root_categories(message.chat.id)


@bot.message_handler(func=lambda message: message.text == START_KB["cart"])
def get_roots(message):

    bot.send_cart(message.from_user.id)


@bot.callback_query_handler(func=lambda call: True if "category" in call.data else False)
def get_categories(call):
    bot.send_subcategories(call)


@bot.callback_query_handler(func=lambda call: True if "product" in call.data else False)
def add_to_cart(call):
    cart = Cart.get_or_create_cart(user_id=call.from_user.id)
    cart.add_product_to_cart(product_id=call.data.replace("product", ""))
    bot.send_message(call.from_user.id, "Товар додано в кошик!")


@bot.inline_handler(func=lambda query: True)
def get_products(query):
    bot.send_products(query)


if __name__ == "__main__":
    bot.polling()