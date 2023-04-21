import time
import logging
import openai
import os

# use like this: 

# g = Generator()

# g.promptTopic(input("Please enter a topic: "))

# g.generateResponse(input(">"))

logging.basicConfig(filename=f'logs/{time.strftime("%Y%m%d")}', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger()

class PromptAlreadyPrompted(Exception):
	pass

class Generator:
	def __init__(self, timestamp):
		self.timestamp = timestamp
		self._APIKey = os.environ['OPENAI_API_KEY']
		openai.api_key = self._APIKey
		self.messages = []
		self._prompt = False

	def addMessage(self, role, query):
		message = {"role":role, "content":query}
		logger.debug(message)
		self.messages.append(message)

	def promptTopic(self, prompt):
		if self._prompt:
			raise PromptAlreadyPrompted("Prompt already asked!")
		self._prompt = True
		self.addMessage("system", f"Behavior like a trivia quiz expert generator. Given the topic {prompt}, you will give me a trivia question based on that subject. Your style is comedic but you only give factually correct questions and answers. Start by giving me easy questions and make the next question harder, make the difficulty exponentially harder. never tell me the answer in the question block. Encourage me and act as a cheerleader. Wait for me to write the answer before giving me the next one. Only provide one question at a time. Have only questions with one word answer")
		return self.generateResponse()
	
	def generateResponse(self, message=''):
		if message:
			self.addMessage("system", message)
		res = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			messages=self.messages
		)
		res = res['choices'][0]['message']['content'].strip()
		self.addMessage("assistant", res)
		print(res)
		return res

def getGenerator(list, time):
	for elem in list:
		if elem.timestamp == time:
			return elem
	raise Exception