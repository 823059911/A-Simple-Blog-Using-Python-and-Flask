from distutils.log import debug 
from flask import Flask, render_template, request, redirect, url_for 
from flask_login import UserMixin, login_user,login_required, logout_user, current_user 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import login_user, logout_user, login_required, LoginManager 
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime 
from flask import flash 


app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app) 
login_manager = LoginManager() 
login_manager.init_app(app) 
login_manager.login_view = 'login'


@login_manager.user_loader 
def load_user(user_id): 
	return User.query.get(int(user_id)) 

class GFGBLOG(db.Model): 
	id = db.Column(db.Integer, primary_key=True) 
	title = db.Column(db.String(50)) 
	author = db.Column(db.String(20)) 
	post_date = db.Column(db.DateTime) 
	content = db.Column(db.Text) 

class User(db.Model, UserMixin): 
	id = db.Column(db.Integer, primary_key=True) 
	username = db.Column(db.String(20), nullable=False, unique=True) 
	password = db.Column(db.String(80), nullable=False) 



@app.route("/") 
def hello_world(): 
	article = GFGBLOG.query.order_by(GFGBLOG.post_date.desc()).all() 
	print(current_user.is_anonymous) 
	if current_user.is_anonymous: 
		name = "guest"
	else: 
		name = current_user.username 
		print("bye") 

	return render_template('index.html', article=article, name=name) 


@app.route('/about') 
def about(): 
	return render_template('about.html') 


@app.route('/addpost', methods=['POST', 'GET']) 
def addpost(): 
	if request.method == 'POST': 
		title = request.form['title'] 
		author = request.form['author'] 
		content = request.form['content'] 

		post = GFGBLOG(title=title, author=author, 
					content=content, post_date=datetime.now()) 

		db.session.add(post) 
		db.session.commit() 
		print("Done") 
		return redirect(url_for('hello_world')) 
	return render_template('add.html') 

@app.route('/update/<int:id>', methods=['POST', 'GET']) 
@login_required
def update(id): 
	if request.method == 'POST': 
		title = request.form['title'] 
		author = request.form['author'] 
		content = request.form['content'] 
		print(content) 

		post = GFGBLOG.query.filter_by(id=id).first() 

		post.title = title 
		post.author = author 
		post.content = content 

		db.session.add(post) 
		db.session.commit() 
		return redirect("/") 

	edit = GFGBLOG.query.filter_by(id=id).first() 
	return render_template('update.html', edit=edit) 

@app.route('/delete/<int:id>') 
@login_required
def delete(id): 
	d = GFGBLOG.query.filter_by(id=id).first() 
	db.session.delete(d) 
	db.session.commit() 
	return redirect(url_for('hello_world')) 

@app.route('/login', methods=['POST', 'GET']) 
def login(): 
	if request.method == 'POST': 
		# print("hello") 
		username = request.form['username'] 
		password = request.form['password'] 
		user = User.query.filter_by(username=username).first() 

		if not user and not check_password_hash(user.password, password): 
			flash('Please check your login details and try again.') 
			# return redirect(url_for('auth.login')) 
			return render_template('not.html') 
		else: 
			login_user(user) 
			print("yes") 
			return redirect(url_for('hello_world')) 

	return render_template('login.html') 

@app.route('/signin', methods=['POST', 'GET']) 
def signin(): 
	if request.method == 'POST': 
		print("hello") 
		username = request.form['username'] 
		password = request.form['password'] 
		user = User(username=username, password=password) 
		db.session.add(user) 
		db.session.commit() 
		return redirect(url_for('hello_world')) 

	return render_template('signin.html') 


@app.route('/logout', methods=['GET', 'POST']) 
@login_required
def logout(): 
	logout_user() 
	return redirect(url_for('hello_world')) 

# main driver function 
if __name__ == '__main__': 
	
	# run() method of Flask class runs the application 
	# on the local development server. 
	app.run(debug=True)
