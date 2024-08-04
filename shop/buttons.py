from telebot import types


class Abstract_constants:
    """Счётчик нажатий на кнопки"""
    catalog_button = 0
    back_menu_button = 0
    back_category_button = 0
    back_start_menu_button = 0
    back_favorites_button = 0
    back_backet_button = 0
    back_products_menu_button = 0
    crowns_button = 0
    bracelets_button = 0
    earrings_button = 0
    necklaces_button = 0
    brooches_button = 0
    favorites_button = 0
    backet_button = 0
    add_favorites_button = 0
    remove_favorites_button = 0
    add_backet_button = 0
    remove_backet_button = 0
    check_leaders_button = 0
    web_site_button = 0


class UsersButtons:
    """Создание кнопок пользователя"""
    def __init__(self):
        self.menu = None
        self.category = None
        self.product_menu = None
        self.backet_menu = None

    def start_menu(self):
        """Начальное меню пользователя"""
        self.menu = types.InlineKeyboardMarkup()
        categorys = types.InlineKeyboardButton('Категори ', callback_data='categorys')
        leaders = types.InlineKeyboardButton('Лидеры\nпродаж', callback_data='leaders')
        favorites = types.InlineKeyboardButton('Избранное', callback_data='favorites')
        basket = types.InlineKeyboardButton('Корзина', callback_data='backet')
        website = types.InlineKeyboardButton('Наш сайт', callback_data='website', url='https://sogianna.ru/')
        self.menu.add(categorys, leaders, favorites, basket, website)
        return self.menu

    def menu_favorites(self):
        """Меню избранного"""
        favorites_menu = types.InlineKeyboardMarkup()
        order = types.InlineKeyboardButton("Отправить в корзину", callback_data="order")
        delete = types.InlineKeyboardButton("Удалить", callback_data="remove_from_favorites")
        basket = types.InlineKeyboardButton('Открыть корзину', callback_data='backet')
        back_start = types.InlineKeyboardButton("Назад", callback_data="back_start_menu")
        favorites_menu.add(order, delete, basket, back_start)
        return favorites_menu

    def menu_backet(self):
        """Меню корзины"""
        backet = types.InlineKeyboardMarkup()
        order = types.InlineKeyboardButton("Купить", callback_data="buy")
        back_start = types.InlineKeyboardButton("Назад", callback_data="back_start_menu")
        delete_backet = types.InlineKeyboardButton("Удалить из корзины", callback_data="delete_in_backet")
        backet.add(order, back_start, delete_backet)
        return backet

    def categorys(self):
        """Меню категорий"""
        self.category = types.InlineKeyboardMarkup()
        crowns = types.InlineKeyboardButton("Короны", callback_data="crowns")
        bracelets = types.InlineKeyboardButton("Браслеты", callback_data="bracelets")
        earrings = types.InlineKeyboardButton("Серьги", callback_data="earrings")
        necklaces = types.InlineKeyboardButton("Украшения на шею", callback_data="necklaces")
        brooches = types.InlineKeyboardButton("Брошь", callback_data="brooches")
        back_menu = types.InlineKeyboardButton("Назад", callback_data="back_start_menu")
        self.category.add(crowns, bracelets, earrings, necklaces, brooches, back_menu)
        return self.category

    def products_menu(self):
        """Меню продуктов"""
        self.product_menu = types.InlineKeyboardMarkup()
        add_to_favorites = types.InlineKeyboardButton("Добавить в избранное", callback_data="add_to_favorites")
        add_to_basket = types.InlineKeyboardButton("Добавить в корзину", callback_data="add_to_basket")
        back_category = types.InlineKeyboardButton("Назад", callback_data="back_category")
        self.product_menu.add(add_to_favorites, add_to_basket, back_category)
        return self.product_menu


class AdminButtons:
    """Создание кнопок админа"""
    def __init__(self):
        self.menu_admin = None

    def admin_menu(self):
        """Меню админа"""
        self.menu_admin = types.InlineKeyboardMarkup()
        add_products = types.InlineKeyboardButton("Добавить товар", callback_data="add_products")
        delete_product = types.InlineKeyboardButton("Удалить товар", callback_data="delete_product")
        change_availability = types.InlineKeyboardButton("Изменить наличие товара", callback_data="change_availability")
        view_counter = types.InlineKeyboardButton("Смотреть статистику", callback_data="view_counter")
        self.menu_admin.add(add_products, delete_product, change_availability, view_counter)
        return self.menu_admin







