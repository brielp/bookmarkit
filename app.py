from flask import Flask, render_template, redirect, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import SignupForm, LoginForm, AddBoardForm, AddPostForm, EditPostForm
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Post, Board
from datetime import date, datetime
from secrets import API_KEY, default_image_url
import requests
import os

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5433/pinterest') or "postgresql://postgres:password@localhost:5433/pinterest"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'VerySecret'
toolbar = DebugToolbarExtension(app)

connect_db(app)


def get_notifications(user_id):
    now = datetime.now()
    user = User.query.get_or_404(user_id);
    board_ids = []
    for board in user.boards:
        board_ids.append(board.id)
    
    posts_due = Post.query.filter(Post.board_id.in_(board_ids), Post.completed == False, Post.complete_by < now).order_by(Post.complete_by).all()
    return posts_due



#Route Setup 
@app.before_request
def add_user_to_g():
    """ If logged in, add current user to global Flask variable """

    if "curr_user" in session:
        g.user = User.query.get(session["curr_user"])
        g.now = datetime.now()

    else:
        g.user = None


# Functions
def do_login(user):
    """ login user into session """

    session["curr_user"] = user.id

def do_logout():
    """ logout user"""

    if "curr_user" in session:
        del session["curr_user"]

def readable_date(list):
        for post in list:
            if post.complete_by:
                post.complete_by = post.complete_by.strftime("%A %b %d, %Y")
        return list

# HOME route

@app.route("/")
def home_page():
    if g.user:
        form = AddBoardForm()
        notifications = get_notifications(g.user.id)
        return render_template("user_home.html", form=form, notifications=notifications)
    else:     
        return render_template('home.html')


# USER Routes

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ Sign up user and save credentials """
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name = form.last_name.data,
                username=form.username.data,
                password=form.password.data
            )

            user_board = Board(title="General", description="A general hodge-podge of articles and ideas")
            user.boards.append(user_board)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("signup.html", form=form)

        do_login(user)
        return redirect("/")
    
    else:
        return render_template('signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user into session and check credentials"""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, password=form.password.data)

        if user:
            do_login(user)
            flash("Suggessfully Logged In.", "success")
            return redirect("/")
        
        flash("Invalid credentials.", "danger")
        
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    """ Log user out of session """
    do_logout()
    return redirect("/")



#BOARD routes

@app.route("/boards/<int:board_id>")
def show_board(board_id):
    """ Show board and posts on board """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = AddPostForm()
    board = Board.query.get_or_404(board_id)
    incomplete_posts = Post.query.filter(Post.board_id == board_id, Post.completed == False).order_by(Post.complete_by).all()
    completed_posts = Post.query.filter(Post.board_id == board_id, Post.completed == True).all()
    dated_posts = readable_date(incomplete_posts)
    notifications = get_notifications(g.user.id)

    return render_template('board.html', board=board, form=form, posts=dated_posts, completed_posts=completed_posts, notifications=notifications)

@app.route("/boards/add", methods=["POST"])
def add_board():
    """ Add new board """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = AddBoardForm(request.form)

    if form.validate_on_submit():
        board = Board(title=form.title.data, description=form.description.data, user_id=g.user.id)
        db.session.add(board)
        db.session.commit()

        return redirect("/")

    else:
        return render_template("user_home.html", form=form)

@app.route("/boards/<int:board_id>/edit", methods=["GET", "POST"])
def edit_board(board_id):
    """ Edit existing board """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    board = Board.query.get_or_404(board_id)
    form = AddBoardForm(obj=board)

    if form.validate_on_submit():
        board.title = form.title.data
        board.description = form.description.data

        db.session.add(board)
        db.session.commit()

        return redirect("/")
    
    else:
        notifications = get_notifications(g.user.id)
        return render_template('edit_board.html', board=board, form=form, notifications=notifications)

@app.route("/boards/<int:board_id>/delete")
def delete_board(board_id):
    """ Delete existing board"""

    board = Board.query.get_or_404(board_id)

    if not g.user or board.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    
    db.session.delete(board)
    db.session.commit()

    return redirect("/")



#POST/BOOKMARK routes

@app.route("/boards/<int:board_id>/posts/add", methods=["POST"])
def add_post(board_id):
    """ Add a post to a board, make request to LinkPreview API """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = AddPostForm(request.form)

    if form.validate_on_submit():
        authdata = {"key": API_KEY, "q": form.url.data}

        resp = requests.get("https://api.linkpreview.net/", params=authdata)

        if resp.status_code != 200:
            print(f"{resp.json()}")
            flash("There was an error while adding this Post. Please try again.", "danger")
            return redirect(f"/boards/{board_id}")

        title = resp.json()["title"]
        description = resp.json()["description"]
        image_url = resp.json()["image"]
        url = resp.json()["url"]
        complete_by = form.complete_by.data
        
        if not title:
            flash("No Title could be found for that URL.", "danger")
            return redirect(f"/boards/{board_id}")
        
        if not image_url:
            image_url = default_image_url

        if not url:
            url = form.url.data

        p1 = Post(title=title, description=description, image_url=image_url, url=url, complete_by=complete_by, board_id=board_id)
        db.session.add(p1)
        db.session.commit()

        return redirect(f"/boards/{board_id}")

    board = Board.query.get_or_404(board_id)
    posts = Post.query.filter_by(board_id=board_id).all()
    dated_posts = readable_date(posts)    

    return render_template('board.html', board=board, form=form, posts=dated_posts)

@app.route("/boards/<int:board_id>/posts/<int:post_id>/toggle_complete")
def toggle_completed(board_id, post_id):
    """ Toggle post completion and save to database """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    post = Post.query.get_or_404(post_id)
    
    if post.completed == True:
        post.completed = False
    else:
        post.completed = True

    db.session.add(post)
    db.session.commit()    

    return redirect(f"/boards/{board_id}")

@app.route("/boards/<int:board_id>/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(board_id, post_id):
    """ Edit or add post due date """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    post = Post.query.get_or_404(post_id)
    form = EditPostForm(obj=post)

    if form.validate_on_submit():
        post.complete_by = form.complete_by.data
        db.session.add(post)
        db.session.commit()

        return redirect(f"/boards/{board_id}")
    
    else:
        notifications = get_notifications(g.user.id)
        return render_template('edit_post.html', form=form, post=post, notifications=notifications)


@app.route("/boards/<int:board_id>/posts/<int:post_id>/delete")
def delete_post(board_id, post_id):
    """ Delete Post """
    board = Board.query.get_or_404(board_id)

    if not g.user or board.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/boards/{board_id}")