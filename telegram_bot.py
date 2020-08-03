from telegram import Bot

class TelegramBot:

	def __init__(self, token, chat_id):
		self.chat_id = chat_id
		self.bot = Bot(token=token)

	def sendMessage(self, msg):
		self.bot.sendMessage(chat_id=self.chat_id, text=msg)
