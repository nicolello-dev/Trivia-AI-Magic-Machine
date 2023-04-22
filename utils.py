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
		message = f"""For each message I give, generate questions based on the topic {prompt}, and give out four possible answers, one of which must be right and the other three must be wrong.
Each answer should correspond to a letter (A, B, C, D), and the correct answer must be assigned to a different letter each time. Absolutely do not give me the right answer.
Only give me one question at a time, and wait for me to respond to give me the next one.
Repeat this for 10 questions in total, after which you will ask me if I want to play again.
Increase the difficulty of the questions as I respond correctly."""
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