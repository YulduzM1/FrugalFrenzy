import csv
import pandas as pd
import requests
import json
from flask import Flask, render_template, request

app = Flask(__name__)

url = 'http://api.nessieisreal.com/enterprise/accounts?key=3ae6e71b194eff8c8c1cb81093705a6d'

# fetch the account data from the API and save it to a CSV file
response = requests.get(url)
data = response.json()

with open('accounts.json', 'w') as outfile:
    json.dump(data, outfile)

# Define home page route
@app.route('/')
def index():
    return render_template('index.html', account_found=False)

# Define login route to handle form submission
@app.route('/login', methods=['POST'])
def login():
    customer_id = request.form['customer_id']
    account_found = False
    with open('accounts.json', 'r') as json_file:
        data = json.load(json_file)
        for row in data['results']:
            if row['customer_id'] == customer_id:
                account_found = True
                break

    if account_found:
        return render_template('Home.html', customer_id=customer_id)
    else:
        return render_template('index.html', account_found=False, customer_id=customer_id)




if __name__ == '__main__':
    app.run(debug=True)