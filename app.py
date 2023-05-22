from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import create_db
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from web_forms import SearchForm, LoginForm, PostForm, UserForm, NamerForm, PasswordForm
from flask_ckeditor import CKEditor


# Create a Flask Instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Add Databas
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password10121012@localhost/our_users'

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Pass Stuff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Admin Paage
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 21:
        return render_template("admin.html")
    else:
        flash("Sorry you must be the admin")
        return redirect(url_for('dashboard'))


# Create Search Fuction
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        # Get data from submitted from
        post.searched = form.searched.data
        # Query the database
        posts = posts.filter(Post.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Post.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)


# Create Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.about_author = request.form['about_author']

        #Check for profle pic
        if request.files['profile_pic']:
            # To Save a File to Database (Achtung auf SQL Incections!)
            name_to_update.profile_pic = request.files['profile_pic']
            # Grab Image Name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Unique Filename with UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # Change to string do save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                flash("User Updated Successfully!")
                our_users = Users.query.order_by(Users.date_added)
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update, our_users=our_users, id=id)
            except:
                flash("Error! Looks like there was a Problem")
                our_users = Users.query.order_by(Users.date_added)
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update, our_users=our_users, id=id)
        else:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html",
                form=form, name_to_update=name_to_update)
    else:
        our_users = Users.query.order_by(Users.date_added)
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update, out_users=our_users, id=id)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check Hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Does Not Exist")
    return render_template("login.html", form=form)


# Create Logout Page
@app.route('/logout', methods= ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have Been Loged Out!")
    return redirect(url_for('login'))



@app.route('/add-post/<int:id>')
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        #post.author = form.author.data
        post.slug = form.slug.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('posts', id=post.id))

    if current_user.id == post.poster.id or current_user.id == 25:
        form.title.data = post.title
        form.content.data = post.content
        #form.author.data = post.author
        form.slug.data = post.slug
        return render_template('edit_post.html', form=form)
    else:
        flash("You are not autorized to edit this post!!!")
        posts = Post.query.order_by(Post.id)
        return render_template("posts.html", id=id, posts=posts)

@app.route('/delete/post/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or current_user.id == 25:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post Deleted Successfully!!!")
            posts = Post.query.order_by(Post.id)
            return render_template("posts.html", id=id, posts=posts)
        except:
            posts = Post.query.order_by(Post.id)
            flash("Uuups something went wrong")
            return render_template("posts.html", posts=posts, id=id)
    else:
        flash("You are not autorized to delete this post!!!")
        posts = Post.query.order_by(Post.id)
        return render_template("posts.html", id=id, posts=posts)
# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Post(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''
        # Add post data to database
        db.session.add(post)
        db.session.commit()
        # Return a Mesage
        flash("Blog Post Submitted Successfully!")

    # Return to webpage
    return  render_template("add_post.html", form=form)

# Blogpost Page
@app.route('/posts')
@login_required
def posts():
    # Grab all the posts from the database
    posts = Post.query.order_by(Post.date_posted)
    return render_template("posts.html", posts=posts)

# JSON Thing
@app.route('/date')
def get_current_date():
    favourite_pizza = {
        "John": "Pepperaoni",
        "Mary": "Cheese",
        "Tim": "Mushroom"
    }
    return favourite_pizza
    #return {"Date": date.today()}


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favourite_color = request.form['favourite_color']
        name_to_update.about_author = request.form['about_author']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update, our_users=our_users, id=id)
        except:
            flash("Error! Looks like there was a Problem")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update, our_users=our_users, id=id)
    else:
        our_users = Users.query.order_by(Users.date_added)
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update, out_users=our_users, id=id)

# Delit Entries
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!!")

            our_users = Users.query.order_by(Users.date_added)
            return render_template("add_user.html",
               form=form, name=name, our_users=our_users, id=id)
        except:
            our_users = Users.query.order_by(Users.date_added)
            flash("Uuups ... Not Deleted!!!")
            return render_template("add_user.html",
               form=form, name=name, our_users=our_users, id=id)
    else:
        flash("Sorry, you can´t that user! ")
        redirect(url_for('dashboard'))


# Create a route decorator
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data,
                         favourite_color=form.favourite_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favourite_color.data = ''
        form.password_hash.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
       form=form, name=name, our_users=our_users)


@app.route('/')
def index():
    first_name = "John"
    stuff = "This is bold text"

    favourite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html",
                           first_name=first_name, stuff=stuff,
                           favourite_pizza=favourite_pizza)


# localhost:5000/user/John
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user_name=name)


# Create Costum Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate From
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup Password by Email
        pw_to_check = Users.query.filter_by(email=email).first()
        #flash("Form Submitted Successfuly")
        # Chack Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        if passed == True:
            flash("Your good to go")
        else:
            flash(f"WTF, are you even  {pw_to_check.name} ?" )

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate From
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfuly")

    return render_template("name.html",
                           name=name,
                           form=form)



# Create a Blog Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key to Link User (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favourite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)

    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff!
    password_hash = db.Column(db.String(128))
    # User Can have Many Posts
    posts = db.relationship('Post', backref='poster')
    profile_pic = db.Column(db.String(255), nullable=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Crate a String
    def __repr__(self):
        return '<Name %r>' % self.name


if __name__=='__main__':
    app.run(debug=True)
