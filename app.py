
import pandas as pd
import requests
import secrets

import json
import mysql.connector
from flask import Flask, render_template, request, redirect, flash, session


app = Flask(__name__)
app.secret_key = '123julia'

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


from datetime import datetime, timedelta

@app.route('/planz/<_id>', methods=['GET', 'POST'])
def planz(_id):
    # Retrieve number of friends the user has
    mycursor.execute("SELECT COUNT(*) FROM friends WHERE name=%s", (_id,))
    num_friends = mycursor.fetchone()[0]

    # Retrieve groups created by the user
    mycursor.execute("SELECT * FROM communities WHERE leader_id=%s", (_id,))
    communities = mycursor.fetchall()

    # Handle form submission
    if request.method == 'POST':
        if 'create_group' in request.form:
            if len(communities) == 0:
                group_name = request.form.get('group_name')
                amount_wanted = request.form.get('amount_wanted')
                time_months = request.form.get('time_months')
                first_payment_date_str = request.form.get('first_payment_date')

                if not first_payment_date_str:
                    first_payment_date = datetime.now() + timedelta(days=5)
                else:
                    first_payment_date = datetime.strptime(first_payment_date_str, '%Y-%m-%d')



                # Calculate monthly plan amount
                plan_amount = (int(amount_wanted) // int(time_months) // num_friends)

                # Insert new group into database
                sql = "INSERT INTO communities (group_name, leader_id, amount_wanted, time_months, first_payment_date) VALUES (%s, %s, %s, %s, %s)"
                val = (group_name, _id, amount_wanted, time_months, first_payment_date)
                mycursor.execute(sql, val)
                mydb.commit()

                # Insert monthly payments into database
                for i in range(int(time_months)):
                    payment_date = first_payment_date + timedelta(days=30*i)
                    sql = "INSERT INTO payments (group_id, amount, member_id, payment_date) VALUES (%s, %s, %s, %s)"
                    val = (mycursor.lastrowid, plan_amount, _id, payment_date)
                    mycursor.execute(sql, val)
                    mydb.commit()

                # Redirect to the same page to refresh the number of groups and show a success message
                flash("Group created successfully!")
                return redirect('/planz/{}'.format(_id))
            else:
                flash("You can only create one group.")
        elif 'delete_group' in request.form:
            group_id = request.form.get('group_id')

            # Delete the group and payments from the database
            sql = "DELETE FROM communities WHERE group_id=%s"
            val = (group_id,)
            mycursor.execute(sql, val)

            sql = "DELETE FROM payments WHERE group_id=%s"
            val = (group_id,)
            mycursor.execute(sql, val)

            mydb.commit()

            # Redirect to the same page to refresh the list of groups and show a success message
            flash("Group deleted successfully!")
            return redirect('/planz/{}'.format(_id))

    return render_template('planz.html', _id=_id, num_friends=num_friends, communities=communities)

# Define about page route
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)