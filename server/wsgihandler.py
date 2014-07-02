import socket
import sys
import site

from meeple import app
from werkzeug.debug import DebuggedApplication


application = app

application.config['DEBUG'] = True
application = DebuggedApplication(application, evalex=True, show_hidden_frames=False)
application.debug = True

