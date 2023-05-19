import pandas as py 
import requests
import decimal

import json
import mysql.connector
from flask import Flask, render_template, request, redirect, flash, session, url_for


app = Flask(__name__)
app.secret_key = '123julia'

import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='user_211',
    passwd='frugalFrienz.123',
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
@app.route('/frienz/<_id>', methods=['GET', 'POST'])
def frienz(_id):
    friend_name = None
    if request.method == 'POST':
        friend_name = request.form.get('friend_name')
       
        # Check if the user is already part of a community
        mycursor.execute("SELECT COUNT(*) FROM communities WHERE leader_id = %s", (_id,))
        community_count = mycursor.fetchone()[0]

        if community_count > 0:
            message = "You are already part of a community and cannot add more friends."
            mycursor.execute("SELECT friend_name FROM friends WHERE name=%s", (_id,))
            friends = [friend[0] for friend in mycursor.fetchall()]

            return render_template('frienz.html', friend_added=False, message=message, _id=_id, friends=friends, friend_name=friend_name)

        # Check if the friend is already part of a group or listed as a friend
        mycursor.execute("SELECT COUNT(*) FROM communities WHERE leader_id = %s", (friend_name,))
        group_count = mycursor.fetchone()[0]
        mycursor.execute("SELECT COUNT(*) FROM friends WHERE name = %s AND friend_name = %s", (_id, friend_name))
        friend_count = mycursor.fetchone()[0]

        if group_count > 0 or friend_count > 0:
            message = "The provided friend is already part of a group or listed as a friend."
            mycursor.execute("SELECT friend_name FROM friends WHERE name=%s", (_id,))
            friends = [friend[0] for friend in mycursor.fetchall()]

            return render_template('frienz.html', friend_added=False, message=message, _id=_id, friends=friends, friend_name=friend_name)
        
        val = (_id, friend_name)
        mycursor.execute("INSERT INTO friends (name, friend_name) VALUES (%s, %s)", val)
        mydb.commit()

        # Add the friend_name account as a friend for the user
        val = (friend_name, _id)
        mycursor.execute("INSERT INTO friends (name, friend_name) VALUES (%s, %s)", val)
        mydb.commit()
       
        

    mycursor.execute("SELECT friend_name FROM friends WHERE name=%s", (_id,))
    friends = [friend[0] for friend in mycursor.fetchall()]

    return render_template('frienz.html', _id=_id, friend_added=True, friends=friends, friend_name=friend_name)


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
    sql = "SELECT group_id FROM communities WHERE leader_id = %s"
    val = (_id,)
    mycursor.execute(sql, val)
    group = mycursor.fetchone()
    if group is None:
        amount_wanted = None
        savings_goal = None
    else:
        mycursor.execute("SELECT amount_saved, amount_wanted FROM communities WHERE leader_id = %s", (_id,))
        result = mycursor.fetchone()
        savings_goal = result[0]
        amount_wanted = result[1]




    if account_found:
        return render_template('Home.html', _id=_id, amount_wanted=amount_wanted, savings_goal=savings_goal, nickname=nickname, balance=balance)
    else:
        return "Account not found"
    




# Define leadz page route
@app.route('/leadz/<_id>')
def leadz(_id):
    return render_template('leadz.html', _id=_id)


from datetime import datetime, timedelta

@app.route('/planz/<_id>', methods=['GET', 'POST'])
def planz(_id):

    # Check if the current user is a member of any group
    mycursor.execute("SELECT group_id FROM payments WHERE member_id=%s", (_id,))
    group_info = mycursor.fetchall()
    if group_info:
        print(group_info)
        group_id = group_info[0][0]

        # Retrieve the leader's ID
        mycursor.execute("SELECT leader_id FROM communities WHERE group_id=%s", (group_id,))
        leader_id = mycursor.fetchone()[0]

        # Retrieve the leader's name
        mycursor.execute("SELECT name FROM friends WHERE friend_name=%s", (leader_id,))
        leader_name = mycursor.fetchone()[0]

        # Retrieve the number of friends the leader has
        mycursor.execute("SELECT COUNT(*) FROM friends WHERE name=%s", (leader_name,))
        num_friends = mycursor.fetchone()[0]

        # Retrieve the groups created by the leader
        mycursor.execute("SELECT * FROM communities WHERE leader_id=%s LIMIT 1", (leader_id,))
        community = mycursor.fetchone()

        # Fetch payments for the group from the database
        sql = "SELECT * FROM payments WHERE group_id=%s"
        val = (group_id,)
        mycursor.execute(sql, val)
        payments = mycursor.fetchall()

        if 'mark_paid' in request.form:
            payment_id = request.form.get('payment_id')

            # Get the group_id associated with the given payment_id
            sql = "SELECT group_id FROM payments WHERE payment_id=%s"
            val = (payment_id,)
            mycursor.execute(sql, val)
            group_id = mycursor.fetchone()[0]

            # Update the paid_status in the payments table
            sql = "UPDATE payments SET paid_status=0 WHERE payment_id=%s"
            val = (payment_id,)
            payments  = mycursor.fetchall()
            mycursor.execute(sql, val)
            mydb.commit()

            # Get the total amount saved so far in the group
            mycursor.execute("SELECT SUM(amount) FROM payments WHERE group_id=%s AND paid_status=0", (group_id,))
            total_saved = mycursor.fetchone()[0]
            
            # Update the amount_saved field in the communities table
            sql = "UPDATE communities SET amount_saved=%s WHERE group_id=%s"
            val = (total_saved, group_id)
            mycursor.execute(sql, val)
            mydb.commit()

            return redirect(url_for('planz', _id=_id))
        
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

            return redirect('/planz/{}'.format(_id))

        return render_template('planz.html', _id=_id, num_friends=num_friends, payments=payments, group=community)

    # Retrieve number of friends the user has
    mycursor.execute("SELECT COUNT(*) FROM friends WHERE name=%s", (_id,))
    num_friends = mycursor.fetchone()[0]

    # Retrieve groups created by the user
    mycursor.execute("SELECT * FROM communities WHERE leader_id=%s LIMIT 1", (_id,))
    community = mycursor.fetchone()
    payments=[]
    # Handle form submission
    if request.method == 'POST':
        if 'create_group' in request.form:    
            if num_friends != 0:
                group_name = request.form.get('group_name')
                amount_wanted = request.form.get('amount_wanted')
                time_months = request.form.get('time_months')
                first_payment_date_str = request.form.get('first_payment_date')

                if not first_payment_date_str:
                    first_payment_date = datetime.now() + timedelta(days=5)
                else:
                    first_payment_date = datetime.strptime(first_payment_date_str, '%Y-%m-%d')

                # Calculate monthly plan amount
                plan_amount = (int(amount_wanted) // int(time_months) // (num_friends+1))

                # Insert new group into database
                sql = "INSERT INTO communities (group_name, leader_id, amount_wanted, time_months, first_payment_date) VALUES (%s, %s, %s, %s, %s)"
                val = (group_name, _id, amount_wanted, time_months, first_payment_date)
                mycursor.execute(sql, val)
                mydb.commit()

                # Get a list of member_ids associated with the leader_id
                sql = "SELECT friend_name FROM friends WHERE name = %s"
                val = (_id,)
                mycursor.execute(sql, val)
                result = mycursor.fetchall()
                member_ids = [row[0] for row in result]
                # Add leader_id to the beginning of the list
                member_ids.insert(0, _id)
         
                # Get group_id associated with the leader_id
                sql = "SELECT group_id FROM communities WHERE leader_id = %s"
                val = (_id,)
                mycursor.execute(sql, val)
                group_id = mycursor.fetchone()[0]
                mycursor.fetchall()
                # Insert monthly payments into database
                for i in range(int(time_months)):
                    payment_date = first_payment_date + timedelta(days=30*i)
                    for member_id in member_ids:
                        # Insert a new payment record with the member_id and friend_name
                        sql = "INSERT INTO payments (group_id, member_id, amount, payment_date, paid_status) VALUES (%s, %s, %s, %s, %s)"
                        val = (group_id, member_id, plan_amount, payment_date, plan_amount)
                        mycursor.execute(sql, val)
                        mydb.commit()

                # Redirect to the same page to refresh the number of groups and show a success message
                flash("Group created successfully!")
                return redirect(url_for('planz', _id=_id, group_id=group_id, payments=payments))
            else:
                flash("Sorry, you need to have at least one friend to create a group.")
       
    if community != None:
        # Fetch payments for the group from the database
        sql = "SELECT * FROM payments WHERE group_id = " + str(community[0])
        mycursor.execute(sql)
        payments = mycursor.fetchall()
    



    return render_template('planz.html', _id=_id, num_friends=num_friends, payments=payments, group=community)

# Define about page route
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
