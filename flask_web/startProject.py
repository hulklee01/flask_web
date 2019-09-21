from __future__ import with_statement
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from contextlib import closing


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , startProject.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'startProject.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select password from user where user_id=?', [request.form['username']])
        pw = cur.fetchone()
        print pw[0]
        if request.form['password'] != pw[0]:
            error = 'Invalid username'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


# Add ID dup check
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = g.db.execute('select user_id from user where user_id=?', [username])
        # print cur.fetchone()
        if cur.fetchone() is not None:
            print "Duplicated ID"
            return redirect(url_for('duplicateid'))
        print "Create User"
        g.db.execute('insert into user (user_id, password) values (?, ?)', [username, password])
        g.db.commit()
        return redirect(url_for('login'))

    return render_template('add_user.html')


@app.route('/dupid', methods=['GET'])
def duplicateid():
    return render_template('duplicate_id.html')


@app.route('/search', methods=['POST'])
def search():
    pass


if __name__ == '__main__':
    app.run()

