from distutils.debug import DEBUG
import os
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Event, Staff, Customer
app = Flask(__name__)

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='owner',
	PASSWORD='pass',

	SQLALCHEMY_DATABASE_URI = 'sqlite:///catering.db'
))
app.config.from_envvar('CATERING_SETTINGS', silent=True)

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

@app.route('/')
def start():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		user = Staff.query.filter_by(username=request.form['username']).first()
		user2 = Customer.query.filter_by(username=request.form['username']).first()
		if request.form['username'] == app.config['USERNAME']:
			if request.form['password'] == app.config['PASSWORD']:
				session['logged_in'] = True
				return redirect(url_for('show_owner_page'))
		if user is None:
			error = 'Invalid'
		elif not check_password_hash(user.password, request.form['password']):
			error = 'Invalid'
		else:
			session['staff_id'] = user.staff_id
			session['logged_in'] = True
			return redirect(url_for('show_staff_page'))
		if user2 is None:
			error = 'Invalid'
		elif not check_password_hash(user2.password, request.form['password']):
			error = 'Invalid'
		else:
			session['customer_id'] = user2.customer_id
			session['logged_in'] = True
			return redirect(url_for('show_customer_page'))
	return render_template('login.html', error=error)

@app.route('/owner')
def show_owner_page():
    events = Event.query.order_by(Event.event_id.desc()).all()
    return render_template('ownerPage.html', events=events)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('start'))

@app.route('/newStaff', methods=['GET', 'POST'])
def create_new_staff_acc():
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		else:
			db.session.add(Staff(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit()
			flash('Account created successfully')
			return redirect(url_for('login'))
	return render_template('createStaffAccount.html', error=error)

@app.route('/staff')
def show_staff_page():
	events = Event.query.order_by(Event.event_id.desc()).all()
	currStaff = Staff.query.filter_by(staff_id=session['staff_id']).first()
	return render_template('staffPage.html', events=events, currStaff=currStaff)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		else:
			db.session.add(Customer(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit()
			flash('Account created successfully')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/welcome', methods=['GET', 'POST'])
def show_customer_page():
	events = Event.query.order_by(Event.event_id.desc()).all()
	user = Customer.query.filter_by(customer_id=session['customer_id']).first()
	return render_template('customerPage.html', events=events, user=user)

@app.route('/add', methods=['POST'])
def add_event():
	if not session.get('logged_in'):
		abort(401)
	user = Customer.query.filter_by(customer_id=session['customer_id']).first()
	d = request.form['date']
	date = datetime.strptime(d, "%Y-%m-%d").date()
	events = Event.query.order_by(Event.event_id.desc()).all()
	new = Event(request.form['name'], user.customer_id, date)
	for event in events:
		if new.date == event.date.date():
			flash('There is already an event set for that date')
			return redirect(url_for('show_customer_page'))
	db.session.add(new)
	db.session.commit()
	return redirect(url_for('show_customer_page'))

@app.route('/delete/<event>', methods=['GET'])
def delete(event):
	if not session.get('logged_in'):
		abort(401)
	e = Event.query.filter_by(event_name=event).first()
	db.session.delete(e)
	db.session.commit()
	return redirect(url_for('show_customer_page'))

@app.route('/signup/<event>', methods=['GET', 'POST'])
def sign_up(event):
	if not session.get('logged_in'):
		abort(401)
	e = Event.query.filter_by(event_name=event).first()
	currStaff = Staff.query.filter_by(staff_id=session['staff_id']).first()
	currStaff.following.append(e)
	db.session.commit()
	return redirect(url_for('show_staff_page'))
	