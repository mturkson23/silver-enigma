# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging 

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory, flash
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from werkzeug.utils import secure_filename

# App modules
from app        import app, lm, db, bc
from app.models import User, Product, Stock, Request, Producttype, Stocktype, Requeststate, User, Role, Sale
from app.forms  import LoginForm, RegisterForm, ProductForm, StockForm, RequestForm, UserForm, SaleForm
from sqlalchemy import func

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
        fullname = request.form.get('fullname', '', type=str)
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email    = request.form.get('email'   , '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(username=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            flash('Error: User exists!')
        else:
            user = User(fullname, username, email, password, '0200000000', '', '', 1)
            # user = User(name, unm, email, pwd, phone_no, address, staff_no, role_id, imagename)

            user.save()

            flash('User created, please <a href="' + url_for('login') + '">login</a>')

    else:
        flash('Input error')

    return render_template('layouts/auth-default.html',
                            content=render_template( 'pages/register.html', form=form, msg=msg ) )


@app.route('/api/stats/<action>', methods=['GET'])
def stats(action):
    return {"revenue": "20,000", "users": 11, "sales": "12,000", "profit":"5,000"}

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
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Wrong password. Please try again.")
        else:
            flash("Invalid Credentials")

    return render_template('layouts/auth-default.html',
                            content=render_template( 'pages/login.html', form=form, msg=msg ))

# List all products
@app.route('/products')
def manage_products():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # fetch all products from database
    products = Product.query.all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/manage-products.html', products=products))

# List all stock items
@app.route('/stock')
def manage_stock():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # fetch all stock from database
    stock = Stock.query.all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/manage-stock.html', stock=stock))        

# Add stock
@app.route('/stock/add', methods=['GET','POST'])
def add_stock():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # add stock to database
    # declare the product form
    form = StockForm(request.form)
    form.product.choices = [(x.id, x.name) for x in Product.query.all()]
    form.stocktype.choices = [(x.id, x.name) for x in Stocktype.query.all()]

    msg = None
    if request.method == 'GET':
        form.process()
        return render_template('layouts/default.html',
                                content=render_template( 'pages/add-stock.html', form=form, message=msg ))    
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        cost_price = request.form.get('cost_price', '', type=float)
        sell_price = request.form.get('sell_price', '', type=float) 
        quantity    = request.form.get('quantity'   , '', type=int) 
        product_id    = request.form.get('product'   , '', type=int)
        stocktype_id    = request.form.get('stocktype'   , '', type=int)
        # see if stock entry already exists
        stock = Stock.query.filter_by(product_id=product_id, quantity=quantity, stocktype_id=stocktype_id).first()
        # 
        if stock:
            flash(f'Error: A stock entry for {stock.quantity} {stock.product} already exists!')
        else:
            stock = Stock(cost_price, sell_price, quantity, product_id, stocktype_id)
            stock.save()
            flash(f'Stock for {stock.product.name} successfully created! Return to stock page or add another stock.')
    else:
        flash('I am sorry but the details you entered cannot be saved :(')
    # print (msg)
    return render_template('layouts/default.html', 
        content=render_template( 'pages/add-stock.html', message=msg, form=form))

# Delete stock item
@app.route('/stock/delete/<id>')
def delete_stock(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if stock item exists
    stock = Stock.query.filter_by(id=id).first()
    if stock:
        db.session.delete(stock)
        db.session.commit()
        flash('Stock item has been successfuly deleted!')
    else:
        flash('The stock item you want to delete does not exist.')
    return redirect('/psalm2vs8/stock')

# Edit stock in request
@app.route('/stock/edit/<id>', methods=['GET', 'POST'])
def edit_stock(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # declare the Stock Form
    form = StockForm(request.form)
    form.product.choices = [(x.id, x.name) for x in Product.query.all()]
    form.stocktype.choices = [(x.id, x.name) for x in Stocktype.query.all()]
    msg = None
    # check if stock already exists
    stock = Stock.query.filter_by(id = id).first()
    form.product.default = stock.product_id
    form.stocktype.default = stock.stocktype_id

    if request.method == 'GET':
        form.process()
        return render_template('layouts/default.html',
                                content=render_template('pages/edit-stock.html', 
                                form=form, 
                                stock=stock, 
                                message=msg))
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        cost_price = request.form.get('cost_price', '', type=float)
        sell_price = request.form.get('sell_price', '', type=float) 
        quantity    = request.form.get('quantity'   , '', type=int) 
        product_id    = request.form.get('product'   , '', type=int)
        # if the requested product exists
        if stock:
            stock.cost_price = cost_price
            stock.sell_price = sell_price
            stock.quantity = quantity
            stock.product_id = product_id
            db.session().commit()
            flash('Stock item successfully created! Return to stock page or make further changes.')
        else:
            flash(f'Error: A stock entry for {stock.quantity} {stock.product} already exists')
    else:
        flash('I am sorry but the details you entered cannot be saved')
    return redirect('/psalm2vs8/stock')

# Add product
@app.route('/products/add', methods=['GET','POST'])
def add_product():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # add product to database
    
    # declare the Product Form
    form = ProductForm(request.form)
    form.product_type.choices = [(x.id, x) for x in Producttype.query.all()]
    msg = None

    if request.method == 'GET':
        form.process()
        return render_template('layouts/default.html',
                                content=render_template( 'pages/add-product.html', form=form, message=msg ))
    print (request.form)
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        name = request.form.get('name', '', type=str)
        product_type = request.form.get('product_type', '', type=int) 
        description    = request.form.get('description', '', type=str) 
        imageurl    = request.form.get('imageurl', '', type=str)
        # see if product already exists
        product = Product.query.filter_by(name=name, producttype_id=product_type).first()
        # 
        if product:
            flash(f'Error: A product named {product.name} already exists!')
        else:
            product = Product(name, description, product_type)
            product.save()
            flash(f'{name} successfully created! Return to product page or add another product.')
    else:
        print(form.e)
        flash('I am sorry but the details you entered cannot be saved')

    return render_template('layouts/default.html', 
        content=render_template( 'pages/add-product.html', message=msg, form=form))

# List all users
@app.route('/users')
def manage_users():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # declare the Request Form
    # form = RequestForm(request.form)
    # form.stock_item.choices = [(x.id, x) for x in Stock.query.all()]
    msg = None
    users = User.query.all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/manage-users.html', users= users, msg = msg ))

# List all requests
@app.route('/requests')
def manage_requests():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # declare the Request Form
    # form = RequestForm(request.form)
    # form.stock_item.choices = [(x.id, x) for x in Stock.query.all()]
    msg = None

    xrequests = Request.query.all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/manage-requests.html', xrequests= xrequests, msg = msg ))

# List all employee requests
@app.route('/employee-requests')
def employee_requests():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # declare the Request Form
    form = RequestForm(request.form)
    form.stock_item.choices = [(x.id, x) for x in Stock.query.all()]
    form.process()
    msg = None

    xrequests = Request.query.filter_by(user_id = current_user.id).all()
    return render_template('layouts/default.html', 
        content=render_template( 'pages/employee-requests.html', requests= xrequests, form = form, msg = msg ))

# Add employee request
@app.route('/employee-requests/add', methods=['POST'])
def add_employee_xrequest():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # add employee request to database
    # declare the Request Form
    form = RequestForm(request.form)
    form.stock_item.choices = [(x.id, x) for x in Stock.query.all()]
    msg = None
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        stock_item = request.form.get('stock_item', '', type=int)
        quantity = request.form.get('quantity', '', type=int) 
        # see if request already exists
        # TODO: filter by datecreated as well
        # request = Request.query.filter_by(user_id=current_user.id, product_id=stock_item, quantity = quantity).first()
        xrequest = Request(current_user.id, stock_item, 1, quantity, 1)
        # check if request is in bounds
        stock = Stock.query.filter_by(id=stock_item).first()
        if quantity <= stock.stocklevel:
            xrequest.save()
            flash('Request successfully created!')
        else:
            flash(f'I am sorry but we have only {stock.quantity} {stock} available')
    else:
        flash('I am sorry but the details you entered cannot be saved :(')
    return redirect('/psalm2vs8/employee-requests')

# Delete request
@app.route('/employee-requests/delete/<id>')
def delete_employee_request(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if request is available
    xrequest = Request.query.filter_by(id=id, user_id=current_user.id).first()
    if xrequest:
        db.session.delete(xrequest)
        db.session.commit()
        flash('Your request has been successfuly deleted!')
    else:
        flash('The request you want to delete does not exist!')
    return redirect('/psalm2vs8/employee-requests')

# record sales on employee request
@app.route('/employee-requests/sales/<id>')
def sales_employee_request(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if request is available
    approved_state_id = 3
    xrequest = Request.query.filter_by(id=id, user_id=current_user.id, state_id=approved_state_id).first()
    if xrequest:
        form = SaleForm(request.form, request_item = xrequest.id)
        msg = None
        # flash()
        sales = Sale.query.filter_by(request_id = id)
        sold = Sale.query.with_entities(func.sum(Sale.quantity).label("total")).filter_by(request_id = id).first()
        xsold_total = sold.total if sold.total else 0
        qty_remaining = xrequest.quantity - xsold_total
        balance = qty_remaining*xrequest.stock.sell_price
        return render_template('layouts/default.html', 
            content=render_template('pages/employee-sales.html', 
            balance = balance, 
            xrequest = xrequest,
            sales= sales,
            quantity_remaining = qty_remaining,
            form = form,
            msg = msg ))
    else:
        flash('The request you want to record sales on does not exist or it has not been approved!')
    return redirect('/psalm2vs8/employee-requests')            

# Add employee request
@app.route('/employee-sales/add', methods=['POST'])
def add_employee_sales():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # add employee sales to database
    # declare the Sale Form
    form = SaleForm(request.form)
    msg = None
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        quantity = request.form.get('quantity', 0, type=int)
        request_id = request.form.get('request_item', 0, type=int)
        # request_id = int(form.request_item.value)
        # print (request_id)
        sale = Sale(current_user.id, request_id, quantity)
        sale.save()
        flash('Sale entry successfully created!')
    else:
        flash('I am sorry but the details you entered cannot be saved :(')
    return redirect(f'/psalm2vs8/employee-requests/sales/{request_id}')

# approve request
@app.route('/requests/approve/<id>')
def approve_employee_request(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if request is available
    xrequest = Request.query.filter_by(id=id).first()
    approved_state = Requeststate.query.filter_by(code= 'approved').first()
    if xrequest:
        xrequest.state_id = approved_state.id
        db.session.commit()
        flash('This request has been approved!')
    else:
        flash('The request you want to approve does not exist.')
    return redirect('/psalm2vs8/requests')

# decline request
@app.route('/requests/decline/<id>')
def decline_employee_request(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if request is available
    xrequest = Request.query.filter_by(id=id).first()
    declined_state = Requeststate.query.filter_by(code= 'declined').first()
    if xrequest:
        xrequest.state_id = declined_state.id
        db.session.commit()
        flash('This request has been declined!')
    # else:
        # msg = 'The request you want to approve does not exist.'
    return redirect('/psalm2vs8/requests')

# Delete product in request
@app.route('/products/delete/<id>')
def delete_product(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if product is available
    product = Product.query.filter_by(id=id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('Product has been successfuly deleted!')
    else:
        flash('The product you want to delete does not exist.')
    return redirect('/psalm2vs8/products')

# Edit product in request
@app.route('/products/edit/<id>', methods=['GET', 'POST'])
def edit_product(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # declare the Product Form
    form = ProductForm(request.form)
    msg = None
    # print (current_user)
    # check if product already exists
    product = Product.query.filter_by(id = id).first()

    # update select component value
    form.product_type.default = product.producttype_id
    form.product_type.choices = [(x.id, x.name) for x in Producttype.query.all()]

    if request.method == 'GET':
        form.process() 
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
            flash(f'{name} successfully edited!')
        else:
            flash(f'Error: A product named {product.name} does not exist!')
    else:
        flash('I am sorry but the details you entered cannot be saved')
    return redirect('/psalm2vs8/products')

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
@login_required
def index(path):
    # if not current_user.is_authenticated:
    #     return redirect(url_for('login'))
    content = None
    try:
        employee_role = Role.query.filter_by(name = "Employee").first()
        if current_user.role_id == employee_role.id:
            return redirect(url_for('employee_requests'))        
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


# Add users
@app.route('/users/add', methods=['GET','POST'])
def add_users():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # add users to database
    
    # declare the user form
    form = UserForm(request.form)
    form.role.choices = [(x.id, x) for x in Role.query.all()]
    msg = None

    if request.method == 'GET':
        form.process()
        return render_template('layouts/default.html',
                                content=render_template( 'pages/add-user.html', form=form, message=msg ))    
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        files_dir = os.path.join(
            os.path.dirname(app.instance_path), 'app/static/files'
        )
        # assign form data to variables
        name = request.form.get('fullname', '', type=str)
        unm = request.form.get('username', '', type=str)
        pwd = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)
        phone_no = request.form.get('phone_no', '', type=str)
        address = request.form.get('address', '', type=str)
        staff_no = request.form.get('staff_no', '', type=str)
        role_id    = request.form.get('role'   , '', type=int)
        image    = request.files.get('image')
        idcard    = request.files.get('idcard')
        imagename = secure_filename(image.filename)
        idcardname = secure_filename(idcard.filename)
        # check if ID card image was chosen
        if idcardname == '':
            flash("Please select a valid ID card image")
            return redirect(url_for('add_users'))

        image.save(os.path.join(
            files_dir, 'photos', imagename
        ))
        idcard.save(os.path.join(
            files_dir, 'idcards', idcardname
        ))
        # see if user already exists
        user = User.query.filter_by(username=unm).first()
        if user:
            flash(f'Error: A user with the username {user.username} already exists!')
        else:
            user = User(name, unm, email, pwd, phone_no, address, staff_no, role_id, imagename)
            user.save()
            flash('User successfully created! <br/> Return to viewing user list or add another user.')
    else:
        flash('I am sorry but the details you entered cannot be saved :(')
    return render_template('layouts/default.html', content=render_template( 'pages/add-user.html', form=form ))

# Delete user in request
@app.route('/users/delete/<id>')
def delete_user(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))    
    # check if user is available
    user = User.query.filter_by(id=id).first()
    if user:
        flash(f'User: {user.username} has been successfuly deleted!')
        db.session.delete(user)
        db.session.commit()
    else:
        flash('The user you want to delete does not exist.')
    return redirect('/psalm2vs8/users')