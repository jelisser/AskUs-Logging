# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import redis
import gevent
import datetime
from flask import Flask, render_template,request
from flask_sockets import Sockets
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'chat'

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)
app.debug = 'DEBUG' in os.environ


sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)

#logging update
logger = logging.getLogger('chat_log')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

#Create Database Model
class LogMessage(db.Model):
    __tablename__="logmessage"
    id = db.Column(db.Integer, primary_key=True)
    messagetext = db.Column(db.String(500), unique=True)
    submitdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, messagetext):
        self.messagetext=messagetext
        #self.submitdate=submitdate

    def __rep__(self):
        return '<Message Tex t%r>' %self.messagetext

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

chats = ChatBackend()
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while not ws.closed:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        #if message:
        #app.logger.info(u'Inserting message: {}'.format(message))
        logger.info(message)
        redis.publish(REDIS_CHAN, message)

        if message is not None:
            reg = LogMessage(message)
            db.session.add(reg)
            db.session.commit()

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep(0.1)

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/login/')
def login():
    return render_template('login.html')

