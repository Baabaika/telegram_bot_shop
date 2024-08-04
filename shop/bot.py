from sqlalchemy.exc import SQLAlchemyError
from buttons import Abstract_constants, UsersButtons, AdminButtons
import telebot
from dbbot import DbShop
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Shopbot(Abstract_constants):
    def __init__(self, token):
        self.token = token
        self.bot = telebot.TeleBot(token=self.token)
        self.user_buttons = UsersButtons()
        self.base = DbShop(dbname='dbbottest', user='postgres', password='admin', host='localhost', port='5432')
        self.admin_buttons = AdminButtons()

    def __setattr__(self, name, value):
        """"""
        super().__setattr__(name, value)
        if hasattr(Abstract_constants, name):
            setattr(Abstract_constants, name, getattr(Abstract_constants, name) + 1)

    def start(self, message):
        """Стартовое меню пользователя
        :param message: экземпляр telebot message"""
        self.bot.send_message(message.chat.id, f"здравствуйте {message.from_user.first_name}!",
                              reply_markup=self.user_buttons.start_menu())

    def catalog(self, message):
        """Счётчик нажатия на кнопки
        :param message: экземпляр telebot message"""
        self.__setattr__("catalog_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.categorys())

    def back_menu(self, message):
        """Возвращение в главное меню
        :param message: экземпляр telebot message"""
        self.__setattr__("back_menu_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.start_menu())

    def back_category(self, message):
        """Возвращение в меню категории
        :param message: экземпляр telebot message"""
        self.__setattr__("back_category_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.categorys())

    def back_start_menu(self, message):
        """Возвращение в главное меню
        :param message: экземпляр telebot message"""
        self.__setattr__("back_start_menu_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.start_menu())

    def menu_backet(self, message):
        """Меню корзина
        :param message: экземпляр telebot message"""
        self.__setattr__("back_backet_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.menu_backet())

    def back_products_menu(self, message):
        """Возвращение в меню продуктов
        :param message: экземпляр telebot message"""
        self.__setattr__("back_products_menu_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.products_menu())

    def crowns(self, message):
        """Категория корона
        :param message: экземпляр telebot message"""
        self.__setattr__("crowns_button", 1)
        self.send_products(message, 'корона')

    def bracelets(self, message):
        """Категория браслеты
        :param message: экземпляр telebot message"""
        self.__setattr__("bracelets_button", 1)
        self.send_products(message, 'браслет')

    def earrings(self, message):
        """Категория серьги
        :param message: экземпляр telebot message"""
        self.__setattr__("earrings_button", 1)
        self.send_products(message, 'серьги')

    def necklaces(self, message):
        """Категория украшения на шею
        :param message: экземпляр telebot message"""
        self.__setattr__("necklaces_button", 1)
        self.send_products(message, 'украшения на шею')

    def brooches(self, message):
        """Категория браслеты
        :param message: экземпляр telebot message"""
        self.__setattr__("brooches_button", 1)
        self.send_products(message, 'брошь')

    def send_products(self, message, product_name: str):
        """Выгрузка товаров по имени
        message: экземпляр telebot message, product_name: str"""
        product_infos = self.base.get_product_by_name(product_name)
        if product_infos:
            for product_info in product_infos:
                stock = "В наличии" if product_info.in_stock == "да" else "Нет в наличии"
                response_message = f"Номер товара: {product_info.id}\n" \
                                   f"Название: {product_info.name}\n" \
                                   f"Описание: {product_info.description}\n" \
                                   f"Цена: {product_info.price} руб.\n" \
                                   f"В наличии: {stock}"
                self.bot.send_message(message.chat.id, response_message)
                # Предполагается, что у вас есть метод для отправки фото
                self.bot.send_photo(message.chat.id, open(product_info.photo, 'rb'),
                                    reply_markup=self.user_buttons.products_menu())
        else:
            self.bot.send_message(message.chat.id, "Продукт 'Браслет' не найден.",
                                  reply_markup=self.user_buttons.products_menu())

    def menu_favorites(self, message):
        """Меню избранное
        :param message: экземпляр telebot message"""
        self.__setattr__("back_favorites_button", 1)
        self.bot.send_message(message.chat.id, "Выберите раздел", reply_markup=self.user_buttons.menu_favorites())

    def get_to_favorites(self, message, user_id: int):
        """Выгрузка товаров в избранном
        :param message: экземпляр telebot message, user_id: int"""
        self.__setattr__("favorites_button", 1)
        logger.info(f"Колбэк 'favorites' в файле получен от {message.from_user.id}")
        get_favorites = self.base.get_favorites(user_id)
        if get_favorites:
            for favorit in get_favorites:
                stock = "В наличии" if favorit['in_stock'] == "да" else "Нет в наличии"
                response_message = f"Номер товара: {favorit['id']}\n" \
                                   f"Название: {favorit['name']}\n" \
                                   f"Описание: {favorit['description']}\n" \
                                   f"Цена: {favorit['price']} руб.\n" \
                                   f"В наличии: {stock}"
                self.bot.send_message(message.chat.id, response_message)
                # Предполагается, что у Вас есть метод для отправки фото
                self.bot.send_photo(message.chat.id, open(favorit['photo'], 'rb'))
            self.bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=self.user_buttons.menu_favorites())
        else:
            self.bot.send_message(message.chat.id, "В избранном пусто.",
                                  reply_markup=self.user_buttons.menu_favorites())

    def add_to_favorites(self, message, product_id: int):
        """Добавление товаров в избранное
        :param message: экземпляр telebot message, product_id: int"""
        self.__setattr__("add_favorites_button", 1)
        user_id = message.from_user.id
        if int(product_id) <= 0:
            self.bot.send_message(message.chat.id,
                                  "Повторите попытку\nНомер продукта должно быть целое положительное число")
        else:
            if self.base.add_product_to_favorites(user_id, int(product_id)):
                self.bot.send_message(message.chat.id, "товар добавлен в избранное")
            else:
                self.bot.send_message(message.chat.id, "товар уже в избранном")

    def remove_from_favorites(self, message, product_id):
        """Удаление товаров из избранного
        :param message: экземпляр telebot message, product_id: int"""
        self.__setattr__("remove_favorites_button", 1)
        try:
            if self.base.remove_favorite_by_id(message.from_user.id, product_id):
                self.bot.send_message(message.chat.id, f"Товар с номером {product_id} удален из избранного")
            else:
                self.bot.send_message(message.chat.id, f"Товар с номером {product_id} не найден в избранном")
        except Exception as e:
            self.bot.send_message(message.chat.id, f"Ошибка при удалении из избранного: {e}")

    def get_to_backet(self, message, user_id):
        """Выгрузка товаров в корзине
        :param message: экземпляр telebot message, user_id: int"""
        self.__setattr__("backet_button", 1)
        get_backets = self.base.get_cart_by_user(user_id)
        if get_backets:
            for get_backet in get_backets:
                stock = "В наличии" if get_backet['in_stock'] == "да" else "Нет в наличии"
                response_message = f"Номер товара: {get_backet['id']}\n" \
                                   f"Название: {get_backet['name']}\n" \
                                   f"Описание: {get_backet['description']}\n" \
                                   f"Цена: {get_backet['price']} руб.\n" \
                                   f"В наличии: {stock}"
                self.bot.send_message(message.chat.id, response_message)
                # Предполагается, что у Вас есть метод для отправки фото
                self.bot.send_photo(message.chat.id, open(get_backet['photo'], 'rb'))
            self.bot.send_message(message.chat.id, 'Выберите раздел', reply_markup=self.user_buttons.menu_backet())
        else:
            self.bot.send_message(message.chat.id, "В корзине пусто.", reply_markup=self.user_buttons.menu_backet())

    def add_to_backet(self, message, product_id):
        """Добавление товаров в корзину
        :param message: экземпляр telebot message, product_id: int"""
        self.__setattr__("add_backet_button", 1)
        user_id = message.from_user.id
        if int(product_id) <= 0:
            self.bot.send_message(message.chat.id,
                                  "Повторите попытку\nНомер продукта должно быть целое положительное число")
        else:
            if self.base.add_product_to_cart(user_id, int(product_id)):
                self.bot.send_message(message.chat.id, "товар добавлен в корзину")
                self.base.remove_favorite_by_id(user_id, int(product_id))
            else:
                self.bot.send_message(message.chat.id, "товар уже в корзине")

    def remove_from_backet(self, message, product_id):
        """Удаление товаров из корзины
        :param message: экземпляр telebot message, product_id: int"""
        self.__setattr__("remove_backet_button", 1)
        try:
            if self.base.remove_product_from_cart(message.from_user.id, product_id):
                self.bot.send_message(message.chat.id, f"Товар с номером {product_id} удален из корзины")
            else:
                self.bot.send_message(message.chat.id, f"Товар с номером {product_id} не найден в корзине")
        except Exception as e:
            self.bot.send_message(message.chat.id, f"Ошибка при удалении из корзины: {e}")

    def check_leaders(self, message):
        """Выгрузка лидеров
        :param message: экземпляр telebot message"""
        self.__setattr__("check_leaders_button", 1)
        try:
            leaders = self.base.get_top_selling_products()
            if leaders:
                for leader in leaders:
                    stock = "В наличии" if leader['in_stock'] == "да" else "Нет в наличии"
                    response_message = f"Номер товара: {leader['id']}\n" \
                                       f"Название: {leader['name']}\n" \
                                       f"Описание: {leader['description']}\n" \
                                       f"Цена: {leader['price']} руб.\n" \
                                       f"В наличии: {stock}"
                    self.bot.send_message(message.chat.id, response_message,
                                          reply_markup=self.user_buttons.products_menu())
            else:
                self.bot.send_message(message.chat.id, "Лидеров пока нет.",
                                      reply_markup=self.user_buttons.products_menu())
        except SQLAlchemyError as e:
            self.bot.send_message(message.chat.id, f"Ошибка при при выгрузке лидеров: {e}")

    def start_menu_admin(self, message):
        """Меню для админа
        :param message: экземпляр telebot message"""
        self.bot.send_message(message.chat.id, f"здравствуйте {message.from_user.first_name}!",
                              reply_markup=self.admin_buttons.admin_menu())

    def add_product(self, name: str, description: str, price: int, in_stock: str, photo):
        """Добавление товаров админом в базу
        name: str, description: str, price: int, in_stock: str"""
        logger.info(f"Попытка добавить продукт: {name}")
        try:
            self.base.add_product_bd(name, description, price, in_stock, photo)
            logger.info(f'Продукт {name} успешно добавлен в базу данных.')
        except Exception as e:
            self.base.session.rollback()
            logger.exception(f'Ошибка при добавлении продукта: {e}')

    def remove_product(self, product_id: int):
        """Удаление товаров админом из базы
        :product_id: int"""
        logger.info(f"Попытка удалить продукт с номером: {product_id}")
        try:
            self.base.remove_product_by_id(product_id=product_id)
            logger.info(f'Продукт с номером {product_id} успешно удалён из базы данных.')
        except Exception as e:
            self.base.session.rollback()
            logger.exception(f'Ошибка при удаления продукта: {e}')

    def shetchik(self, message):
        """Статистика нажатия на кнопки
        :param message: экземпляр telebot message"""
        obj = f"На кнопку каталог нажали: {Abstract_constants.catalog_button}\n" \
              f"На кнопку короны нажали: {Abstract_constants.crowns_button}\n" \
              f"На кнопку браслеты нажали: {Abstract_constants.bracelets_button}\n" \
              f"На кнопку серьги нажали: {Abstract_constants.earrings_button}\n" \
              f"На кнопку украшения на шею нажали: {Abstract_constants.necklaces_button}\n" \
              f"На кнопку броши нажали: {Abstract_constants.brooches_button}\n" \
              f"На кнопку в меню избранное нажали: {Abstract_constants.add_favorites_button}\n" \
              f"На кнопку наш сайт нажали: {Abstract_constants.crowns_button}"
        self.bot.send_message(message.chat.id, obj)







