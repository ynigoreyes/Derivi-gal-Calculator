from flask import Flask, render_template, request, session, url_for, redirect
from functools import wraps
import json
import os
import sympy

app = Flask(__name__)
app.secret_key = 'DGCalc'

# List of things we need to solve
#
# How to get the history
# How to show the answers to the equation
# How to login so that we can see how we can save our history
# and associate it with our account
# Form validation with Python
# Learn what JSON is
# Learn what an API is
# Explain how to use I/O
# Learn real Python!

# Challenge:
# Rewrite the register and login routes to use MySQL

LOGIN_DIR = 'user/logins.txt'

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET:
    Return the login page

    POST:
    Gets data from POST to compare to the text file lines.
    If there is a user found in the textfile, then we will set the user's login
    status to True and their credentials to the recorded data. This can be used
    throughout the application

    Example:
    We can send the session['name'] to the front end so that we can see our name
    on the home page.
    It would read...
    "Welcome <session['name']>! This is Derivigal Calculator"

    """
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        userInput = request.form['username']                    # Grabs the user input for username
        pwInput = request.form['password']                      # Grabs the user input for password

        session['logged_in'] = False                            # Used for default case

        user_accounts = open(LOGIN_DIR, 'r')                    # Opens the logins.txt file as a read-only
        for accounts in user_accounts.readlines():              # Reads each line in the txt file
            name, tryUser, email, tryPw = accounts.split(',')   # splits the line at the ',' and sets the
                                                                # left side equal to tryUsername and right to tryPassword

            if userInput == tryUser.strip('\n').strip(' ') and pwInput == tryPw.strip('\n').strip(' '):

                session['logged_in'] = True                     # Sets the user's status to logged in
                session['name'] = name.strip('\n').strip(' ')   # Sets the user's name
                session['username'] = userInput                 # Sets the user's username
                session['email'] = email.strip('\n').strip(' ') # Sets the user's email
                return redirect(url_for('home'))

        if session['logged_in'] is False:                       # Checks to see if there is someone with that username
            print('Sorry, No user found with that name')        # Sends an error message to the user (replace with json)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/account', methods=['GET'])
def account():
    return render_template('account.html')

@app.route('/api/get-history', methods=['GET'])
def getHistory():
    """
    Gets the history of the current user and sends it in this format
    {
        'history': [<equation_1>, <equation_2>, <equation_n>]
    }
    """
    pass

if __name__ == '__main__':
    app.run()
