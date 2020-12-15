import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from datetime import datetime, timedelta


# today date global variable
today = datetime.now()
expiryd = datetime.now() + timedelta(days=14)


# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log Admin in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username!")
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password!")
            return render_template('login.html')

        # Query database for username
        rows = db.execute("SELECT * FROM admin WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("invalid username and/or password!")
            return render_template('login.html')

        # Remember which admin has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect admin to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/login1", methods=["GET", "POST"])
def login1():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username1"):
            flash("must provide username!")
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password1"):
            flash("must provide password!")
            return render_template('login.html')

        # Query database for username
        rows = db.execute("SELECT * FROM students WHERE username = :username",
                          username=request.form.get("username1"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password1")):
            flash("invalid username and/or password!")
            return render_template('login.html')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/index1")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET"])
@login_required
def index():
    """available books"""

    books= db.execute('SELECT * FROM books WHERE quantity > 0 ORDER BY title ASC')
    return render_template('index.html', books = books)

@app.route("/index1", methods=["GET", "POST"])
@login_required
def index1():
    if request.method=='post':
        books = db.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title ASC")
        return render_template('index1.html', books = books)

    else:
        books = db.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title ASC")
        return render_template('index1.html', books = books)


@app.route("/addbook", methods=["GET", "POST"])
@login_required
def addbook():
    """Add a book"""

    if request.method == 'POST':

        # take all input into variables
        book_id = request.form.get('book_id')
        author = request.form.get('author').upper()
        title = request.form.get('title').upper()
        qty = int(request.form.get('qty'))

        if qty <= 0:
            flash('Quanty must a positive integer')
            return redirect('/addbook')

        # add book in the system
        try:
            db.execute("INSERT INTO BOOKS VALUES(:book_id, :title, :author, :qty)", book_id = book_id, title = title, author = author, qty = qty)
        except:
            flash('book already exist')
            return redirect('/addbook')

        flash ('Book added successfully!')
        return redirect('/')

    else:
        return render_template('addbook.html')


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update book details"""

    if request.method == 'POST':

        # take all input into variables
        book_id = request.form.get('book_id')
        author = request.form.get('author').upper()
        title = request.form.get('title').upper()
        quantity = int(request.form.get('quantity'))

        if quantity <= 0:
            flash('Quanty must a positive integer')
            return redirect('/update')
        # check if book exist
        titlex = db.execute('SELECT * FROM books WHERE book_id = :book_id',book_id = book_id)
        if len(titlex) != 1:
            flash('Book not found')
            return redirect('/update')


        db.execute("UPDATE books SET title = :title, author = :author, quantity = :quantity WHERE book_id = :book_id",
                    book_id = book_id, title = title, author = author, quantity = quantity)


        flash ('Book updated successfully!')
        return redirect('/')

    else:
        return render_template('update.html')


@app.route("/books", methods=["GET"])
@login_required
def books():
    """all books"""

    books= db.execute('SELECT * FROM books')


    return render_template("books.html", books = books)

@app.route("/available", methods=["GET"])
@login_required
def available():
    """available books"""

    books= db.execute('SELECT * FROM books WHERE quantity > 0 ORDER BY title ASC')


    return render_template("available.html", books = books)

@app.route("/available1", methods=["GET"])
@login_required
def available1():
    """available books"""

    books= db.execute('SELECT * FROM books WHERE quantity > 0 ORDER BY title ASC')


    return render_template("available1.html", books = books)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure password was confirmed is the same
        if request.form.get("password") != request.form.get("confirmation"):
            flash('password and confirmation must be the same!')
            return render_template('register.html')

        # Add user into the database table

        try:
            key = db.execute("INSERT INTO students(id, name, username, password) VALUES(:id, :name, :username, :password);",
                            id = request.form.get('id'),
                            name = request.form.get('name'),
                            username = request.form.get('username'),
                            password = generate_password_hash(request.form.get('password')))
        except:
            flash("User already exists")
            return render_template('register.html')

        if key is None:
            flash("Registration error! Check if user is not already registered")
            return render_template('register.html')
        session["user_id"] = key
        username = request.form.get('username')
        flash(f"{username} Registered")
        return redirect("/index1")


    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for books"""
    if request.method == "POST":
        book_id = request.form.get('book_id')

        books = db.execute('SELECT * FROM books WHERE book_id = :book_id', book_id = book_id)

        if len(books) < 1:
            flash('BOOK ID not found!')
            return redirect('search')

        flash('Book found!')
        return render_template('searched.html', books=books)
    else:
        return render_template('search.html')


@app.route("/search1", methods=["GET", "POST"])
@login_required
def search1():
    """Search for books"""
    if request.method == "POST":
        book_id = request.form.get('book_id')

        books = db.execute('SELECT * FROM books WHERE book_id = :book_id and quantity > 0', book_id = book_id)

        if len(books) < 1:
            flash('BOOK ID not found or not available for now!')
            return redirect('/search1')

        flash("Book found")
        return render_template('searched1.html', books=books)


    else:
        return render_template('search1.html')

@app.route("/order1", methods=["GET", "POST"])
@login_required
def order1():
    """Place an order for books"""
    # mm/dd/y
    d3 = today.strftime("%b-%d-%Y")
    expiry = expiryd.strftime("%b-%d-%Y")
    student_id = session['user_id']
    if request.method == 'POST':
        # query book by book id
        book_id = request.form.get('book_id')
        try:
            book = db.execute('SELECT * FROM books WHERE book_id = :book_id', book_id=book_id)
        except:
            flash('Book not found or unavailable!')
            return redirect('/order1')

        # check for the number of books in store
        try:
            qty = book[0]['quantity']
        except:
            flash('Book not found!')
            return redirect('/order1')
        if qty < 1:
            flash('Book unavailable for now, try again later')
            return redirect('/order1')

        # keep track of all ordered books
        student = db.execute('SELECT * FROM students WHERE id = :student_id', student_id = student_id)
        book_id = book[0]['book_id']
        title = book[0]['title']
        author = book[0]['author']
        quantity = book[0]['quantity']
        name = student[0]['name']
        try:
            db.execute('INSERT INTO orders(book_id, title, author, student_id, date, expiry) VALUES(:book_id, :title, :author, :name, :date, :expiry)',
                        book_id = book_id, title = title, author = author, name = name, date = d3, expiry = expiry)
            # update the number of available books
            quantity1 = int(quantity) - 1
            db.execute('UPDATE books SET quantity = :quantity1  WHERE book_id = :book_id', quantity1 = quantity1, book_id = book_id)

        except:
            flash('ERROR!!! could not place order check if you have not already ordered the same book!')
            return redirect('/order1')

        flash('order placed! You have 2 weeks to return the book!')
        return redirect('/rented1')

    else:
        return render_template('order1.html', d3 = d3, student_id = student_id, expiry = expiry)


@app.route("/return1", methods=["GET", "POST"])
@login_required
def return1():
    """return a books"""
    # mm/dd/y
    d3 = today.strftime("%b-%d-%Y %H:%M:%S")
    student_id = session['user_id']

    if request.method == 'POST':
        order = int(request.form.get('book_id'))
        books = db.execute('SELECT * FROM books WHERE book_id = :book_id', book_id = order)
        quantity = books[0]['quantity']
        if order < 0:
            flash('id cannot be a negative integer')
            return redirect('/return1')

        # check if user have the book
        book_id = request.form.get('book_id')
        try:
            db.execute('SELECT * FROM orders WHERE book_id = :book_id', book_id = book_id)
        except:
            flash('you do not have that book')
            return render_template('return1.html')

        # return the book from orders to available books

        try:
            db.execute('DELETE FROM orders WHERE book_id = :book_id', book_id = book_id)
            quantity1 = int(quantity) + 1
            db.execute('UPDATE books SET quantity = :quantity1  WHERE book_id = :book_id', quantity1 = quantity1, book_id = book_id)

        except:
            flash('ERROR while returning the book')
            return redirect('/index1')

        flash('Book returned successfully!')
        return redirect('/index1')

    else:
        return render_template('return1.html', d3 = d3, student_id = student_id)


@app.route("/rented1", methods=["GET"])
@login_required
def rented1():
    """rented books"""
    student_id = session['user_id']
    student = db.execute('SELECT * FROM students WHERE id = :student_id', student_id = student_id)
    name = student[0]['name']
    books= db.execute('SELECT * FROM orders WHERE student_id = :name ORDER BY expiry ASC', name = name)

    # try to calculate the remaining days to expiry
    today = datetime.now().date()


    return render_template('rented1.html', books = books, today = today)

@app.route("/orders", methods=["GET"])
@login_required
def orders():
    """all orders for books"""
    orders= db.execute('SELECT * FROM orders ORDER BY expiry ASC')


    # try to calculate the remaining days to expiry
    today = datetime.now().date()

    return render_template('orders.html', orders = orders, today = today)


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """change password"""
    if request.method == 'POST':
        # make sure the passwords match
        if request.form.get('password') != request.form.get('confirmation'):
            flash("password and confirmation must be the same!")
            return redirect ('/changepassword')

        # select student from students
        hash = generate_password_hash(request.form.get('password'))

        try:
            db.execute("SELECT password FROM students WHERE id = :user_id", user_id=session["user_id"])
        except:
            flash('Error while changing password')
            return redirect ('/changepassword')

        # update password
        try:
            db.execute("UPDATE students SET password = :hash WHERE id = :user_id", hash = hash, user_id = session["user_id"])
        except:
            flash('Error while changing password')
            return redirect ('/changepassword')

        flash("Password successfully changed!")
        return redirect("/index1")


    else:
        return render_template('changepassword.html')


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """change password"""
    if request.method == 'POST':
        # make sure the passwords match
        if request.form.get('password') != request.form.get('confirmation'):
            flash("password and confirmation must be the same!")
            return redirect ('/changepass')

        # select student from students
        hash = generate_password_hash(request.form.get('password'))

        try:
            db.execute("SELECT password FROM admin WHERE id = :user_id", user_id=session["user_id"])
        except:
            flash('Error while changing password')
            return redirect ('/changepass')

        # update password
        try:
            db.execute("UPDATE admin SET password = :hash WHERE id = :user_id", hash = hash, user_id = session["user_id"])
        except:
            flash('Error while changing password')
            return redirect ('/changepassword')

        flash("Password successfully changed!")
        return redirect("/")


    else:
        return render_template('changepass.html')


@app.route("/addadmin", methods=["GET", "POST"])
@login_required
def addadmin():
    """Add another admin"""

    if request.method == 'POST':
        if request.form.get("password") != request.form.get("confirmation"):
            flash('password and confirmation must be the same!')
            return render_template('addadmin.html')

        # give permission to super admin only
        admin = db.execute('SELECT * FROM admin WHERE id = :user_id', user_id = session['user_id'])
        if admin[0]['id'] != 2:
            flash('only super admin can add another admin')
            return redirect('/')
        # Add admin into the database table

        try:
            key = db.execute("INSERT INTO admin(name, username, password) VALUES(:name, :username, :password);",
                            name = request.form.get('name'),
                            username = request.form.get('username'),
                            password = generate_password_hash(request.form.get('password')))
        except:
            flash("admin already exists")
            return render_template('addadmin.html')

        if key is None:
            flash("Registration error! Check if admin is not already registered")
            return redirect('/addadmin')
        session["user_id"] = key
        username = request.form.get('username')
        flash(f"{username} Registered")
        return redirect("/")

    else:
        return render_template('addadmin.html')

@app.route("/allstudents", methods=["GET"])
@login_required
def allstudents():
    """registered students"""
    students= db.execute('SELECT * FROM students')

    return render_template('allstudents.html', students = students)
