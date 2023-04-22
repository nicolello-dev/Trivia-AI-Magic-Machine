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
		self.addMessage("system", f"Act like a trivia game master designer and generator.Your style is comedic but you only give factually correct questions and answers. Based around {prompt}, for each round, come up with 1 question with 4 answers (A, B, C, D) that I can choose from. There is only one correct answer, and I must guess it. Wait for my response before asking the next question. I'll get 10 points for each correct answer I guess. I will receive 0 points for each incorrect answer. Increase the difficulty of each correct answer. Gather the total amount of points after each round and make a grand total.  I’ll have 10 rounds to reach 100 points. If I don’t reach 100 points in 10 rounds I’ll lose and ask if I want to start a new game. You will start by asking me only the first question, then wait for me to answer back, then you will proceed with the next question, and so on. At the end of the last question ask if I would like to play again. Let’s start.")
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