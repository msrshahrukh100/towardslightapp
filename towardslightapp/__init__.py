from flask import Flask
from flask.ext.socketio import SocketIO




app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'


# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345'
app.config['MYSQL_DATABASE_DB'] = 'towardslightdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


app.config['UPLOAD_FOLDER'] = '/home/mohammad/towardslight/app/towardslightapp/static/Uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])



app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='msr.concordfly@gmail.com',
    MAIL_PASSWORD='lwkffkxtzebqdltl'
    )


from routes import mail
from routes import mysql 
from routes import socketio 

mysql.init_app(app)
socketio.init_app(app)


import towardslightapp.routes


