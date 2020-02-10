from bot import TGBot
from shop.config import TOKEN
from shop.models.model import Texts, Category, Product
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


@bot.callback_query_handler(func=lambda call: True if "category" in call.data else False)
def get_categories(call):
    bot.send_subcategories(call)


@bot.callback_query_handler(func=lambda call: True if "product" in call.data else False)
def get_categories(call):
    print(call)
    # bot.send_message(call, "Продукт додано в кошик")


@bot.inline_handler(func=lambda query: True)
def get_products(query):
    bot.send_products(query)


if __name__ == "__main__":
    bot.polling()