import os

from flask import Flask,redirect, render_template, flash, request, session, g, jsonify
from sqlalchemy.exc import IntegrityError
import requests

from SECRETS import API_KEY, SECRET_KEY
from models import db, connect_db, User, Quote, Tag
from forms import SignUpForm, LoginForm, QuoteForm, EditUserForm
CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///quotacove'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get(SECRET_KEY, "it's a secret")

connect_db(app)
with app.app_context():
    db.create_all()



############################################################
# Homepage and user signup/login/logout

@app.before_request
def add_user_to_g():
    """"If user is logged in, add current user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user"""
    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



############################################################
# Homepage, Sign up, and Login routes

@app.route('/')
def homepage():
    """Gets quote of the day"""
    qotd = requests.get('https://favqs.com/api/qotd').json().get('quote')
    
    quotes = (Quote
              .query
              .order_by(Quote.timestamp.desc())
              .limit(100)
              .all())
    
    list_tags = ['Business','Coding', 'Deep', 
                  'Funny', 'Fierce', 'Historical',
                  'Happy', 'Inspirational', 'Kindness',
                  'Men', 'Motivational', 'Over it', 
                  'Scary',  'Sad', 'Women']

    if not Tag.query.all():
        tags = [Tag(name=name) for name in list_tags]
        for tag in tags:

            db.session.add(tag)
            db.session.commit()
        
    return render_template('homepage.html', qotd=qotd, quotes=quotes)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user signup. Creates new user, adds user to database, and redirects them to the homepage."""
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                fav_quote=form.fav_quote.data,
                fav_quote_author=form.fav_quote_author.data,
                img_url=form.img_url.data or User.img_url.default.arg
            )

            db.session.commit()


        except IntegrityError:
            flash("Username already taken", "danger")
            return redirect('/signup')
        
        do_login(user)

        return redirect('/')
        
    return render_template('users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs a user in and redirects them to the homepage."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data,
            password=form.password.data
        )
        
        if user:
            do_login(user)
            flash(f'Welcome back {user.username}!', 'success')
            return redirect('/')
        
        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Logs out a user and redirects them to the homepage."""

    do_logout()

    return redirect('/')



############################################################
# User details and following

@app.route('/users')
def list_users():
    """List user from search bar or all users"""

    search = request.args.get('search')

    if not search:
        users = User.query.all()
        # Serialize the user data and return as JSON
        user_data = [{'id': user.id, 'username': user.username, 'img_url': user.img_url, 'fav_quote': user.fav_quote, 'fav_quote_author': user.fav_quote_author} for user in users]
        return jsonify(user_data)
    else:
        users = User.query.filter(User.username.ilike(f"%{search}%")).all()
        # Serialize the user data and return as JSON
        user_data = [{'id': user.id, 'username': user.username, 'img_url': user.img_url, 'fav_quote': user.fav_quote, 'fav_quote_author': user.fav_quote_author} for user in users]
        return jsonify(user_data)


@app.route('/users/<int:user_id>')
def show_profile(user_id):
    """Show the user their profile"""

    user = User.query.get_or_404(user_id)
    quotes = (Quote
              .query
              .filter(Quote.user_id == user_id)
              .order_by(Quote.timestamp.desc())
              .limit(100)
              .all()
              )

    return render_template('users/profile.html', user=user, quotes=quotes)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edits user and redirects to profile"""

    if not g.user:
        flash("Please Sign up/in.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    form = EditUserForm()

    if form.validate_on_submit():
        try:
            auth = User.authenticate(user.username,
                                     form.password.data)
            
            if not auth:
                flash('Invalid Password', 'danger')
                return redirect(f'/users/edit/{user_id}')
            
            user.username = form.username.data
            user.email = form.email.data
            user.img_url = form.img_url.data or User.img_url.default.arg
            user.fav_quote = form.fav_quote.data
            user.fav_quote_author = form.fav_quote_author.data

            db.session.commit()
            return redirect(f'/users/{user_id}')


        except IntegrityError:
            flash("Username already taken", "danger")
            return redirect(f'/users/edit/{user_id}')

    return render_template('users/edit.html', form=form, user=user)

@app.route('/users/delete', methods=['POST'])
def delete_user():
    """Deletes user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/')


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def toggle_follow_user(follow_id):
    """Follows and unfollow a user"""

    if not g.user:
        flash("Please Sign up/in.", "danger")
        return 'Error'
    
    user = User.query.get_or_404(follow_id)

    if user in g.user.following:
            g.user.following.remove(user)
            db.session.commit()
            return "Unfollowed"
    else:
            g.user.following.append(user)
            db.session.commit()

            return 'Followed'
    
@app.route('/users/<int:user_id>/data')
def get_user_data(user_id):
    """Gets data for a user based on type"""

    user = User.query.get_or_404(user_id)

    data_type = request.args.get('type')

    if data_type == 'followers':
        data = [{'id': follower.id, 'username': follower.username, 'img_url': follower.img_url, 'fav_quote': follower.fav_quote, 'fav_quote_author': follower.fav_quote_author} for follower in user.followers]
    elif data_type == 'following':
        data = [{'id': followed.id, 'username': followed.username, 'img_url': followed.img_url, 'fav_quote': followed.fav_quote, 'fav_quote_author': followed.fav_quote_author} for followed in user.following]
    else:
        return jsonify({'error': 'Invalid data type'})

    return jsonify(data)



############################################################
# Quote and Tags routes        

@app.route('/quotes/new', methods=['GET', 'POST'])
def add_quote():
    """Add quote """

    if not g.user:
        flash("Please Sign up/in.", "danger")
        return redirect("/")
    
    form = QuoteForm()
    tags = Tag.query.all()

    if form.validate_on_submit():
        try:
            tags_ids = request.form.getlist('tags')
            selected_tags = Tag.query.filter(Tag.id.in_(tags_ids)).all()
            quote = Quote(
                text=form.text.data,
                author=form.author.data,
                tags=selected_tags
            )
            g.user.quotes.append(quote)
            
            db.session.commit()
            return redirect(f'/users/{g.user.id}')
        
        except IntegrityError:
            flash("Quote already exist!", 'danger')
            return redirect('/quotes/new')

    return render_template('quotes/make-quote.html', form=form, tags=tags)

@app.route('/quotes/edit/<int:quote_id>', methods=['GET', 'POST'])
def edit_quote(quote_id):
    """Edits quote then redirects to user profile"""

    if not g.user:
        flash("Please Sign up/in.", "danger")
        return redirect("/")
    
    form = QuoteForm()

    quote = Quote.query.get_or_404(quote_id)
    tags = Tag.query.all()

    if form.validate_on_submit():
        try:
            quote.text=form.text.data
            quote.author=form.author.data

            tags_ids = request.form.getlist('tags')
            quote.tags = Tag.query.filter(Tag.id.in_(tags_ids)).all()

            db.session.add(quote)
            db.session.commit()

            return redirect(f'/users/{g.user.id}')
        
        except IntegrityError:
            flash("Quote already exist!", 'danger')
            return redirect('/quotes/new')

    return render_template('quotes/edit-quote.html', form=form, quote=quote, tags=tags)


@app.route('/quotes/save/<int:quote_id>', methods=["POST"])
def toggle_save_quote(quote_id):
    """Saves quote"""
    
    quote = Quote.query.get(quote_id)



    if quote in g.user.saves:
            g.user.saves.remove(quote)
            db.session.commit()

            return jsonify({'status': 'unsave'})
    else:
            g.user.saves.append(quote)
            db.session.commit()

            return jsonify({'status': 'save'})


@app.route('/quotes/delete/<int:quote_id>', methods=['POST'])
def delete_quote(quote_id):
    """Deletes quote"""

    try:
        quote = Quote.query.get_or_404(quote_id)
        db.session.delete(quote)
        db.session.commit()
        return 'Deleted'
    except Exception as e:
        print(f"Error deleting quote: {e}")
        return 'Error'
    
    
@app.route('/tags')
def get_tags():
    """Get all tags"""

    tags=Tag.query.all()
    user_data = [{'id': tag.id, 'name': tag.name} for tag in tags]

    return jsonify(user_data)


@app.route("/tags/<int:tag_id>")
def list_quotes_by_tag(tag_id):
    """Gets all quotes that a specific tag"""

    tag = (Tag.query.get(tag_id))
    quotes = (Quote
            .query
            .filter(Quote.tags.any(id=tag_id))
            .order_by(Quote.timestamp.desc())
            .all())
    
    return render_template('tags/list_quotes.html', quotes=quotes, tag=tag)