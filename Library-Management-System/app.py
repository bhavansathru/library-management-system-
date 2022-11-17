import threading
import requests
import json
import sqlite3
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
def dbActions():
   mydb = sqlite3.connect('lbms.db')
   mycursor = mydb.cursor()
   qry1 = """create table if not exists bookStocks (title text, author text, isbn text primary key,
       pubDate text, publication text, nob integer)"""
   qry2 = """create table if not exists users(name text, email text,userId text primary key,
         password text, phno integer, gender text, bloodgroup text, address text, userType text)"""
   qry3 = """create table if not exists issuedBooks(userId text primary key,
          isbn text,issuedDate text, returnDate text, fineAmount integer)"""
   mycursor.execute(qry1)
   mycursor.execute(qry2)
   mycursor.execute(qry3)
   mydb.commit()
   mycursor.close()
   mydb.close()
def addApiBooks():
   mydb = sqlite3.connect('lbms.db')
   mycursor = mydb.cursor()
   try:
      qry= "select * from bookStocks"
      mycursor.execute(qry)
   except:
      datas = None
   else:
      datas = mycursor.fetchall()
   if not bool(datas):
      req = requests.get("https://frappe.io/api/method/frappe-library")
      apiBooks = json.loads(req.content)['message']
      myBook = []
      c = 0
      for book in apiBooks:
         book = {'title' : book['title'],'authors' : book['authors'],
                  'isbn' : book['isbn'],'publicationDate' : '-'.join(book['publication_date'].split('/')[::-1]),
                  'publication' : book['publisher'], 'nob' : 0}
         if len(book["publicationDate"]) < 10:
            d = book["publicationDate"].split('-')
            if len(d[1])<2:
               d[1] = '0'+d[1]
            if len(d[2])<2:
               d[2] = '0'+d[2]
            book["publicationDate"] = d[0]+'-'+d[2]+'-'+d[1]
            
         myBook.append(book)
      books = [tuple(book.values()) for book in myBook]
      qry = """create table if not exists bookStocks (title text, author text, isbn text primary key,
         pubDate text, publication text, nob integer)"""
      qry2 = "insert into bookStocks (title, author, isbn, pubDate, publication, nob) values (?, ?, ?, ?, ?, ?)"
      mycursor.execute(qry)
      mycursor.executemany(qry2, books)
   mydb.commit()
   mycursor.close()
   mydb.close()
t1 = threading.Thread(target = addApiBooks)
t2 = threading.Thread(target = dbActions)
t1.start() 
t2.start() 

app = Flask(__name__)

app.secret_key = 'secret-key-2022'

@app.route('/')
def index():
   return render_template("login.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
   if(request.method == 'POST'):
        mydb = sqlite3.connect('lbms.db')
        myCursor = mydb.cursor()
        userId = request.form.get('userId')
        password = request.form.get('password')     
        myCursor.execute("select * from users where userId = ? and password = ? and userType = 'admin'",
        (userId, password))
        data = myCursor.fetchone() 
        myCursor.close()
        if bool(data):
            name = data[0]
            flash(f"Welcome {name}")  
            return redirect('/home')
        else:
            flash("invalid User Name password")
   return render_template("login.html")

@app.route('/home')
def home():
   return render_template("home.html")

@app.route("/addUser", methods = ['POST', 'GET'])
def addUser():
   if(request.method == 'POST'):
      try:
        name = request.form.get('name')
        email = request.form.get('email')
        userId = email[:email.index('@')]
        password = request.form.get('password') 
        phno = request.form.get('phno')  
        gender = request.form.get('gender')
        bloodgroup = request.form.get('bloodgroup')
        address = request.form.get('address')
        userType = request.form.get('userType')
        mydb = sqlite3.connect("lbms.db")
      except Exception as e:
         print(f"Error : {e}")
      else:
        mycursor = mydb.cursor()
        qry2 = """insert into users(name, email, userId, password, phno, gender, bloodgroup, address, userType)
         values (?, ?, ?, ?, ?, ?, ?, ?, ?) """
        mycursor.execute(qry2, (name, email,userId, password, phno, gender, bloodgroup, address, userType))
        mydb.commit()
        mycursor.close()
        mydb.close()
        return "<h1>Registered Successfully</h1>"

   return render_template("addUser.html")

@app.route("/addBook", methods = ['POST', 'GET'])
def addBook():
   if(request.method == 'POST'):
      try:
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn') 
        pubDate = request.form.get('pubDate') 
        publication = request.form.get('publication')
        nob = request.form.get('nob')
        mydb = sqlite3.connect("lbms.db")
      except Exception as e:
         print(f"Error : {e}")
      else:
        mycursor = mydb.cursor()
        qry2 = "insert into bookStocks (title, author, isbn, pubDate, publication, nob) values (?, ?, ?, ?, ?, ?)"
        mycursor.execute(qry2, (title, author, isbn, pubDate, publication, nob))
        mydb.commit()
        mycursor.close()
        mydb.close()
        return "<h1>Book Added Successfully</h1>"
   return render_template("addBook.html")

@app.route("/issueBook", methods = ['POST', 'GET'])
def issueBook():
   if request.method == "POST":
      try:
         userId = request.form.get("userId")
         isbn = request.form.get("isbn")
         issueDate = request.form.get("issueDate")
         mydb = sqlite3.connect("lbms.db")
      except Exception as e:
         print("Error : ", e)
      else:
         mycursor = mydb.cursor()
         qry2 = "insert into issuedBooks(userId, isbn, issuedDate)values(?, ?, ?)"
         mycursor.execute(qry2, (userId, isbn, issueDate))
         mydb.commit()
         mycursor.close()
         mydb.close()
         return "<h1>Book Issued Successfully</h1>"
   return render_template("issueBook.html")

@app.route("/returnBook", methods = ['POST', 'GET'])
def returnBook():
   if request.method == "POST":
      try:
         userId = request.form.get("userId")
         isbn = request.form.get("isbn")
         returnDate = request.form.get("returnDate")
         mydb = sqlite3.connect("lbms.db")
      except Exception as e:
         return f"<p>{e}</p>"
      else:
         mycursor = mydb.cursor()
         mycursor.execute("select issuedDate from issuedBooks where userId = ? and isbn = ?", (userId, isbn))
         issueDate = mycursor.fetchone()[0]
         if bool(issueDate):
            y1,m1,d1 = issueDate.split('-')
            iDate = datetime(int(y1),int(m1),int(d1))
            y2,m2,d2 = returnDate.split('-')
            rDate = datetime(int(y2),int(m2),int(d2))
            fineDays = int(str(rDate-iDate).split()[0])
            if fineDays > 15:
               fineAmount = (fineDays-15)*5
            else:
               fineAmount = 0
         else:
            return "<h1>In Valid User Id</h1>"
         qry1 = "update issuedBooks set returnDate = ?, fineAmount = ? where userId = ? and  isbn = ?"
         mycursor.execute(qry1, (returnDate, fineAmount, userId, isbn))
         mydb.commit()
         mycursor.close()
         mydb.close()
         return "<h1>Successfully Returned</h1><br><h3>Fine :"+str(fineAmount)+"</h3>"
   return render_template("returnBook.html")

@app.route("/issuedBook")
def issuedBook():
   mydb = sqlite3.connect("lbms.db")
   mycursor = mydb.cursor()
   mycursor.execute("select * from issuedBooks ")
   datas = mycursor.fetchall()
   mydb.commit()
   mycursor.close()
   mydb.close()
   return render_template("issuedBook.html", books = datas)

@app.route("/searchBook", methods = ['POST', 'GET'])
def searchBook():
   mydb = sqlite3.connect("lbms.db")
   mycursor = mydb.cursor()
   mycursor.execute("select * from bookStocks")
   datas = mycursor.fetchall()
   if request.method == 'POST':
      title = request.form.get("title")
      mycursor.execute("select * from bookStocks where title like ? order by title asc", ('%'+str(title)+'%',))
      datas = mycursor.fetchall()
   mydb.commit()
   mycursor.close()                    
   mydb.close()
   return render_template("searchBook.html", books = datas)
   
@app.route("/searchUser", methods = ['POST', 'GET'])
def searchUser():
   mydb = sqlite3.connect("lbms.db")
   mycursor = mydb.cursor()
   mycursor.execute("select * from users")
   datas = mycursor.fetchall()
   if request.method == 'POST':
      name = request.form.get("name")
      mycursor.execute("select * from users where name like ? order by name asc", ('%'+name+'%',))
      datas = mycursor.fetchall()
   mycursor.close()
   mydb.commit()
   mydb.close()
   return render_template("searchUser.html", users = datas)

@app.route("/editBook/<bookId>", methods = ['POST', "GET"])
def editBook(bookId):
   mydb = sqlite3.connect("lbms.db")
   mycursor = mydb.cursor()
   if request.method =="POST":
      title = request.form.get('title');              author = request.form.get('author')
      isbn = request.form.get('isbn') ;               pubDate = request.form.get('pubDate')  
      publication = request.form.get('publication');  nob = request.form.get('nob')
      qry = "update bookStocks set title=?, author=?, isbn=?, pubDate=?, publication=?, nob=? where isbn = ?"
      qry2= "select * from bookStocks"
      mycursor.execute(qry, (title, author, isbn, pubDate, publication, nob, bookId))
      mycursor.execute(qry2)
      datas = mycursor.fetchall()
      mydb.commit()
      mycursor.close()
      mydb.close()
      return render_template("searchBook.html", books=datas)
   else:
      mycursor.execute("select * from bookStocks where isbn = ?",(bookId,))
      datas = mycursor.fetchone()
      mycursor.close()
      mydb.close()
      print(type(datas))
      for x in datas:
         print(type(x))
      return render_template("editBook.html", book = datas)

@app.route("/editUser/<string:userID>", methods = ['POST', "GET"])
def editUser(userID):
   mydb = sqlite3.connect("lbms.db")
   mycursor = mydb.cursor()
   if request.method =="POST":
      name = request.form.get('name');             email = request.form.get('email')
      userId = email[:email.index('@')];           password = request.form.get('password') 
      phno = request.form.get('phno') ;            gender = request.form.get('gender')
      bloodgroup = request.form.get('bloodgroup'); address = request.form.get('address')
      userType = request.form.get('userType')
      qry = """update users set name=?, email=?, userId=?, password=?, phno=?, gender=?,
          bloodgroup=?, address=?, userType=? where userId = ?"""
      mycursor.execute(qry,(name, email,userId, password, phno, gender, bloodgroup, address, userType, userID))
      qry2= "select * from users"
      mycursor.execute(qry2)
      datas = mycursor.fetchall()
      mydb.commit()
      mycursor.close()
      mydb.close()
      return render_template("searchUser.html", users=datas)
   else:
      mycursor.execute("select * from users where userId = ?",(userID,))
      datas = mycursor.fetchone()
      mycursor.close()
      mydb.close()
      return render_template("editUser.html", user = datas)

@app.route("/deleteBook/<bookId>", methods = ['POST', 'GET'])
def deleteBook(bookId):
   if request.method == 'POST':
      mydb = sqlite3.connect("lbms.db")
      mycursor = mydb.cursor()
      qry = "delete from bookStocks where isbn = ?"
      mycursor.execute(qry, (bookId,))
      mycursor.execute("select * from bookStocks")
      datas = mycursor.fetchall()
      mydb.commit()
      mycursor.close()
      mydb.close()
      return render_template("searchBook.html", books=datas)

@app.route("/deleteUser/<string:userID>", methods = ['POST', 'GET'])
def deleteUser(userID):
   if request.method == 'POST':
      mydb = sqlite3.connect("lbms.db")
      mycursor = mydb.cursor()
      qry = "delete from users where userId = ?"
      mycursor.execute(qry, (userID,))
      mycursor.execute("select * from users")
      datas = mycursor.fetchall()
      mydb.commit()
      mycursor.close()
      mydb.close()
      return render_template("searchUser.html", users = datas)

if __name__ == '__main__':
   app.run(debug = True)
