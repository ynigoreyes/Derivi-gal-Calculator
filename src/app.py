# Ynigo Reyes
# Texas Tech University
# Computer Science
# Started 3/19/2018
# Derivigal-Calculator
#
# This is a web app using Flask-Python with Javascript
# The purpose of this app is to show students what the real world use of python is
#
# Many of the students that attend ACMSDC Python Software Development are underclassman
# who may have never had any experience programming before and there are some students
# who come thinking that Python is useless and a kid's language. This type of web app's
# difficulty is high enough to challenge the beginners and show the naysayers that
# Python is used in the real world. In this case, it was used for rapid development.
#
# The situation goes as stated...
# Students are constantly switching between integral and derivative calculator so
# I am taking the time to make these two one web app that all students can use. It
# also prints out the answer in a way that most online homework text fields will accept
#
# CAUTION: APP WILL NOT WORK AFTER APRIL 30, 2018. MATHJAX CDN WILL NOT BE WORKING

from __future__ import division
from os import getcwd, listdir, path, chdir, getenv
from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from sympy import integrate, symbols, diff
from functools import wraps
from local_db import LOCAL_DB


# App Setup
app = Flask(__name__)
# Change this to whatever you want if ignoring env variables
app.secret_key = getenv("DGCALC")

# DB Setup
historyTable = LOCAL_DB("database", "history")
userTable = LOCAL_DB("database", "users")

historyTable.createColumns("username", "history")
userTable.createColumns("name", "username", "email", "password")

# List of things we need to solve
#
# How to write readable code
# How to get the history
# How to show the answers to the equation
# How to login so that we can see how we can save our history
# and associate it with our account
# Form validation with Python
# Learn what JSON is
# Learn what an API is (Teach them POST and GET; Submit and Refresh)
# Explain how to use I/O
# Learn real Python!

# Challenge:
# Rewrite the register and login routes to use MySQL
# Fix the implicit multiplication problem

HOME_DIR = getcwd()
LOGIN_DIR = path.normpath(getcwd() + '\\user\\logins.txt')
HISTORY_DIR = path.normpath(getcwd() + '\\user\\history')


# keeping track of the math symbols
x = symbols('x')


def is_logged_in(f):
  """
  This is the wrapper that will make sure that those who do have not logged in,
  will not be able to access the dashboard menu
  """
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect(url_for('login'))
  return wrap

@app.route('/', methods=['GET'])
def home():
  return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  """
  Lets the user register so that they can save their history

  A cool feature would be to allow the backend to send
  messages to be displayed on the home screen
  """
  if request.method == 'GET':
    return render_template('register.html')
  if request.method == 'POST':
    data = request.get_json()

    errorList = []        # This is where we will save all of our errors to display
    listOfUsernames = []  # This is where we will store all of the taken usernames

    name = data["name"]
    username = data['username']
    email = data['email']
    password = data['password']
    confirmPassword = data['confirmPassword']

    # We want to make sure that there are no duplicate usernames
    userTable.selectAny("username")
    listOfUsernames = userTable.fetchResults()
    if username in listOfUsernames:
      errorList.append("There is already a user with that name")

    # Form Validation
    # Ask why we do not want to use elif statements
    # Answer: We want all of these to be checked, no matter what
    if len(name) == 0 or len(username) == 0 or len(email) == 0 or len(password) == 0:
      errorList.append("Must fill in all fields")
    if confirmPassword != password:
      errorList.append("Passwords do not match")
    if len(username) < 5:
      errorList.append("Username must be at least 5 characters long")
    if "@" not in email:
      errorList.append("This email is invalid")

    # Checks for errors
    # If there are no errors, create a new user in the user and history table
    if len(errorList) == 0:
      userTable.insert(name, username, email, password)
      historyTable.insert(username, None)

    return jsonify({"errorMessages": errorList})


@app.route('/login', methods=['GET', 'POST'])
def login():
  """
  GET:
  Return the login page

  POST:
  Gets data from POST to compare to the text file lines.
  If there is a user found in the text file, then we will set the user's login
  status to True and their credentials to the recorded data. This can be used
  throughout the application

  """
  if request.method == 'GET':
    return render_template('login.html')

  elif request.method == 'POST':

    data = request.get_json()
    errorList = []                    # Will hold all of the errors we will pass

    userInput = data['username']      # Grabs the user input for username
    pwInput = data['password']        # Grabs the user input for password
    session['logged_in'] = False      # Used for default case

    # Find the user with that username and grab their password
    userTable.select(userInput, "username", "password")
    results = userTable.fetchResults()

    if data['username'] == "" or data['password'] == "":
      errorList.append("Please fill out all required forms")

    # Check if there were results found
    if len(results) == 0:
      errorList.append("No user found with that username")

    # Checks if the username exists and the password matches
    elif len(results) != 0 and pwInput == results[0]:
      errorList = []
      session['username'] = userInput   # Gives a unique cookie to work with
      session['logged_in'] = True       # Sets the user's status to logged in

    else:
      errorList.append("Invalid username or password")

    return jsonify({"errors": errorList})


@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  return redirect(url_for("home"))


@app.route('/api/evaluate', methods=['POST'])
def evaluate():
  """
  Evaluates the expression given

  Needs the:
  1. Operation to execute
  2. The equation to execute upon
  3. Setting symbol to x
  """
  data = request.get_json()

  equation = data['equation']
  operation = data['operation']
  answer = "~"

  # Integration or Derivitive
  if operation == 'integrate':
    answer = str(integrate(equation, x))
  elif operation == 'derive':
    answer = str(diff(equation, x))

  # Needed to fix the syntax so that math.js is able to read sympy
  if "**" in answer:
    answer = answer.replace("**", "^")

  return jsonify({'answer': str(answer)})


@app.route('/api/get-history', methods=['GET'])
@is_logged_in
def getHistory():
  """
  Gets the history of the current user and sends it in this format
  We are not trying to send duplicates so we convert the history into a set and then back into a list so that we can send it through JSON

  {
  "history": [<equation_1>, <equation_2>, <equation_n>]
  }
  """

  historyTable.select(session["username"], "username", "history")
  data = historyTable.fetchResults(amount=1)

  # If our user has a previous history
  if data[0] is not None:

    obj = []
    # Creates a new list of equations without duplicates
    # while keeping the order of the equations the same
    for eq in data[0]:
      if eq not in obj:
        obj.append(eq)

    # Replaces the old history with one that does not include any duplicates
    historyTable.replace(session['username'], 'username', obj,'history')

    return jsonify({"history": obj})

  # If the user does not have a history yet
  else:
    return jsonify({"history": []})



@app.route('/api/update-history', methods=['POST'])
@is_logged_in
def updateHistory():
  """
  Updates the history of the current user

  {
  "equationPost": "sin(x)"
  }
  """
  data = request.get_json()
  equation = data['equation'].replace(" ", "")

  historyTable.update(session["username"], "username", equation, "history")

  return jsonify({"status": "success"})


@app.route('/api/get-login-status', methods=['GET'])
def getLoginStatus():
  status = False

  if 'logged_in' in session.keys():
    status = session['logged_in']

  return jsonify({"status": status})


if __name__ == '__main__':
  app.run(debug=True)
