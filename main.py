import flask
from flask import request
from utils import Generator, getGenerator, logLoc
import json
import os
import requests

app = flask.Flask(__name__)

ip2loc = os.environ['IP2LOC']

generators = []

def getCountry():
	headers_list = request.headers.getlist("X-Forwarded-For")
	user_ip = headers_list[0] if headers_list else request.remote_addr
	r = requests.get(f'https://api.ip2location.io/?key={ip2loc}&ip={user_ip}')
	j = json.loads(r.text)
	return j['country_name']

@app.route('/topic', methods=['GET'])
def setTopic():
	timestamp = flask.request.args.get('time')
	gen = Generator(timestamp)
	gen.country = getCountry()
	generators.append(gen)
	
	topic = flask.request.args.get('topic')
	
	if topic:
		return json.dumps({"response": gen.promptTopic(topic)})
		
	return f"{topic} not a topic"

@app.route('/question', methods=['GET'])
def getQuestion():
	answer = flask.request.args.get('q')
	timestamp = flask.request.args.get('time')
	gen = getGenerator(generators, timestamp)
	if answer: return json.dumps({"response": gen.generateResponse(answer)})
	return f"{answer} not an answer"

@app.route('/')
def home():
	logLoc(getCountry())
	return flask.render_template("index.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port="8080")