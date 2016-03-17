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


@app.route('/register')
def register():
    return render_template('register_page.html')


@app.route('/')
def main():
    if session.get('logged_in'):
        cur = get_db().cursor()

        activities_ids = query_db(
            'SELECT ActivityID FROM FaveActivities WHERE UserID=\'{}\''.format(session.get('user_id')))

        activities_names = [
            query_db('SELECT Name from Activities WHERE ID=\'{}\''.format(current_activity_id[0]), one=True)[0] for
            current_activity_id in activities_ids]

        user_preferences_string = ''
        if request.method == 'POST':
            user_preferences_string = 'ActivityID = \'{}\''.format()
        else:
            user_preferences_strings = []
            for preference in activities_ids:
                user_preferences_strings.append('ActivityID = \'{}\''.format(preference[0]))
            user_preferences_string = ' OR '.join(user_preferences_strings)

        events = query_db('SELECT * FROM Events WHERE ' + user_preferences_string)

        events_data = []

        events_ids = [event[0] for event in events]
        for i in range(len(events)):
            current_users_ids = [c[0] for c in query_db(
                'SELECT UserID FROM Registrations WHERE EventID=\'{}\''.format(events_ids[i]))]
            current_users = []
            for current_user_id in current_users_ids:
                current_users.append(
                    query_db('SELECT UserName from Users WHERE ID=\'{}\''.format(current_user_id), one=True)[0])

            city_name = query_db('SELECT Name from Cities WHERE ID=\'{}\''.format(events[i][1]), one=True)[0]
            specific_location = events[i][2]
            date = events[i][3]
            max_registers = events[i][4]
            activity = query_db('SELECT Name from Activities WHERE ID=\'{}\''.format(events[i][5]), one=True)[0]

            events_data.append((city_name, specific_location, date, max_registers, activity, current_users))

        return render_template('main.html', events_data=events_data, activities_names=activities_names)
    else:
        return redirect(url_for('login_page'))


@app.route('/register_success', methods=['POST'])
def register_success_handler():
    name = '\'' + request.form['Name'] + '\''
    user_name = '\'' + request.form['Username'] + '\''
    password = '\'' + request.form['Password'] + '\''
    date_of_birth = '\'' + request.form['date_of_birth'] + '\''
    gender = '\'' + request.form['Gender'] + '\''
    email = '\'' + request.form['email'] + '\''
    phone = '\'' + request.form['Phone Number'] + '\''
    city = '\'' + request.form['favourite_cities'] + '\''
    args = ','.join([name, user_name, password, date_of_birth, gender, email, phone])
    query = 'INSERT INTO Users (Name, UserName, Password, Age, Gender, Email, Phone) VALUES ({})'.format(args)
    query_db2(query)
    select_user_query = 'SELECT * FROM Users WHERE UserName={}'.format(user_name)
    user_id = query_db(select_user_query)[0][0]
    insert_city(city, user_id)
    insert_activity('1', user_id) if request.form.get('running') == 'on'else None  # should return 'on'
    insert_activity('2', user_id) if request.form.get('walking') == 'on' else None
    insert_activity('3', user_id) if request.form.get('basketball') == 'on' else None
    insert_activity('4', user_id) if request.form.get('soccer') == 'on' else None
    insert_activity('5', user_id) if request.form.get('tennis') == 'on' else None
    insert_activity('6', user_id) if request.form.get('gym') == 'on' else None
    return render_template('register_success.html')


def insert_activity(activity_id, user_id):
    args = ','.join([str(user_id), activity_id])
    query = 'INSERT INTO FaveActivities (UserID, ActivityID) VALUES ({})'.format(args)
    query_db2(query)


def insert_city(city_id, user_id):
    args = ','.join([str(user_id), str(city_id)])
    query = 'INSERT INTO RelevantCities (UserID, CityID) VALUES ({})'.format(args)
    query_db2(query)


def query_db2(query, args=(), one=False):
    db = get_db()
    db.execute(query, args)
    db.commit()


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
            session['username'] = request.form['username']
            session['user_id'] = \
                query_db('SELECT ID FROM Users WHERE UserName=\'{}\''.format(request.form['username']), one=True)[0]
            return redirect(url_for('main'))
    return render_template('login_page.html', error=error)


@app.route('/profile')
def profile():
    if session.get('logged_in'):
        # Get username from session
        username = session.get('username')
        user = query_db('SELECT * FROM Users WHERE UserName=\"{}\"'.format(username))
        sports_ids = query_db('SELECT * FROM FaveActivities WHERE UserID=\"{}\"'.format(user[0][0]))
        activities = []
        for id in sports_ids:
            # Get the activities names according to their ids.
            activities.append(query_db('SELECT Name FROM Activities WHERE ID=\'{}\''.format(id[2]))[0][0])
        return render_template('profile.html', user=user, activities=activities)
    else:
        return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))


@app.route('/createEvent')
def create_event():
    # if session.get('logged_in'):
    return render_template('create_event.html')
    # else:
    #     return redirect(url_for('login_page'))


@app.route('/event_success', methods=['POST'])
def event_success():
    if session.get('logged_in'):
        # Create the event
        activity = '\'' + request.form['activity'] + '\''
        city_id = '\'' + request.form['city'] + '\''
        location = '\'' + request.form['location'] + '\''
        date = '\'' + request.form['date'] + '\''
        time = '\'' + request.form['time'] + '\''
        max_part = '\'' + request.form['max_part'] + '\''
        user_id = session.get('user_id')

        return render_template('event_success.html')

        #args = ','.join([city_id, location, ])
    else:
        return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.config.from_object(__name__)
    app.run()
