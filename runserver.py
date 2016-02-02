from towardslightapp import app

from flask.ext.socketio import SocketIO
from towardslightapp import socketio

socketio.run(app,debug=True)
