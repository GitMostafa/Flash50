from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import sqlite3

# Configure application
app = Flask(__name__)  

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensures responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

connect = sqlite3.connect("flash50.db", check_same_thread=False)
db = connect.cursor()


@app.route("/")
@login_required
def index():
    """Shows collections of the user"""

    # Loads the database info so that we push it into the main page
    db.execute("SELECT * FROM info WHERE user_id = ?", (session["user_id"],))
    info = db.fetchall()
    db.execute("SELECT * FROM collections_info WHERE user_id = ?", (session["user_id"],))
    collections_info = db.fetchall()
    # Loads the main page
    return render_template("index.html", info=info, collections_info=collections_info)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username", "small_popup")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password", "small_popup")
            return render_template("login.html")
        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = db.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            flash("invalid username and/or password", "big_popup")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return render_template("about.html")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers user"""
    if request.method == "POST":
        # Checks that the user has inputted a username
        if not request.form.get("username"):
            flash("must provide username", "small_popup")
            return render_template("register.html")

        # Checks if the username was already registered
        db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        username_check = db.fetchall()
        if len(username_check) == 1:
            flash("username already exists", "small_popup")
            return render_template("register.html")

        # Checks that the user has inputted a password
        if not request.form.get("password"):
            flash("must provide password", "small_popup")
            return render_template("register.html")
        # Checks that the user has re-entered the password
        if not request.form.get("confirmation"):
            flash("must confirm password", "small_popup")
            return render_template("register.html")

        # Checks that the password is re-entered correctly
        if request.form.get("password") != request.form.get("confirmation"):
            flash("password wasn't confirmed correctly", "huge_popup")
            return render_template("register.html")

        username = request.form.get("username")
        password = request.form.get("password")
        hashedPassword = generate_password_hash(password)

        # Save the new user into the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashedPassword))
        connect.commit()
        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        userInfo = db.fetchall()
        user_id = userInfo[0][0]
        db.execute("INSERT INTO info (user_id, collections_num) VALUES (?, ?)", (user_id, 0))
        connect.commit()
        
        return redirect("/")

    # Loads the register page if the method was get
    return render_template("register.html")

@app.route("/collection/<collection_name>", methods=["GET", "POST"])
@login_required
def view_collection(collection_name):
    """Views collection that user selects"""
    if request.method == "POST":
        db.execute("SELECT * FROM collections_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        collections_info = db.fetchall()
        db.execute("SELECT * FROM cards_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        cards_info = db.fetchall()
        return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)
    
    # Loads the home page if the method was get
    return redirect(url_for('index'))


@app.route("/addcard/<collection_name>", methods=["GET", "POST"])
@login_required
def add_card(collection_name):
    """Allows user to add a card"""
    if request.method == "POST":
        db.execute("SELECT * FROM collections_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        collections_info = db.fetchall()
        db.execute("SELECT * FROM cards_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        cards_info = db.fetchall()
        if not request.form.get("title_card"):
            flash("must provide name for the card", "big_popup_cards")
            return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)
        
        if not request.form.get("content_card"):
            flash("must provide content for the card", "big_popup_cards")
            return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)
        
        title_card = request.form.get("title_card")
        content_card = request.form.get("content_card")

        # Check title card and content's length so that it doesn't break the card's frame
        if len(title_card) > 12:
            flash("card title is too big", "tiny_popup")
            return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)
        if len(content_card) > 105:
            flash("card content is too big", "tiny_popup")
            return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)
        
        db.execute("INSERT INTO cards_info (user_id, collection_name, card_title, card_content) VALUES (?, ?, ?, ?)",
                   (session["user_id"], collection_name, title_card, content_card))
        connect.commit()
        
        db.execute("SELECT * FROM collections_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        cards_num = db.fetchall()
        userCards = cards_num[0][3] + 1
        db.execute("UPDATE collections_info SET cards_num = ? WHERE user_id = ? AND collection_name = ?", (userCards, session["user_id"], collection_name))
        connect.commit()
        db.execute("SELECT * FROM collections_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        collections_info = db.fetchall()
        db.execute("SELECT * FROM cards_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        cards_info = db.fetchall()
        return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)

    # Loads the home page if the method was get
    return redirect(url_for('index'))


@app.route("/deletecard/<collection_name>/<title_card>", methods=["GET", "POST"])
@login_required
def delete_card(collection_name, title_card):
    """Removes selected card"""
    if request.method == "POST":
        db.execute("DELETE FROM cards_info WHERE card_title = ? AND collection_name = ? AND user_id = ?", (title_card, collection_name, session["user_id"]))
        connect.commit()
        db.execute("SELECT * FROM collections_info WHERE collection_name = ? AND user_id = ?", (collection_name, session["user_id"]))
        cards_num = db.fetchall()
        userCards = cards_num[0][3] - 1
        db.execute("UPDATE collections_info SET cards_num = ? WHERE collection_name = ? AND user_id = ?", (userCards, collection_name, session["user_id"]))
        connect.commit()
        db.execute("SELECT * FROM collections_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        collections_info = db.fetchall()
        db.execute("SELECT * FROM cards_info WHERE user_id = ? AND collection_name = ?", (session["user_id"], collection_name))
        cards_info = db.fetchall()
        return render_template("collection.html", collections_info=collections_info, cards_info=cards_info, collection_name=collection_name)

    # Loads the home page if the method was get
    return redirect(url_for('index'))


@app.route("/addcollection", methods=["GET", "POST"])
@login_required
def add_collection():
    """Allows user to add a collection"""
    if request.method == "POST":
        # Checks that the user has inputted a collection name
        if not request.form.get("name_collection"):
            flash("must provide name for the collection", "big_popup")
            return render_template("addcollection.html")
        
        # Checks if the collection already exists
        db.execute("SELECT * FROM collections_info WHERE collection_name = ? AND user_id = ?",
                          (request.form.get("name_collection"), session["user_id"]))
        collection_check = db.fetchall()
        if len(collection_check) == 1:
            flash("collection already exists", "small_popup")
            return render_template("addcollection.html")
        
        # Checks if collection name is too big
        if len(request.form.get("name_collection")) > 6:
            flash("collection name is too big", "small_popup")
            return render_template("addcollection.html")
        
        # Updates database information after adding the collection
        collection = request.form.get("name_collection")
        db.execute("INSERT INTO collections_info (user_id, collection_name, cards_num) VALUES (?, ?, ?)", (session["user_id"], collection, 0))
        connect.commit()
        db.execute("SELECT * FROM info WHERE user_id = ?", (session["user_id"],))
        collections_num = db.fetchall()
        userCollections = collections_num[0][2] + 1
        db.execute("UPDATE info SET collections_num = ? WHERE user_id = ?", (userCollections, session["user_id"]))
        connect.commit()

        # Loads the main page
        return redirect(url_for('index'))
        
    # Loads the add collection page if the method was get
    return render_template("addcollection.html")


@app.route("/deletecollection/<collection_name>", methods=["GET", "POST"])
@login_required
def delete_collection(collection_name):
    """Deletes collection that user exists"""
    if request.method == "POST":
        db.execute("DELETE FROM collections_info WHERE collection_name = ? AND user_id = ?", (collection_name, session["user_id"]))
        connect.commit()
        db.execute("SELECT * FROM info WHERE user_id = ?", (session["user_id"],))
        collections_num = db.fetchall()
        userCollections = collections_num[0][2] - 1
        db.execute("UPDATE info SET collections_num = ? WHERE user_id = ?", (userCollections, session["user_id"]))
        connect.commit()

        return redirect(url_for('index'))

    # Loads the home page if the method was get
    return redirect(url_for('index'))


@app.route("/about")
@login_required
def about():
    """Shows about page"""
    return render_template("about.html")

if __name__ == '__main__':
	app.run(debug=True)