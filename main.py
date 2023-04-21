import flask
from utils import Generator, getGenerator
import json
import time

app = flask.Flask(__name__)

gen = Generator(time.time())

generators = []

@app.route('/topic', methods=['GET'])
def setTopic():
	timestamp = flask.request.args.get('time')
	gen = Generator(timestamp)
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
	return flask.render_template("index.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port="8080")