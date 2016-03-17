from flask import Flask, render_template, session, redirect, url_for, request, g
import sqlite3

app = Flask(__name__)

SECRET_KEY = 'development key'

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

    error = None
    if request.method == 'POST':
        cur = get_db().cursor()
        password = query_db('SELECT Password FROM Users WHERE UserName=\'{}\''.format(request.form['username']),
                            one=True)

        if password is None:
            error = "No user with such user name"
        elif password[0] != request.form['password']:
            error = "password doesn't match user name"
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))
    return render_template('login_page.html', error=error)


@app.route('/hello')
def hello():
    return render_template('main.html')


if __name__ == '__main__':
    app.config.from_object(__name__)
    app.run()
