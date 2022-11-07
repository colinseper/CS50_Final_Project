# importing python libraries
import sqlite3
from flask import Flask, redirect, render_template, flash, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

# imports login required function and apology
from helpers import login_required, apology

# configures application
app = Flask(__name__)

# ensures the templates are auto-reloaded
# all updates to the template are done automatically
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configures session to use filesystem (not cookies) aka. in the project folder
# creates an ability to store more data, additionally data is needed at the server
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# makes sure website requests are not cached aka. responses aren't stored to be reused
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def history():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():

    # clears user data
    session.clear()

    # sends user data
    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password")

        # check for user input
        if not usern:
            return apology("Please Enter Your Username")
        elif not passw:
            return apology("Please Enter Your Password")
        else:
            connection = sqlite3.connect("catalog.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ?", [usern])
            user_tab = cursor.fetchall()

            # 2 represents password hash in catalog
            if len(user_tab) != 1 or not check_password_hash(user_tab[0][2], passw):
                return apology("Invalid Username or Password")
            else:
                # record the user has logged in
                session["user_id"] = user_tab[0][0]

                # closing the cursor and connection
                cursor.close()
                connection.close()

                return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods= ["GET", "POST"])
def register():

    # sending user info
    if request.method == "POST":

        # create a connection to the resume database
        # check same thread = False allows connection to be used across multiple cursors
        connection = sqlite3.connect("catalog.db")

        # creates a cursor object to execute queries in SQLite3
        cursor = connection.cursor()

        usern = request.form.get("username")
        passw = request.form.get("password")
        confirm = request.form.get("confirmation")

        # execute a query through the cursor and fetch the result, storing it in check_usern
        # returns list of tuples
        cursor.execute("SELECT * FROM users WHERE username = ?", [usern])
        usern_check = cursor.fetchall()

        # registers user, ensuring passwords are at least 7 characters, with an upper and special character
        if not usern:
            return apology("Please Enter A Username")
        elif len(usern_check) != 0:
            return apology("Please Choose A Different Username")
        elif not passw:
            return apology("Please Enter A Password")
        elif len(passw) < 7:
            return apology("Please Enter A Password with at Least 7 Characters")
        elif passw.islower():
            return apology("Please Enter A Password with an Uppercase Letter")

        # .isalnum() checks if a string is alphanumeric (ie. has only letters or numbers) and returns false otherwise
        elif passw.isalnum():
            return apology("Please Use A Special Character in Your Password")
        elif not confirm:
            return apology("Please Re-Enter Your Password")
        elif passw != confirm:
            return apology("Password's Do Not Match")

        # if all checks pass
        else:
            passw_hash = generate_password_hash(passw)

            # use cursor to execute, shouldn't need to fetchall() unless I want to return a list
            # commit commits the changes to the db
            cursor.execute("INSERT INTO users (username, pass_hash) VALUES (?,?)", [usern, passw_hash])
            connection.commit()

            # close the cursor and connection to the database
            cursor.close()
            connection.close()

            return redirect("/")
    else:
        return render_template("register.html")

@app.route("/shop", methods= ["GET", "POST"])
@login_required
def shop():
    id = session["user_id"]

    if request.method == "POST":
        book = request.form.get("book")
        water_b = request.form.get("wbot")
        chessboard = request.form.get("cb")
        hammock = request.form.get("hck")

        test = [book, water_b, chessboard, hammock]
        success = []

        # check item the user bought
        for item in test:
            if item != None:
                success.append(item)

        # assigns bought item
        bought = success[0]

        # assign price value
        if bought == book:
            price = 5.95
            quantity = request.form.get("bq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        elif bought == water_b:
            price = 3.25
            quantity = request.form.get("wbq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        elif bought == chessboard:
            price = 15.00
            quantity = request.form.get("cq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        else:
            price = 20.00
            quantity = request.form.get("hq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        connection = sqlite3.connect("catalog.db")
        cursor = connection.cursor()
        total = price * quantity
        cursor.execute("INSERT INTO cart (user_id, item, cost, quantity, cost_tot) VALUES (?, ?, ?, ?, ?)", [id, bought, price, quantity, total])
        connection.commit()
        cursor.close()
        connection.close()

        flash("Item Successfully Bought")

        return redirect("/shop")
    else:
        return render_template("shop.html")

@app.route("/deals", methods= ["GET", "POST"])
@login_required
def deals():
    id = session["user_id"]

    if request.method == "POST":
        laptop = request.form.get("laptop")
        headphones = request.form.get("hp")
        necklace = request.form.get("neck")
        sweatshirt = request.form.get("swt")

        test = [laptop, headphones, necklace, sweatshirt]
        success = []

        for item in test:
            if item != None:
                success.append(item)

        bought = success[0]

        if bought == laptop:
            price = 100
            quantity = request.form.get("lq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        elif bought == headphones:
            price = 50
            quantity = request.form.get("hq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        elif bought == necklace:
            price = 80
            quantity = request.form.get("nq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        else:
            price = 30
            quantity = request.form.get("sq")

            if not quantity:
                return apology("Please Enter the Quantity")
            else:
                quantity = int(quantity)

        connection = sqlite3.connect("catalog.db")
        cursor = connection.cursor()
        total = price * quantity
        cursor.execute("INSERT INTO cart (user_id, item, cost, quantity, cost_tot) VALUES (?, ?, ?, ?, ?)", [id, bought, price, quantity, total])
        connection.commit()
        cursor.close()
        connection.close()

        flash("Item Successfully Bought")

        return redirect("/deals")
    else:
        return render_template("deals.html")

@app.route("/orders")
@login_required
def orders():
    id = session["user_id"]

    connection = sqlite3.connect("catalog.db")
    cursor = connection.cursor()
    cursor.execute("SELECT order_id, cost, time FROM orders WHERE user_id = ?", [id])
    orders = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("orders.html", orders=orders)

@app.route("/cart", methods = ["GET", "POST"])
@login_required
def cart():
    id = session["user_id"]

    if request.method == "POST":
        # checks for remove
        removed_id = request.form.get("remove")
        connection = sqlite3.connect("catalog.db")
        cursor = connection.cursor()

        if removed_id != None:
            cursor.execute("DELETE FROM cart WHERE cart_id = ?", [removed_id])
            connection.commit()
            cursor.close()
            connection.close()

            flash("Removed from cart")

            return redirect("/cart")

        # gets date
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d")

        cursor.execute("SELECT SUM(cost_tot) FROM cart WHERE user_id = ?", [id])
        cost_t = cursor.fetchall()
        cost = cost_t[0][0]

        if cost == None:
            return apology("Nothing in Cart to Checkout")

        cursor.execute("INSERT INTO orders (user_id, cost, time) VALUES (?, ?, ?)", [id, cost, time])
        connection.commit()
        cursor.execute("DELETE FROM cart")
        connection.commit()

        flash("Checkout Complete!")

        return redirect("/cart")
    else:
        connection = sqlite3.connect("catalog.db")
        cursor = connection.cursor()
        cursor.execute("SELECT cart_id, item, cost, quantity, cost_tot FROM cart WHERE user_id = ?", [id])
        cart = cursor.fetchall()
        cursor.close()
        connection.close()

        return render_template("cart.html", cart=cart)

@app.route("/contact", methods= ["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        id = session["user_id"]
        option = request.form.get("option")
        complaint = request.form.get("issue")

        if len(complaint) == 0:
            return apology("Please Enter A Complaint")

        # connect and insert complaint into db
        connection = sqlite3.connect("catalog.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO complaints (user_id, type, complaint) VALUES (?, ?, ?)", [id, option, complaint])
        connection.commit()

        # sends a message over to the html page
        flash("Successfully Sent")

        cursor.close()
        connection.close()

        return redirect("/")
    else:
        return render_template("contact.html")