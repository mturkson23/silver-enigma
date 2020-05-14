# -*- encoding: utf-8 -*-

import datetime
from app         import db, bc
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import random

# `Base` = declarative_base()
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer,     primary_key=True)
    username = db.Column(db.String(64),  unique = True)
    fullname = db.Column(db.String(200), unique = True)
    email    = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(80))
    phoneno = db.Column(db.String(20), server_default = '')
    address = db.Column(db.String(80), server_default = '')
    staffno  = db.Column(db.String(20), unique = True)
    photo    = db.Column(db.String(20), server_default = 'sample.png')
    role_id  = db.Column(db.Integer, ForeignKey('role.id'))

    request = relationship("Request", back_populates = "user")
    role = relationship("Role", back_populates="user")

    def __init__(self, fullname, username, email, password, phoneno = None, address = None, staff_no = '', role_id = 1, photourl = None):
        self.fullname       = fullname
        self.username       = username
        self.password       = bc.generate_password_hash(password).decode('utf-8')
        self.email          = email
        self.phoneno        = phoneno
        self.address        = address
        self.role_id        = role_id
        self.staffno        = str(random.randint(100000,999999)) if staff_no == '' else staff_no
        self.photo          = photourl if photourl is not None else 'sample.png'

    def __repr__(self):
        return '<User %r - %s>' % (self.id) % (self.email)

    def __str__(self):
        return f'User {self.username}, id={self.id}, staffno={self.staffno}'

    def save(self):
        # inject self into db session
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self

class Role(db.Model):
    __tablename__ = 'role'
    __table_args__ = {'extend_existing': True}
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100))
    description  = db.Column(db.String(225))

    user = relationship("User", back_populates="role")

    def __init__(self, name, description):
        self.name        = name
        self.description = description

    def __repr__(self):
        return '%s' % (self.name)

    def save(self):
        # inject self into db session
        db.session.add (self)
        # commit change and save the object
        db.session.commit()
        return self

class Product(db.Model):
    __table_args__ = {'extend_existing': True}
    id              = db.Column(db.Integer,    primary_key=True)
    name            = db.Column(db.String(200))
    imageurl        = db.Column(db.String(24), server_default = 'sample.png')
    description     = db.Column(db.Text, nullable=True)
    producttype_id  = db.Column(db.Integer, ForeignKey('producttype.id'))

    stock = relationship("Stock", back_populates="product")
    # request = relationship("Request", back_populates="product")
    producttype = relationship("Producttype", back_populates="product")

    db.UniqueConstraint('name', 'producttype_id', name='unique_name_producttype_id')

    def __init__(self, name, description, producttype_id):
        self.name = name
        self.description  = description
        self.producttype_id  = producttype_id

    def __repr__(self):
        return '%s (%s)' % (self.name, self.producttype)

    def save(self):
        # inject self into db session
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self

class Stock(db.Model):
    __table_args__ = {'extend_existing': True} 
    id         = db.Column(db.Integer, primary_key=True)
    cost_price  = db.Column(db.Float)
    sell_price  = db.Column(db.Float)
    quantity   = db.Column(db.Integer)
    product_id  = db.Column(db.Integer, ForeignKey('product.id'))

    product = relationship("Product", back_populates="stock")
    request = relationship("Request", back_populates="stock")

    def __init__(self, cost_price, sell_price, quantity, product_id):
        self.cost_price = cost_price
        self.sell_price = sell_price
        self.quantity  = quantity
        self.product_id  = product_id

    def __repr__(self):
        return '%s (GHS %s)' % (self.product, self.sell_price)

    def save(self):
        # inject self into db session
        db.session.add ( self )
        # commit change and save the object
        db.session.commit()
        return self

class Requesttype(db.Model):
    __table_args__ = {'extend_existing': True}
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100))
    description  = db.Column(db.String(225))

    request = relationship("Request", back_populates="requesttype")

    def __init__(self, name, description):
        self.name        = name
        self.description = description

    def __repr__(self):
        return '<Requesttype %r - %r>' % (self.id) % (self.name)

    def save(self):
        # inject self into db session
        db.session.add (self)
        # commit change and save the object
        db.session.commit()
        return self

class Producttype(db.Model):
    __tablename__ = 'producttype'
    __table_args__ = {'extend_existing': True}
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100))
    description  = db.Column(db.String(225))

    product = relationship("Product", back_populates="producttype")

    def __init__(self, name, description):
        self.name        = name
        self.description = description

    def __repr__(self):
        return '%s' % (self.name)

    def save(self):
        # inject self into db session
        db.session.add (self)
        # commit change and save the object
        db.session.commit()
        return self

class Requeststate(db.Model):
    __table_args__ = {'extend_existing': True}
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100))
    code         = db.Column(db.String(25))
    description  = db.Column(db.String(225))

    request = relationship("Request", back_populates="requeststate")

    def __init__(self, name, description):
        self.name = name
        self.description  = description

    def __repr__(self):
        return '%s' % (self.name)

    def save(self):
        # inject self into db session
        db.session.add (self)
        # commit change and save the object
        db.session.commit()
        return self        

class Request(db.Model):
    __tablename__ = 'request'
    __table_args__ = {'extend_existing': True}

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, ForeignKey('user.id'))
    stock_id        = db.Column(db.Integer, ForeignKey('stock.id'))
    requesttype_id  = db.Column(db.Integer, ForeignKey('requesttype.id'))
    quantity        = db.Column(db.Integer)
    state_id        = db.Column(db.Integer, ForeignKey('requeststate.id'))
    stamp           = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_created    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="request")
    # product = relationship("Product", back_populates="request")
    stock = relationship("Stock", back_populates="request")
    requesttype = relationship("Requesttype", back_populates="request")
    requeststate = relationship("Requeststate", back_populates="request")

    def __init__(self, user_id, stock_id, requesttype_id, quantity, state_id):
        self.user_id = user_id
        self.stock_id  = stock_id
        self.requesttype_id  = requesttype_id
        self.quantity = quantity
        self.state_id = state_id

    def __repr__(self):
        return '%s' % (self.stock_id)

    def save(self):
        # inject self into db session
        db.session.add (self)
        # commit change and save the object
        db.session.commit()
        return self