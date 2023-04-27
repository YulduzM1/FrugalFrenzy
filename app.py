import csv
import pandas as pd
import requests
import json
import mysql.connector
from flask import Flask, render_template, request, redirect


app = Flask(__name__)
import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='YulduzM1',
    database='findb'
)

mycursor = mydb.cursor()
sqlFormula = "INSERT INTO friends (name, friend_name) VALUES (%s, %s)"

url = 'http://api.nessieisreal.com/enterprise/accounts?key=3ae6e71b194eff8c8c1cb81093705a6d'
response = requests.get(url)
data = response.json()
# Define home page route
@app.route('/')
def index():
    return render_template('index.html', account_found=False)


# Define logout route to handle logout action
@app.route('/logout')
def logout():
    return redirect('/')

# Define login route to handle form submission
@app.route('/login', methods=['POST'])
def login():
    _id = request.form['_id']
    account_found = False
    nickname = ''
    for row in data['results']:
        if row['_id'] == _id:
            account_found = True
            nickname = row['nickname']
            balance = row['balance']
            break

    if account_found:
        return render_template('Home.html', _id=_id, nickname=nickname, balance=balance)
    else:
        return render_template('index.html', account_found=False, _id=_id)
    


# Define frienz page route
# Define frienz page route
@app.route('/frienz/<_id>', methods=['GET', 'POST'])
def frienz(_id):
    friend_name = None
    if request.method == 'POST':
        friend_name = request.form.get('friend_name')
        if friend_name is None:
            return render_template('frienz.html', friend_added=False, message='Please enter a friend name', _id=_id)
        val = (_id, friend_name)
        mycursor.execute("INSERT INTO friends (name, friend_name) VALUES (%s, %s)", val)
        mydb.commit()
    mycursor.execute("SELECT friend_name FROM friends WHERE name=%s", (_id,))
    friends = [friend[0] for friend in mycursor.fetchall()]
    return render_template('frienz.html', _id=_id, friends=friends, friend_name=friend_name, friend_added=True)


# Define home page route
@app.route('/home/<_id>')
def home(_id):
    account_found = False
    nickname = ''
    balance = 0
    for row in data['results']:
        if row['_id'] == _id:
            account_found = True
            nickname = row['nickname']
            balance = row['balance']
            break

    if account_found:
        return render_template('Home.html', _id=_id, nickname=nickname, balance=balance)
    else:
        return "Account not found"


# Define leadz page route
@app.route('/leadz/<_id>')
def leadz(_id):
    return render_template('leadz.html', _id=_id)


# Define leadz page route
@app.route('/planz/<_id>')
def planz(_id):
    return render_template('planz.html', _id=_id)
    

# Define about page route
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)