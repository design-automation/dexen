# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

import os

from flask import Flask
from flask.ext.login import LoginManager
from werkzeug.wsgi import SharedDataMiddleware


TEMPLATE_PATH = os.path.join("app", "views")
STATIC_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__name__)), "app")

app = Flask(__name__, template_folder=TEMPLATE_PATH,
            static_folder=STATIC_FOLDER_PATH,
            static_url_path="")


app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    "/": os.path.join(os.path.dirname(__file__), "app")
})


app.config['UPLOAD_FOLDER'] = os.getcwd() #tempfile.gettempdir()
app.secret_key = "3&\xfe%\x08\x14\xf1\xcf\xba\xdci\xeb\x08\x10\xac\x1af\xb1\xd7\x07(j\xfb\x17"

login_mgr = LoginManager(app)
login_mgr.init_app(app)


print "app root path", app.root_path

