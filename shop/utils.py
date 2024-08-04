import logging
import os
import uuid
import telebot
from bot import Shopbot
from config import token, payments_token

shop = Shopbot(token=token)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
product_info = {}


def invoice_process(message):
	try:
		product_id = int(message.text)
		product = shop.base.get_product_by_id(message.from_user.id, product_id)
		shop.bot.send_invoice(
			message.chat.id,
			title=product.name,
			description=product.description,
			provider_token=payments_token,
			currency='RUB',
			photo_url=product.photo if product.photo else None,
			photo_width=512,
			photo_height=512,
			need_phone_number=True,
			need_shipping_address=True,
			is_flexible=False,
			prices=[telebot.types.LabeledPrice(label=product.name, amount=product.price * 100)],
			invoice_payload=str(uuid.uuid4())
		)
		shop.base.increment_sold_count(product_id=int(message.text))
	except ValueError:
		shop.bot.send_message(message.chat.id, "Ошибка: ID продукта должен быть целым положительным числом.")
		shop.bot.register_next_step_handler(message, invoice_process)


def process_product_id_backet(message):
	try:
		product_id = int(message.text)
		if product_id <= 0:
			raise ValueError("ID продукта должен быть положительным числом.")
		shop.remove_from_backet(message, product_id)
	except ValueError as e:
		shop.bot.send_message(message.chat.id, f"Ошибка: {e}. Пожалуйста, отправьте целое положительное число.")
		shop.bot.register_next_step_handler_by_chat_id(message.chat.id, process_product_id_backet)


def process_add_product_id_backet(message):
	try:
		product_id = int(message.text)
		if product_id <= 0:
			raise ValueError("ID продукта должен быть положительным числом.")
		logger.info(f"Получен ID продукта: {product_id}")
		shop.add_to_backet(message, product_id)
	except ValueError as e:
		logger.error(f"Ошибка при получении ID продукта: {e}")
		shop.bot.send_message(message.chat.id, f"Ошибка: {e}. Пожалуйста, отправьте целое положительное число.")
		shop.bot.register_next_step_handler_by_chat_id(message.chat.id, process_add_product_id_backet)


def save_photo(message, name, description, price, in_stock):
	if message.content_type == 'photo':
		folder = name
		photo_file_id = message.photo[-1].file_id
		file_name = f"{photo_file_id}.jpg"
		file_path = os.path.join(folder, file_name)

		if not os.path.exists(folder):
			os.makedirs(folder)

		file_info = shop.bot.get_file(photo_file_id)
		downloaded_file = shop.bot.download_file(file_info.file_path)
		with open(file_path, 'wb') as f:
			f.write(downloaded_file)

		shop.add_product(name, description, price, in_stock, file_path)
		logger.info(f"товар {name} от {message.from_user.id} добавлен в базу с фото")
		shop.bot.send_photo(chat_id=message.from_user.id, photo=open(file_path, 'rb'),
							caption=f"Товар '{name}' добавлен")
	else:
		shop.bot.send_message(message.from_user.id, "Отправь фото товара")


def process_product_info(message):
	logger.info(f"Получена информация о товаре от {message.from_user.id}")
	product_info[message.from_user.id] = {'text': message.text}
	try:
		name, description, price, in_stock = message.text.split(";")
		logger.info(f"Информация о товаре разобрана: {name}, {description}, {price}, {in_stock}")
		msg_photo = shop.bot.send_message(message.from_user.id, "Теперь нужно фото товара")
		shop.bot.register_next_step_handler(msg_photo, save_photo, name, description, price, in_stock)
		logger.info("Обработчик следующего шага зарегистрирован для получения фото товара.")
	except ValueError as e:
		logger.error(f"Ошибка при разборе информации о товаре: {e}")
		shop.bot.send_message(message.from_user.id,
							"Отправь данные строго в формате имя, описание, цена, в наличии или нет через запятую")
	except Exception as e:
		logger.error(f"Ошибка при добавлении в базу: {e}")
		shop.bot.send_message(message.from_user.id, "Ошибка при добавлении в базу")


def process_add_product_id(message):
	try:
		product_id = int(message.text)
		if product_id <= 0:
			raise ValueError("ID продукта должен быть положительным числом.")
		logger.info(f"Получен ID продукта: {product_id}")
		shop.add_to_favorites(message, product_id)
	except ValueError as e:
		logger.error(f"Ошибка при получении ID продукта: {e}")
		shop.bot.send_message(message.chat.id, f"Ошибка: {e}. Пожалуйста, отправьте целое положительное число.")
		shop.bot.register_next_step_handler_by_chat_id(message.chat.id, process_add_product_id)


def process_product_id(message):
	try:
		product_id = int(message.text)
		if product_id <= 0:
			raise ValueError("ID продукта должен быть положительным числом.")
		shop.remove_from_favorites(message, product_id)
	except ValueError as e:
		shop.bot.send_message(message.chat.id, f"Ошибка: {e}. Пожалуйста, отправьте целое положительное число.")
		shop.bot.register_next_step_handler_by_chat_id(message.chat.id, process_product_id)


