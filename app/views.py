# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging 

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

# App modules
from app        import app, lm, db, bc
from app.models import User, Product
from app.forms  import LoginForm, RegisterForm, ProductForm

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None

    if request.method == 'GET': 

        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/register.html', form=form, msg=msg ) )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(username=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = password #bc.generate_password_hash(password)

            user = User(username, email, pw_hash)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     

    else:
        msg = 'Input error'     

    return render_template('layouts/auth-default.html',
                            content=render_template( 'pages/register.html', form=form, msg=msg ) )


@app.route('/api/stats/<action>', methods=['GET'])
def stats(action):
    return {"revenue": "120,000", "users": 11, "sales": "20,000", "profit":"5,000"}

# Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(username=username).first()

        if user:
            
            #if bc.check_password_hash(user.password, password):
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Invalid Credentials"

    return render_template('layouts/auth-default.html',
                            content=render_template( 'pages/login.html', form=form, msg=msg ))

# List all products
@app.route('/products')
def fetch_products():
    # declare the product form
    form = ProductForm(request.form)

    # fetch all products from database
    products = Product.query.all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/manage-products.html', products=products))

# Add product
@app.route('/products/add', methods=['GET','POST'])
def add_product():
    # add product to database
    
    # declare the Product Form
    form = ProductForm(request.form)

    msg = None

    if request.method == 'GET': 
        return render_template('layouts/default.html',
                                content=render_template( 'pages/add-product.html', form=form, message=msg ))    
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        name = request.form.get('name', '', type=str)
        product_type = request.form.get('product_type', '', type=int) 
        description    = request.form.get('description'   , '', type=str) 
        imageurl    = request.form.get('imageurl'   , '', type=str)
        # see if product already exists
        product = Product.query.filter_by(name=name, producttype_id=product_type).first()
        # 
        if product:
            msg = f'Error: A product named {product.name} already exists!'
        else:
            product = Product(name, description, product_type)
            product.save()
            msg = 'Product successfully created! Return to product page or add another product.'
    else:
        msg = 'I am sorry but the details you entered cannot be saved :('
    
    print (msg)
    return render_template('layouts/default.html', 
        content=render_template( 'pages/add-product.html', message=msg, form=form))        

# List all requests
@app.route('/requests')
def requests():
    return render_template('layouts/default.html', content=render_template( 'pages/manage-requests.html'))

# Delete product in request
@app.route('/products/delete/<id>')
def delete_product(id):
    # check if product is available
    product = Product.query.filter_by(id=id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        msg = 'Product has been successfuly deleted!'
    else:
        msg = 'The product you want to delete does not exist.'
    return redirect('/products')

# Edit product in request
@app.route('/products/edit/<id>', methods=['GET', 'POST'])
def edit_product(id):
    # declare the Product Form
    form = ProductForm(request.form)
    msg = None
    # check if product already exists
    product = Product.query.filter_by(id = id).first()

    # update select component value
    print(form.product_type)
    form.product_type.default = product.producttype_id
    if request.method == 'GET': 
        return render_template('layouts/default.html',
                                content=render_template('pages/edit-product.html', 
                                form=form, 
                                product=product, 
                                message=msg))
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        name            = request.form.get('name', '', type=str)
        product_type    = request.form.get('product_type', '', type=int) 
        description     = request.form.get('description' , '', type=str) 
        imageurl        = request.form.get('imageurl', '', type=str)
        # if the requested product exists
        if product:
            product.name = name
            product.producttype_id = product_type
            product.description = description
            db.session().commit()
            msg = 'Product successfully created! Return to product page or add another product.'            
        else:
            msg = f'Error: A product named {product.name} does not exist!'
    else:
        msg = 'I am sorry but the details you entered cannot be saved :('

    return redirect('/products')

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    # print (current_user)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    content = None
    try:
        # try to match the pages defined in -> pages/<input file>
        return render_template('layouts/default.html',
                                content=render_template( 'pages/'+path) )
    except:
        return render_template('layouts/auth-default.html',
                                content=render_template( 'pages/404.html' ) )
# Return sitemap 
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
