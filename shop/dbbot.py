import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

cart_table = Table('cart', Base.metadata,
	Column('user_id', Integer, ForeignKey('users.id')),
	Column('product_id', Integer, ForeignKey('products.id')))

favorite_table = Table('favorites', Base.metadata,
	Column('user_id', Integer, ForeignKey('users.id')),
	Column('product_id', Integer, ForeignKey('products.id'))
)

cart_item_table = Table('cart_items', Base.metadata,
	Column('user_id', Integer, ForeignKey('users.id')),
	Column('product_id', Integer, ForeignKey('products.id'))
)


class Product(Base):
	"""Создание таблицы продукт"""
	__tablename__ = 'products'
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, nullable=False)
	description = Column(String)
	price = Column(Integer, nullable=False)
	in_stock = Column(String, default="да")
	photo = Column(String)
	sold_count = Column(Integer, default=0)

	cart_items = relationship('CartItem', back_populates='product')
	users = relationship('User', secondary=cart_table, back_populates='products')
	favorites = relationship('Favorite', back_populates='product')  # Added favorites relationship
	orders = relationship('Orders', back_populates='product')

	def __init__(self, name, description, price, in_stock, photo):
		self.name = name
		self.description = description
		self.price = price
		self.in_stock = in_stock
		self.photo = photo
		self.favorites = []


class User(Base):
	"""Создание таблицы пользователь"""
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	products = relationship('Product', secondary=cart_table, back_populates='users')
	favorites = relationship('Favorite', back_populates='user')
	cart_items = relationship('CartItem', back_populates='user')
	orders = relationship('Orders', back_populates='user')


class Favorite(Base):
	"""Создание таблицы избранное"""
	__tablename__ = 'favorites'
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
	name = Column(String, nullable=False)
	description = Column(String)
	price = Column(Integer, nullable=False)
	in_stock = Column(String, default="да")
	photo = Column(String)
	sold_count = Column(Integer, default=0)

	user = relationship('User', back_populates='favorites')
	product = relationship('Product', back_populates='favorites')

	__table_args__ = {'extend_existing': True}


####### СОЗДАНИЕ ТАБЛИЦЫ КОРЗИНА
class CartItem(Base):
	"""Создание таблицы корзина"""
	__tablename__ = 'cart_items'
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
	name = Column(String, nullable=False)
	description = Column(String)
	price = Column(Integer, nullable=False)
	in_stock = Column(String, default="да")
	photo = Column(String)
	sold_count = Column(Integer, default=0)

	user = relationship('User', back_populates='cart_items')
	product = relationship('Product', back_populates='cart_items')

	__table_args__ = {'extend_existing': True}


class Orders(Base):
	"""Создание таблицы заказы"""
	__tablename__ = 'orders'
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
	order_date = Column(DateTime, nullable=False)  # Дата и время заказа
	name = Column(String, nullable=False)
	description = Column(String)
	price = Column(Integer, nullable=False)
	photo = Column(String)
	delivery_address = Column(String, nullable=False)  # Адрес доставки
	phone_number = Column(String, nullable=False)  # Номер телефона для связи

	user = relationship('User', back_populates='orders')  # Не забудьте добавить в модель User
	product = relationship('Product', back_populates='orders')  # Не забудьте добавить в модель Product

	__table_args__ = {'extend_existing': True}


class DbShop:
	"""Создание класса для управление базой данных"""
	def __init__(self, dbname, user, password, host, port):
		self.engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')
		Base.metadata.create_all(self.engine)
		Session = sessionmaker(bind=self.engine)
		self.session = Session()

	def get_image_url(self, photo_path):
		"""Обработка фото"""
		if not os.path.isfile(photo_path):
			logger.error(f"Файл фото {photo_path} не найден.")
			return None

		return photo_path

	def add_product_bd(self, name: str, description: str, price: int, in_stock: str, photo):
		"""Добавление продуктов админом"""
		product = Product(
			name=name,
			description=description,
			price=price,
			in_stock=in_stock,
			photo=photo
		)
		self.session.add(product)
		self.session.commit()

	def remove_product_by_id(self, product_id: int):
		"""Удаление продукта по id"""
		logger.info(f"Запрос на удаление продукта с ID {product_id}")
		try:
			product = self.session.query(Product).get(product_id)
			if not product:
				logger.error(f"Продукт с ID {product_id} не найден.")
				return False

			self.session.delete(product)
			self.session.commit()

			logger.info(f"Продукт с ID {product_id} успешно удален.")
			return True
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при удалении продукта с ID {product_id}: {e}")
			return False

	def get_product_by_name(self, product_name: str):
		"""Выгрузка продуктов по имени"""
		try:
			product_infos = self.session.query(Product).filter_by(name=product_name).all()
			if not product_infos:
				logger.error(f"Продукт с именем {product_name} не найден.")
				return None

			products_with_photos = []
			for product_info in product_infos:
				if product_info.photo:
					product_info.photo_html = self.get_image_url(product_info.photo)
				else:
					logger.warning(f"У продукта {product_name} нет фото.")
					product_info.photo_html = None

				products_with_photos.append(product_info)

			return products_with_photos
		except SQLAlchemyError as e:
			logger.error(f"Ошибка при получении продуктов с именем {product_name}: {e}")
			return None

	def add_product_to_cart(self, user_id: int, product_id: int):
		"""Добавление продуктов в корзину"""
		logger.info(f"Пользователь {user_id} начинает добавление товара в корзину с ID {product_id}")
		try:
			existing_user = self.session.query(User).get(user_id)
			if not existing_user:
				new_user = User(id=user_id)
				self.session.add(new_user)
				self.session.commit()

			existing_product = self.session.query(Product).get(product_id)
			if not existing_product:
				return False

			existing_cart_item = self.session.query(CartItem).filter_by(user_id=user_id, product_id=product_id).first()
			if existing_cart_item:
				logger.info(f"Продукт с ID {product_id} уже есть в корзине пользователя {user_id}.")
				return False

			new_cart_item = CartItem(
				user_id=user_id,
				product_id=product_id,
				name=existing_product.name,
				description=existing_product.description,
				price=existing_product.price,
				in_stock=existing_product.in_stock,
				photo=existing_product.photo
			)

			self.session.add(new_cart_item)
			self.session.commit()
			return True

		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при добавлении продукта в корзину: {e}")
			return False

	def remove_product_from_cart(self, user_id: int, product_id: int):
		"""Удаление продуктов из корзины"""
		try:
			existing_user = self.session.query(User).get(user_id)
			if not existing_user:
				return False

			cart_item = self.session.query(CartItem).filter_by(user_id=user_id, product_id=product_id).first()
			if not cart_item:
				logger.info(f"Продукт с номером {product_id} не найден в корзине пользователя {user_id}.")
				return False

			self.session.delete(cart_item)
			self.session.commit()

			logger.info(f"Продукт с номером {product_id} успешно удален из корзины пользователя {user_id}.")
			return True

		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при удалении продукта из корзины: {e}")
			return False

	def get_cart_by_user(self, user_id: int):
		"""Выгрузка продуктов из корзины"""
		logger.info(f"Вызов get_cart_by_user с user_id: {user_id}")
		print(f"Пользователь : user_id = {user_id} выгружает данные из корзины")
		try:
			cart_products = self.session.query(CartItem).filter_by(user_id=user_id).all()

			if not cart_products:
				logger.info(f"Пользователь {user_id} не имеет продуктов в корзине.")
				return []

			products = []
			for cart_product in cart_products:
				product = {
					'id': cart_product.product_id,
					'name': cart_product.name,
					'description': cart_product.description,
					'price': cart_product.price,
					'in_stock': cart_product.in_stock,
					'photo': cart_product.photo,
					'sold_count': cart_product.sold_count
				}
				products.append(product)

			return products
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при получении избранных продуктов: {e}")
			return []

	def add_product_to_favorites(self, user_id: int, product_id: int):
		"""Добавление продуктов в избранное"""
		logger.info(f"Пользователь {user_id} начинает добавление товара в избранное с ID {product_id}")
		print(f"Перед добавлением в избранное: user_id = {user_id}, product_id = {product_id}")
		try:
			user = self.session.query(User).get(user_id)
			if not user:
				user = User(id=user_id)
				self.session.add(user)
				self.session.commit()

			product = self.session.query(Product).get(product_id)
			if not product:
				logger.error(f"Продукт с ID {product_id} не найден.")
				return False

			existing_favorite = self.session.query(Favorite).filter_by(user_id=user_id, product_id=product_id).first()
			if existing_favorite:
				logger.info(f"Продукт с ID {product_id} уже есть в избранном пользователя {user_id}.")
				return False

			product = self.session.query(Product).get(product_id)
			if not product:
				return False

			new_favorite = Favorite(
				user_id=user_id,
				product_id=product_id,
				name=product.name,
				description=product.description,
				price=product.price,
				in_stock=product.in_stock,
				photo=product.photo
			)
			self.session.add(new_favorite)
			self.session.commit()

			return True
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при добавлении продукта в избранное: {e}")
			return False

	def get_favorites(self, user_id: int):
		"""Выгрузка продуктов из избранного"""
		logger.info(f"Вызов get_favorites с user_id: {user_id}")
		print(f"Пользователь : user_id = {user_id} выгружает данные из избранного")
		try:
			favorites = self.session.query(Favorite).filter_by(user_id=user_id).all()
			if not favorites:
				logger.info(f"Пользователь {user_id} не имеет избранных продуктов.")
				return []

			products = []
			for favorite in favorites:
				product = {
					'id': favorite.product_id,
					'name': favorite.name,
					'description': favorite.description,
					'price': favorite.price,
					'in_stock': favorite.in_stock,
					'photo': favorite.photo,
					'sold_count': favorite.sold_count
				}
				products.append(product)

			logger.info(f"Пользователь {user_id} успешно получил свои избранные продукты.")
			return products
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при получении избранных продуктов пользователя {user_id}: {e}")
			return []

	def remove_favorite_by_id(self, user_id: int, product_id: int):
		"""Удаление продуктов из избранного"""
		try:
			favorite = self.session.query(Favorite).filter_by(user_id=user_id, product_id=product_id).first()

			if not favorite:
				logger.info(f"Товар с ID {product_id} не найден в избранном пользователя {user_id}.")
				return False

			self.session.delete(favorite)
			self.session.commit()

			logger.info(f"Товар с ID {product_id} успешно удален из избранного пользователя {user_id}.")
			return True

		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при удалении товара из избранного: {e}")
			return False

	def get_top_selling_products(self, limit=10):
		"""Выгрузка первых 10 лидеров продаж"""
		logger.info(f"Запрос первых {limit} лидеров продаж")
		try:
			top_selling_products = self.session.query(Product).order_by(Product.sold_count.desc()).limit(limit).all()
			if not top_selling_products:
				logger.info("Нет проданных продуктов.")
				return []

			products = []
			for product in top_selling_products:
				product_info = {
					'id': product.id,
					'name': product.name,
					'description': product.description,
					'price': product.price,
					'in_stock': product.in_stock,
					'photo': product.photo,
					'sold_count': product.sold_count
				}
				products.append(product_info)

			logger.info(f"Успешно получены популярные продукты: {len(products)}.")
			return products

		except SQLAlchemyError as e:
			logger.error(f"Ошибка при получении лидеров продаж: {e}")
			return []

	def get_product_by_id(self, user_id: int, product_id: int):
		"""Поиск товара по id"""
		try:
			user = self.session.query(User).get(user_id)
			if not user:
				user = User(id=user_id)
				self.session.add(user)
				self.session.commit()

			product = self.session.query(Product).get(product_id)
			return product
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при добавлении продукта в заказ: {e}")
			return False

	def save_order(self, user_id: int, product_id: int, datetime: int, delivery_address: str, phone_number: int):
		"""Купленные товары"""
		logger.info(f"Пользователь {user_id} начинает покупку товара в заказ с ID {product_id}")
		try:
			user = self.session.query(User).get(user_id)
			logger.info(f"отработала 756 строка файла базы")
			if not user:
				user = User(id=user_id)
				self.session.add(user)
				self.session.commit()

			product = self.session.query(Product).get(product_id)
			logger.info(f"отработала 763 строка файла базы найден продукт в базе")
			if not product:
				logger.error(f"Продукт с ID {product_id} не найден.")
				return False

			logger.info(f"начинаем добавление товара в таблицу покупки")
			new_order = Orders(
				user_id=user_id,
				product_id=product_id,
				order_date=datetime,
				name=product.name,
				description=product.description,
				price=product.price,
				photo=product.photo,
				delivery_address=delivery_address,
				phone_number=phone_number
			)
			self.session.add(new_order)
			logger.info(f"отработала 781 строка файла базы товар добавлен в купленые")
			self.session.commit()

			return id
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при добавлении продукта в заказ: {e}")
			return False

	def increment_sold_count(self, product_id: int):
		"""Увеличение количества проданных товаров"""
		logger.info(f"Увеличение количества проданных товаров для продукта с ID {product_id}")
		try:
			product = self.session.query(Product).get(product_id)
			if not product:
				logger.error(f"Продукт с ID {product_id} не найден.")
				return False

			product.sold_count += 1
			self.session.commit()

			logger.info(f"Количество проданных товаров для продукта с ID {product_id} успешно увеличено.")
			return True
		except SQLAlchemyError as e:
			self.session.rollback()
			logger.error(f"Ошибка при увеличении sold_count продукта с ID {product_id}: {e}")
			return False

