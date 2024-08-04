import logging

import PIL as pillow
import sqlalchemy
from telebot.types import PreCheckoutQuery
import telebot

from utils import process_product_id, process_add_product_id, process_product_info, \
    process_add_product_id_backet, process_product_id_backet, invoice_process
from bot import Shopbot
from config import token, admin_id


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
product_info = {}


def run_bot():
    shop = Shopbot(token=token)

    @shop.bot.message_handler(commands=['start'])
    def go_start(message):
        """Обработка команды старт"""
        logger.info(f"Команда 'start' получена от {message.from_user.id}")
        if message.from_user.id == int(admin_id):
            shop.start_menu_admin(message)
        else:
            shop.start(message=message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'website')
    def website_button():
        """Обработка кнопки наш сайт"""
        shop.web_site_button += 1

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'categorys')
    def go_catalog(call):
        """Обработка команды категории"""
        logger.info(f"Команда 'catalog' получена от {call.from_user.id}")
        shop.catalog(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'back_start_menu')
    def back_start_menu(call):
        """Обработка команды back_start_menu"""
        logger.info(f"Колбэк 'back_start_menu' получен от {call.from_user.id}")
        shop.back_start_menu(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'back_category')
    def back_category(call):
        """Обработка команды back_category"""
        logger.info(f"Колбэк 'back_category' получен от {call.from_user.id}")
        shop.back_category(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'crowns')
    def check_crowns(call):
        """Обработка команды корона"""
        logger.info(f"Колбэк 'crowns' получен от {call.from_user.id}")
        shop.crowns(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'bracelets')
    def check_bracelets(call):
        """Обработка команды браслеты"""
        logger.info(f"Колбэк 'bracelets' получен от {call.from_user.id}")
        shop.bracelets(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'earrings')
    def check_earrings(call):
        """Обработка команды серьги"""
        logger.info(f"Колбэк 'earrings' получен от {call.from_user.id}")
        shop.earrings(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'necklaces')
    def check_necklaces(call):
        """Обработка команды украшения на шею"""
        logger.info(f"Колбэк 'necklaces' получен от {call.from_user.id}")
        shop.necklaces(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'brooches')
    def check_brooches(call):
        """Обработка команды брошь"""
        logger.info(f"Колбэк 'brooches' получен от {call.from_user.id}")
        shop.brooches(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'favorites')
    def check_favorites(call):
        """Обработка команды фавориты"""
        logger.info(f"Колбэк 'favorites' получен от {call.from_user.id}")
        shop.get_to_favorites(message=call.message, user_id=call.from_user.id)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'remove_from_favorites')
    def prompt_for_product_id(call):
        """Обработка команды удаление из избранного"""
        shop.bot.send_message(call.from_user.id, "Отправьте номер товара.")
        shop.bot.register_next_step_handler_by_chat_id(call.from_user.id, process_product_id)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'add_to_favorites')
    def prompt_for_product_id(call):
        """Обработка команды добавление в избранное"""
        logger.info(f"Пользователь {call.from_user.id} начал добавление товара в избранное.")
        shop.bot.send_message(call.from_user.id, "Отправьте номер товара.")
        shop.bot.register_next_step_handler_by_chat_id(call.from_user.id, process_add_product_id)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'leaders')
    def check_leaders(call):
        """Обработка команды лидеры"""
        logger.info(f"Колбэк 'leaders' получен от {call.from_user.id}")
        shop.check_leaders(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'view_counter')
    def statistics(call):
        """Обработка команды статистика"""
        logger.info(f"Команда 'view_counter' получена от {call.from_user.id}")
        shop.shetchik(message=call.message)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'add_products')
    def add_product_handler(call):
        """Обработка команды добавление продуктов"""
        logger.info(f"Команда 'add_products' получена от {call.from_user.id}")
        if call.from_user.id == int(admin_id):
            try:
                msg = shop.bot.send_message(call.from_user.id, "Отправьте информацию о товаре.")
                shop.bot.register_next_step_handler(msg, process_product_info)
                logger.info("Обработчик следующего шага зарегистрирован для получения информации о товаре.")
            except Exception as e:
                logger.error(f"Ошибка при регистрации обработчика следующего шага: {e}")

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'delete_product')
    def add_product_handler(call):
        """Обработка команды удаление продуктов"""
        logger.info(f"Команда 'delete_product' по"
                    f"лучена от {call.from_user.id}")
        if call.from_user.id == int(admin_id):
            try:
                msg = shop.bot.send_message(call.from_user.id, "Отправьте номер товара.")
                shop.bot.register_next_step_handler(msg, shop.bot.remove_product)
                logger.info("Обработчик следующего шага зарегистрирован для получения информации о товаре.")
            except Exception as e:
                logger.error(f"Ошибка при регистрации обработчика следующего шага: {e}")

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'backet')
    def backet(call):
        """Обработка команды корзина"""
        logger.info(f"Колбэк 'backet' получен от {call.from_user.id}")
        shop.get_to_backet(message=call.message, user_id=call.from_user.id)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'add_to_basket')
    def prompt_for_product_id(call):
        """Обработка команды добавление в корзину"""
        return add_backet(call=call)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'order')
    def add_backet(call):
        """Обработка команды добавление в корзину"""
        logger.info(f"Пользователь {call.from_user.id} начал добавление товара в корзину.")
        shop.bot.send_message(call.from_user.id, "Отправьте номер товара.")
        shop.bot.register_next_step_handler_by_chat_id(call.from_user.id, process_add_product_id_backet)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'delete_in_backet')
    def prompt_for_product_id(call):
        """Обработка команды удаление из корзины"""
        shop.bot.send_message(call.from_user.id, "Отправьте номер товара.")
        shop.bot.register_next_step_handler_by_chat_id(call.from_user.id, process_product_id_backet)

    @shop.bot.callback_query_handler(func=lambda call: call.data == 'buy')
    def buy(call):
        """Обработка команды покупка товара"""
        logger.info(f"Команда 'buy' получена от {call.from_user.id}")
        shop.bot.send_message(call.from_user.id, "Пожалуйста, введите ID товара.")
        shop.bot.register_next_step_handler_by_chat_id(call.from_user.id, invoice_process)

    @shop.bot.pre_checkout_query_handler(lambda q: True)
    def checkout_process(pre_checkout_query: PreCheckoutQuery):
        """Обработка результата покупки"""
        shop.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    shop.bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    while True:
        try:
            run_bot()
        except Exception as e:
            logger.error(f"Ошибка: {e}")


