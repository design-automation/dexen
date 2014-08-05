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


from flask.ext.wtf.form import Form
from wtforms.fields import TextField, PasswordField
from wtforms import validators


class LoginForm(Form):
    """ Class the represents a Flask form for existing users to login.
    Subclasses flask.ext.wtf.form.Form.
    """
    username = TextField(validators=[validators.required()])
    password = PasswordField(validators=[validators.required()])

    def __init__(self, user_mgr, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user_mgr = user_mgr

    def validate(self):
        # rv = super(LoginForm, self).validate()
        user = self.get_user()
        if user is None:
            return False
            raise validators.ValidationError('Invalid user')
        
        if user.password != self.password.data:
            return False
            raise validators.ValidationError('Invalid password')
        
        return True

    def get_user(self):
        return self.user_mgr.get_user(username=self.username.data)


class RegistrationForm(Form):
    """ Class the represents a Flask form for new users to register.
    Subclasses flask.ext.wtf.form.Form.
    """
    username = TextField(validators=[validators.required()])
    password = PasswordField(validators=[validators.required()])

    def __init__(self, user_mgr, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.user_mgr = user_mgr

    def validate(self):
        # rv = super(RegistrationForm, self).validate()
        if self.user_mgr.exists(self.username.data):
            return False
            raise validators.ValidationError('Duplicate username')
        return True
