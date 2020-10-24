import os
import json
from flask import Flask, session, render_template, url_for, request, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
from stopper import *
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Index page of the site.
@app.route("/")
def index():
    session.clear() #clears any session available
    return render_template("index.html") #renders the index page. Index page contains the login form.

#login route for checking the input credentials
@app.route("/login", methods=['POST', 'GET'])
def login():
    session.clear() #clears any session available
    name = request.form.get("username") #gets the input from the login form
    hash = request.form.get("password")

    #checks if either username or password is empty
    if not name:
        return render_template("error.html", message="Either your username or password is empty. Fix that!", url="/")
    if not hash:
        return render_template("error.html", message="Either your username or password is empty. Fix that!", url="/")

    #if not empty gets the information from database
    check = db.execute("SELECT * FROM users WHERE user_name=:name", {"name": name}).fetchone()

    #if there is no username in database return a error message
    if check is None:
        return render_template("error.html", message="User doesn't exist. Register", url="register")

    #create a session with id and name, name is used later
    session["id"] = check[0]
    session["name"] = check[1]

    #checks the name and password inputted and in database are matching
    if(name == check[1] and sha256_crypt.verify(hash, check[2])):
        return redirect("/search")

    #if doesnt match return an error message
    else:
        return render_template("error.html", message = "Username and Password do not match", url="/")

#logout route
@app.route("/logout")
def logout():
    session.clear() #clears all the session
    return redirect("/") #returns back to index page

#gets to register page
@app.route("/register", methods=['POST', 'GET']) #has both post and get method
def register():
    if request.method == 'GET': #if get method return only register page
        return render_template("register.html")
    
    if request.method == 'POST':
        reg_name = request.form.get("username")
        reg_hash = request.form.get("password") #get inputs from register page
        reg_check_hash = request.form.get("checkpassword")
         #encrypt the credentials

        #check if register form is empty
        if not reg_name:
            return render_template("error.html", message="Enter a valid name", url="register")
        elif not reg_hash:
            return render_template("error.html", message="Enter a valid password", url="register")
        elif not reg_check_hash:
            return render_template("error.html", message="Confirm Password", url="register")
        #verify password and confirm password match
        elif reg_hash != reg_check_hash:
            return render_template("error.html", message="Passwords doesn't match", url="register")

        reg_hash = sha256_crypt.encrypt(reg_hash)
        reg_check_hash = sha256_crypt.encrypt(reg_check_hash)

        #check if user already exists
        check_reg = db.execute("SELECT * FROM users WHERE user_name=:reg_name", {"reg_name": reg_name}).fetchone()
        db.commit()

        #if no user exist
        if check_reg is None:
            #create registration process
            insert_get = db.execute("INSERT INTO users(user_name, password)\
                                    VALUES(:reg_name, :reg_hash)",{"reg_name": reg_name, \
                                        "reg_hash": reg_hash})
            db.commit()
            return redirect("/") #after registration complete redirect to index page

        #if user exists return an error
        elif check_reg[1] == reg_name: 
            return render_template("error.html", message = "User already exists, Try a different one", url="register")

@app.route("/about")
def about():
    return render_template("about.html")
    

#for deleting a user
@app.route("/delete", methods=['POST', 'GET'])
@login_required
def delete():
    if request.method == "GET": #if method is post
        return render_template("delete.html",url = "search")
    if request.method == "POST": #if to delete
        db.execute("DELETE FROM comments WHERE user_id = :id", {"id": session["id"]})
        db.execute("DELETE FROM users WHERE user_name = :name",{ "name" : session["name"] }) #delete the user
        db.commit()
        return redirect("/") #redirect to index

#for search page
@app.route("/search")
@login_required
def search():
    return render_template("search_page.html", name = session["name"]) #return search_page

#shows the books available in database
@app.route("/result", methods=['POST', 'GET'])
@login_required
def result():
        search = str(request.form.get("searchbook")) #get book details from search page and convert it to string. conversion is for like search, because integer dont support like method
        search = search.title() #capitalize
        #search isbn, title, author or year
        if not search:
            return render_template("error.html", message = "Enter something to search", url="search")

        #selects books that matches the search
        result = db.execute("SELECT * FROM books WHERE isbn LIKE '%"+search+"%'\
                            OR title LIKE '%"+search+"%' OR author LIKE '%"+search+"%' \
                            OR year LIKE '%"+search+"%' LIMIT 10").fetchall()
        db.commit()
        
        #if no books found throw error
        if not result:
            return render_template("error.html", message = "No books found", url="search")

        #if books found show results
        return render_template("result.html", result = result, url = "/search") #give the results

#show the book details
@app.route("/book/<string:book_isbn>", methods=['GET', 'POST'])
@login_required
def book(book_isbn):
    #select book that matches isbn 
    selectbook = db.execute("SELECT * FROM books WHERE isbn = :book_isbn", {"book_isbn":book_isbn}).fetchone()
    db.commit()

    if request.method == "GET": #if method is get
        KEY = os.getenv("KEY") 
        bookapi = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book_isbn})    
        book = bookapi.json()
        gbook = book['books'][0] #get details from goodreads api
        reviews = db.execute("SELECT users.user_name, comment, rating, to_char(added_time, 'DD Mon YY - HH24:MI:SS') \
                             as added_time FROM users INNER JOIN comments ON users.user_id = comments.user_id WHERE \
                             books_id = :books ORDER BY added_time", {"books": selectbook[0]})
        return render_template("book.html", isbn = selectbook, gbook = gbook, reviews = reviews) #go to the book

    if request.method == "POST": #if method is post
        comment = str(request.form.get("comment")) #get comment and rating
        rate = int(request.form.get("rate"))
        comexist = db.execute("SELECT * FROM comments WHERE user_id = :user AND books_id = :bookid", {"user": session['id'], "bookid": selectbook[0]}).fetchone()
        db.commit()
        if comexist:
            flash("You have already reviewed the book", "error") #if user already reviewes the book return to book page
            return redirect("/book/" + book_isbn)
        
        if not comment: #if user tries to submit blank review 
            flash("You cannot submit blank review", "error")
            return redirect("/book/" + book_isbn)

        if rate > 5 and rate < 1: #if user tries to edit html and submit review stop it.
            flash("Rating is limited to 5", "error")
            return redirect("/book/"+book_isbn)
        
        else: #if everything fails insert the comment into database
            db.execute("INSERT INTO comments(user_id, books_id, comment, rating)\
                       VALUES(:user, :bookid, :comment, :rating)", {"user": session["id"],\
                       "bookid": selectbook[0], "comment": comment, "rating": rate})
            db.commit()
            flash('Review submitted!', 'info') #throw a flash message
            return redirect("/book/" + book_isbn)

@app.route("/api/<string:isbn>", methods=['GET'])
def api(isbn):

    #select books with comment
    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(comments.comment_id) as comments_count, \
                    AVG(comments.rating) as average_score \
                    FROM books \
                    INNER JOIN comments \
                    ON books.books_id = comments.books_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn})

    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN Or No reviews yet."}), 404
 
    tmp = row.fetchone()

    result = dict(tmp.items())
    
    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)

if __name__ == "__main__":
    app.run()