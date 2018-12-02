## AskUs Chat Application
The AskUs Chat application is an integratable chat application for library branches.  The application is light, responsive and data driven.

This project was created by Ben Ruedinger and Juliana Lisser to complete the requirements for the MSIST program at the University of Wisconsin-Milwaukee.

A live version of this application is availabe at [AskUs](shrouded-fortress-25014.herokuapp.com).

## Motivation
Many libraries are limited on the technology that they are able to integrate into their branch specific websites.  AskUs is focused on creating a light and extensible chat application which can easily be integrated into a pre-exiting webpage.
AskUs is also focused on brining insight to libraries in regards to what information patrons are searching for.  This is done through logging of all chat records and the presentation of application insights through an admin portal.

## Code style
This application was written as a Flask web application in Python version 2.7.

## Screenshots
The landing page for the chat application was designed to be branch agnostic.  The look and feel of the application can be quickly adjusted in the custom.css file.
![chatapp](https://user-images.githubusercontent.com/36139233/49335637-cc957500-f5b6-11e8-9101-e619dbad580d.PNG)

The admin panel allows for KPIs to be presented to library staff allowing for insights from patron chats to be impactful and actionable.
![admin](https://user-images.githubusercontent.com/36139233/49335653-26963a80-f5b7-11e8-8e9e-6d1ea10d5e31.PNG)

## Tech/framework used
This application was built to be deployed on Heroku. It utilizes Redis cache and a PostgreSQL database.  

This application was written in Python 2.7.

<b>Python Packages Used</b>
- Flask 0.10.1
- Flask Sockets 0.2.0
- Gevent 1.0.2
- Gevent Websockets 0.9.5
- Greenlet 0.4.9
- Gunicorn 19.4.5
- Itsdangerous 0.24
- Jinja2 2.8
- MarkupSafe 0.23
- Redis 2.10.5
- Werkzeug 0.11.3
- Psycopg2 2.7.3.2
- Flask Sqlalcehmy 2.3.2
- Flask Heroku 0.1.8
- SQLAlchemy 1.2.14

## Features
The following are features of this application:
- The application is developed using the Flask framework
- This application is a Web 2.0 application since it is both responsive and data driven
- User data is protected through a session based security layer which can be configured to work with pre-existing institutional data
- Chat messages are logged and analyzed to created actionable metrics
- The application has a consistent look and feel through out the interface
- An admin panel is available with up to the second actionable data
- The user interface was deisgned for ease of use for all library patrons
- The application is available 24/7
- Due to the use of Redis the chat applicaiton allows for real time communication
- This system is fully documented

## Installation
Installing this application on another instance of Heroku is fairly simple. The following steps will walk a new user through this deployment.
- Install Git and Heroku CLI
- Clone this repo
- Create a Heroku app
```
$ heroku create
```
- Deploy a redis cache
```
$ heroku addons:create heroku-redis:hobby-dev
```
- Deploy a PostgreSQL resource
```
$ heroku addons:create heroku-postgresql:hobby-dev
```
- Update code locally and push to the production application
```
$ git push heroku master
````

## Tests
This application was tested through out development based on 5 use cases:
- Patron asks a question
- Librarian logs in
- Librarian checks chat reporting
- Librarian uses the drop down menu
- Security paths

## Credits
This application was created by Ben Ruedinger and Juliana Lisser.  The concept of this application was created by Ben through his current work at the university library where he saw a real need for a simple extensible application that libraries could leverage.

Project management and interface design was handled by Ben.
Systems architecture, deployment and version control was handeled by Juliana.

