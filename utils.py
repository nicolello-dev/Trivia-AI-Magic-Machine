import time
import logging
import openai
import os
import json

# use like this: 

# g = Generator()

# g.promptTopic(input("Please enter a topic: "))

# g.generateResponse(input(">"))

logging.basicConfig(filename=f'logs/{time.strftime("%Y%m%d")}', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger()

class PromptAlreadyPrompted(Exception):
	pass

class GeneratorDoesntExist(Exception):
	pass

class Generator:
	def __init__(self, timestamp):
		self.timestamp = timestamp
		self._APIKey = os.environ['OPENAI_API_KEY']
		openai.api_key = self._APIKey
		self.messages = []
		self._prompt = False
		self.country = ''
		logger.debug(f"Generator created with timestamp {timestamp}")

	@property
	def dict(self):
		return {
			"timestamp": self.timestamp,
			"_prompt": self._prompt,
			"country": self.country,
			"messages": self.messages
		}

	def addMessage(self, role, query):
		message = {"role":role, "content":query}
		logger.debug(f"Message added, message:{message}")
		self.messages.append(message)

	def promptTopic(self, prompt):
		if self._prompt:
			logger.error(f"Prompt already asked! generator timestamp {self.timestamp}")
			raise PromptAlreadyPrompted("Prompt already asked!")
		self._prompt = True
		message = f"""You are a trivia game master designer and generator with a comedic style. Your task is to generate factually correct questions and answers, incorporating emojicons in each. Be funny and conversational. When given a topic, generate a single question based on the topic {prompt} with four possible answers (A, B, C, D), ensuring the correct answer is assigned to a different letter each time. Do not reveal the correct answer. Wait for a response before generating the next question. Provide a total of 10 questions, then ask if the user wants to play again. Each question is worth 10 points, and answering incorrectly results in a loss of 10 points.Remind me of my current score after every question. Gradually increase the difficulty of each question as the user answers correctly. If the user answers correctly, respond with "Correct! 🎉" and if incorrect, respond with "Wrong! 💩"."""
		self.addMessage("system", message)
		with open(f"logs/conversations/{self.timestamp}.json", 'w') as f:
			json.dump(self.dict, f, indent=4)
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
		with open(f"logs/conversations/{self.timestamp}.json", 'w') as f:
			json.dump(self.dict, f, indent=4)
		return res

def getGenerator(list, time):
	for elem in list:
		if elem.timestamp == time:
			return elem
	raise GeneratorDoesntExist(f"The generator doesn't exist! timestamp given:{time}")

def logLoc(loc):
	logger.info(f"Request from {loc}")