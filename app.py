# from test_folder.test_file import testfunction
import eventlet
import json
import pprint
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap

eventlet.monkey_patch()

app = Flask(__name__)
# app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '10.0.1.189'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'username'
app.config['MQTT_PASSWORD'] = 'password'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('#')

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    print("on publish")
    pprint.pprint(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    print("on subscribe")
    print(data['payload'])
    mqtt.subscribe(data['topic'])


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
	# print(dir(message))
	print("on message")
	print(message.payload)
	data = dict(
		topic=message.topic,
		payload=message.payload.decode()
	)
	socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
