from telebot import TeleBot, types
from config import TOKEN
from keyboards import START_KB

bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    buttons = START_KB.values()
    kb = types.InlineKeyboardMarkup()

    inline_buttons = [types.InlineKeyboardButton(text=button, switch_inline_query_current_chat=button)
                      for button in buttons]

    kb.add(*inline_buttons)
    bot.send_message(message.chat.id, "text", reply_markup=kb)


@bot.inline_handler(func=lambda query: True)
def inline(query):
    results = []
    for i in range(10):
        kb = types.InlineKeyboardMarkup()

        button = types.InlineKeyboardButton(text="Додати в кошик", callback_data=str(i))
        kb.add(button)
        result1 = types.InlineQueryResultArticle(
            id=i,
            title=f"Назва",
            description='Опис',
            input_message_content=types.InputTextMessageContent(message_text="Description"),
            url="https://www.i-foto-graf.com/_pu/1/37961787.jpg",
            reply_markup=kb
        )
        results.append(result1)
    bot.answer_inline_query(query.id, results, cache_time=0)


@bot.chosen_inline_handler(func=lambda chosen_result: True)
def chosen_result(chosen_result):
    print(chosen_result)

bot.polling()