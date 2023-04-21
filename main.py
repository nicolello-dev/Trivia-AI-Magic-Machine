import flask
from utils import Generator
import json

app = flask.Flask(__name__)

gen = Generator()

@app.route('/reset')
def reset():
	global gen 
	gen = Generator()
	return "<h1>Reset!</h1>"

@app.route('/topic', methods=['GET'])
def setTopic():
	reset()
	topic = flask.request.args.get('topic')
	if topic: return json.dumps({"response": gen.promptTopic(topic)})
	return f"{topic} not a topic"

@app.route('/question', methods=['GET'])
def getQuestion():
	answer = flask.request.args.get('q')
	if answer: return json.dumps({"response": gen.generateResponse(answer)})
	return f"{answer} not an answer"

@app.route('/')
def home():
	return flask.render_template("index.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port="8080")