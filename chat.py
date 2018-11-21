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
from flask import Flask, render_template,request,flash,session,redirect,abort,url_for
from flask_sockets import Sockets
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
from sqlalchemy import extract


REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'chat'

app = Flask(__name__, static_url_path='/static')
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

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



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
    username=session['username']
    return render_template('index.html',username=username)

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
    username = session['username']

    filtertoken = '%'+username+'%'
    #Gather all chat records for a given user
    totalrecords = len(LogMessage.query.all())
    records = LogMessage.query.filter(LogMessage.messagetext.like(filtertoken)).all()
    totaluserrecords = len(records)
    percentcontrib = ((totaluserrecords*1.0)/totalrecords)*100

    #Chat Topics
    #Media - (books, magazines, movies, articles, music, library)
    book = LogMessage.query.filter(LogMessage.messagetext.like('%book%')).all()
    magazine = LogMessage.query.filter(LogMessage.messagetext.like('%magazine%')).all()
    movie = LogMessage.query.filter(LogMessage.messagetext.like('%movie%')).all()
    article = LogMessage.query.filter(LogMessage.messagetext.like('%article%')).all()
    music = LogMessage.query.filter(LogMessage.messagetext.like('%music%')).all()
    library = LogMessage.query.filter(LogMessage.messagetext.like('%library%')).all()
    bookcount = len(book)
    magazinecount = len(magazine)
    moviecount = len(movie)
    articlecount = len(article)
    musiccount = len(music)
    librarycount = len(library)
    #Topics - (fantasy, romance, science fiction, technology, history, math)
    fantasy = LogMessage.query.filter(LogMessage.messagetext.like('%fantasy%')).all()
    romance = LogMessage.query.filter(LogMessage.messagetext.like('%romance%')).all()
    sfiction = LogMessage.query.filter(LogMessage.messagetext.like('%science fiction%')).all()
    technology = LogMessage.query.filter(LogMessage.messagetext.like('%tech%')).all()
    history=LogMessage.query.filter(LogMessage.messagetext.like('%history%')).all()
    math = LogMessage.query.filter(LogMessage.messagetext.like('%math%')).all()
    fantasycount = len(fantasy)
    romancecount = len(romance)
    sfictioncount = len(sfiction)
    technologycount = len(technology)
    historycount = len(history)
    mathcount = len(math)

    #Times and Message Frequency
    hours=[]
    hourslabels =[]
    for i in range(25):
        hours.append(len(LogMessage.query.filter(extract('hour',LogMessage.submitdate)==i).all()))
    for i in range(25):
        hourslabels.append(i)
    
    maxhour = max(hours)
    minhour = min(hours)
    averagehour = sum(hours)/(len(hours)*1.0)
    maxhourlabel = hours.index(maxhour)
    minhourlabel = hours.index(minhour)
    
    return render_template('admin.html', username=username,
    filtertoken = filtertoken,
    totalrecords = totalrecords,
    records = records,
    totaluserrecords = totaluserrecords,
    percentcontrib = percentcontrib,
    bookcount = bookcount,
    magazinecount = magazinecount,
    moviecount = moviecount,
    articlecount = articlecount,
    musiccount = musiccount,
    librarycount = librarycount,
    fantasycount = fantasycount,
    romancecount = romancecount,
    sfictioncount = sfictioncount,
    technologycount = technologycount,
    historycount = historycount,
    mathcount = mathcount,
    maxhour = maxhour,
    minhour = minhour,
    averagehour = averagehour,
    maxhourlabel = maxhourlabel,
    minhourlabel = minhourlabel
    )

@app.route('/login/',methods=['GET','POST'])
def login():
    error = None
    username = session['username']

    if username != 'default':
        return redirect(url_for('loggedin'))

    if request.method == 'POST':
        if request.form['username'] != 'admin' and request.form['password'] != 'secret':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = 'admin'
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)

@app.route('/logout/')
def logout():
    session['username']='default'
    return render_template('logout.html')

@app.route('/loggedin/')
def loggedin():
    username=session['username']
    return render_template('loggedin.html',username=username)