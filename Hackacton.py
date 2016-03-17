from flask import Flask, render_template, session, redirect, url_for, request, g
import sqlite3

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('Sportner.db')
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def main():
    if session.get('logged_in'):
        return render_template('main.html')
    else:
        return redirect(url_for('login_page'))

@app.route('/register_success', methods=['POST'])
def register_success_handler():
    name  = '\'' + request.form['Name'] + '\''
    user_name ='\'' + request.form['Username'] + '\''
    password = '\'' + request.form['Password'] + '\''
    date_of_birth = '\'' + request.form['date_of_birth'] + '\''
    gender = '\'' + request.form['Gender'] + '\''
    email = '\'' + request.form['email'] + '\''
    phone = '\'' + request.form['Phone Number'] + '\''
    args = ','.join([name, user_name, password, date_of_birth, gender,email, phone])
    query = 'INSERT INTO Users (Name, UserName, Password, Age, Gender, Email, Phone) VALUES ({})'.format(args)
    query_db2(query)
    return render_template('register_success.html')


@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if session.get('logged_in'):
        return redirect(url_for('main'))

    # error = None
    # cur = get_db().cursor()
    # error = ''
    # for user in query_db('select * from Cities'):
    #     error += '{}: <h1>{}</h1> <br/>'.format(user[0], user[1])
    # if request.method == 'POST':
    # if request.form['username'] != app.config['USERNAME']:
    #     error = 'Invalid username'
    # elif request.form['password'] != app.config['PASSWORD']:
    #     error = 'Invalid password'
    # else:
    #     session['logged_in'] = True
    #     # flash('You were logged in')
    #     return redirect(url_for('main'))
    return render_template('login_page.html')


@app.route('/profile')
def profile():
    # TODO Get username from session
    user = query_db('SELECT * FROM Users WHERE UserName=\"max\"')
    sports_ids = query_db('SELECT * FROM FaveActivities WHERE UserID=\"1\"')
    activities = []
    for id in sports_ids:
        # Get the activities names according to their ids.
        activities.append(query_db('SELECT Name FROM Activities WHERE ID=\'{}\''.format(id[2]))[0][0])
    return render_template('profile.html', user=user, activities=activities)


if __name__ == '__main__':
    app.run()
