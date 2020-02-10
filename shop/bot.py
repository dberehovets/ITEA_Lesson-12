from telebot import TeleBot, types
from models.model import Category, Product


class TGBot(TeleBot):

    def __init__(self, token, *args):
        super().__init__(token, *args)

    def root_categories(self, user_id, force_send=True):
        cats = Category.objects.filter(is_root=True)

        kb = types.InlineKeyboardMarkup()

        buttons = [types.InlineKeyboardButton(callback_data="category" + str(cat.id), text=cat.title) for cat in cats
                   if cat.subcategories]
        buttons = buttons + [types.InlineKeyboardButton(text=cat.title, switch_inline_query_current_chat=str(cat.id))
                             for cat in cats if not cat.subcategories]

        kb.add(*buttons)
        if not force_send:
            return kb

        self.send_message(user_id, "Виберіть категорію", reply_markup=kb)

    def send_subcategories(self, call, user_id=None, text=None, force_send=True):

        # if not all([user_id, text]) and force_send:
        #     raise Exception("Force send cannot be used without user_id or text")

        kb = types.InlineKeyboardMarkup()

        category = Category.objects.get(id=call.data.replace("category", ""))

        buttons = [types.InlineKeyboardButton(callback_data="category" + str(cat.id), text=cat.title) for cat in category.subcategories
                   if cat.subcategories]
        buttons = buttons + [types.InlineKeyboardButton(text=cat.title, switch_inline_query_current_chat=str(cat.id))
                             for cat in category.subcategories if not cat.subcategories]

        kb.add(*buttons)
        self.edit_message_text(category.title, message_id=call.message.message_id,
                              chat_id=call.message.chat.id, reply_markup=kb)

    def send_products(self, query):

        category = Category.objects.get(id=query.query)
        products = category.get_products()

        results = []
        for product in products:

            kb = types.InlineKeyboardMarkup()

            button = types.InlineKeyboardButton(text="Додати в кошик", callback_data="product" + str(product.id))
            kb.add(button)
            result1 = types.InlineQueryResultArticle(
                id=str(product.id),
                title=product.title,
                description=f"{product.price} грн",
                input_message_content=types.InputTextMessageContent(parse_mode="HTML",
                                                disable_web_page_preview=False,
                                                message_text=f"{product.title} - {product.price} грн <a href='{product.image}'>&#8204</a>"
                                                ),
                thumb_url="https://www.i-foto-graf.com/_pu/1/37961787.jpg",
                reply_markup=kb
            )
            results.append(result1)
        self.answer_inline_query(query.id, results, cache_time=0)