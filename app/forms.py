# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	username    = StringField  (u'Username'        , validators=[DataRequired()])
	password    = PasswordField(u'Password'        , validators=[DataRequired()])

class RegisterForm(FlaskForm):
	username    = StringField  (u'Username'  , validators=[DataRequired()])
	password    = PasswordField(u'Password'  , validators=[DataRequired()])
	email       = StringField  (u'Email'     , validators=[DataRequired(), Email()])

class ProductForm(FlaskForm):
	name    		= StringField  (u'Name'  , validators=[DataRequired()])
	product_type   = SelectField(u'Product Type', coerce=int, choices = [(1, 'Airtime'), (2, 'E-Cash')], validators=[DataRequired()])
	description     = StringField  (u'Description', validators=[DataRequired()])	
	imageurl 		= FileField (u'Product Icon')	
