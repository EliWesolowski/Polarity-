from flask import Flask, request, render_template, redirect, session
import requests
import json
from textblob import TextBlob
import matplotlib.pyplot as plt
from twitter_analysis import get_sentiment_data, positive_tweet_ids, negative_tweet_ids, neutral_tweet_ids
import os
import db
import sqlite3


app = Flask(__name__)
app.secret_key = 'sdfsd8f7bs87df6bs8d7f6b8sf'

def fetch_data_from_db(email):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    user_id = cursor.fetchone()
    if user_id:
        session['user_id'] = user_id[0]
    else:
        return redirect('/login')

    cursor.execute("SELECT searchterm FROM saved_reports WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data



@app.route('/')
def home():
    return render_template('templates/home.html')

@app.route('/login')
def login():
    return render_template('templates/login.html')

@app.route('/logup', methods=['POST'])
def logup():
    if request.method != 'POST':
        return "400" #Bad Request

   
    email = request.form['email']
    password = request.form['password']

    # Query the database for a user with the specified email and password
    def validate_user(): 
        connection = sqlite3.connect('mydatabase.db')
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM users where email = '" + email + "' and password = '" + password + "';")
        rows = result.fetchall()
        return len(rows) >= 1 
        
            
    if validate_user() == True:
        return render_template('/templates.bot.html')
    else: 
        return "404" #Not Found 

        
@app.route('/savesearch', methods=['GET', 'POST'])
def savesearch():
     if request.method == 'POST':

        searchterm = session.get('query')
        user_id = session['user_id']
        print(searchterm)
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saved_reports")
        print(cursor.fetchall())
        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()


        cursor.execute("INSERT INTO saved_reports (user_id, searchterm) VALUES (?, ?)", (user_id, searchterm))
        conn.commit()
        return redirect('/savedreports')
    
        
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()


        cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", (first_name, last_name, email, password))
        conn.commit()
        cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)", (first_name, last_name, email, password))


        cursor.execute("SELECT last_insert_rowid()")
        user_id = cursor.fetchone()
        session['user_id'] = user_id[0]
        
        return redirect('/')
        
    else:
        return '''
            <form method="post">
                <input type="text" name="first_name" placeholder="First Name">
                <input type="text" name="last_name" placeholder="Last Name">
                <input type="email" name="email" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <button type="submit">Sign Up</button>
            </form>
        '''

@app.route('/bot', methods=['GET', 'POST'])
def main():
    return render_template('templates/bot.html')

@app.route('/signup')
def signup():
    return render_template('templates/signup.html')

@app.route('/search', methods=['GET', 'POST'])
def search():

    query = request.form['query']
    session['query'] = query
    

    sentiment_data = get_sentiment_data(query)
    

    num_positive = sentiment_data.count('positive')
    num_negative = sentiment_data.count('negative')
    num_neutral = sentiment_data.count('neutral')

    labels = ['Positive Tweets', 'Negative Tweets', 'Neutral Tweets']
    sizes = [num_positive, num_negative, num_neutral]
    colors = ['#ACCBE1','#7C98B3','#536B78','#536B78']
    fig = plt.figure()
    fig.patch.set_facecolor('black')
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    
    file_path = "C:/Users/mweso/OneDrive/Desktop/FlaskTutorial/static/images/plot"
    plt.savefig(file_path)  
    return render_template('templates/search_results.html', query=query, positive_tweet_ids=positive_tweet_ids, negative_tweet_ids=negative_tweet_ids, neutral_tweet_ids=neutral_tweet_ids)
    

    


app.config['DEBUG'] = True

def results():
    return render_template('search_results.html', positive_tweet_ids=positive_tweet_ids, negative_tweet_ids=negative_tweet_ids, neutral_tweet_ids=neutral_tweet_ids)

if __name__ == '__main__':
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    res = cursor.execute("""CREATE TABLE IF NOT EXISTS users
    (user_id int,
    first_name varchar(255),
    last_name varchar(255),
    email varchar(255),
    password varchar(255)) """)


    cursor.execute("""CREATE TABLE IF NOT EXISTS saved_reports
    (user_id int,
    searchterm varchar(255))""")
    

    app.run()
    