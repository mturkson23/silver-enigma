# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, SelectField, SubmitField, PasswordField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	username    = StringField  (u'Username'        , validators=[DataRequired()])
	password    = PasswordField(u'Password'        , validators=[DataRequired()])

class RegisterForm(FlaskForm):
	fullname    = StringField  (u'Full Name'  , validators=[DataRequired()])
	username    = StringField  (u'Username'  , validators=[DataRequired()])
	password    = PasswordField(u'Password'  , validators=[DataRequired()])
	email       = StringField  (u'Email'     , validators=[DataRequired(), Email()])

class ProductForm(FlaskForm):
	name    		= StringField  (u'Name'  , validators=[DataRequired()])
	product_type    = SelectField(u'Product Type', coerce=int)
	description     = StringField  (u'Description', validators=[DataRequired()])	
	imageurl 		= FileField (u'Product Icon')	

class StockForm(FlaskForm):
	cost_price    		= DecimalField  (u'Cost Price'  , validators=[DataRequired()])
	sell_price    		= DecimalField  (u'Selling Price'  , validators=[DataRequired()])
	quantity    		= IntegerField  (u'Quantity'  , validators=[DataRequired()])
	product   			= SelectField(u'Product', coerce=int)

class RequestForm(FlaskForm):
	quantity    		= IntegerField  (u'Quantity'  , validators=[DataRequired()])
	stock_item   		= SelectField(u'Request Item', coerce=int)