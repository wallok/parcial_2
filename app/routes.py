from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, SignUpForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts=current_user.posts.paginate(1,5,False).items
    return render_template("index.html",posts=posts, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        #POST
        #Iniciar sesión con base de datos
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("No se encontro el usuario o la contraseña esta incorrecta")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        flash("Iniciaste Sesión correctamente, Hola {}".format(form.username.data))
        return redirect("/index")
    return render_template("login.html", title="Login",form=form)

@app.route("/index/delete/<int:id>", methods=["POST"])
@login_required
def delete_note(id):
    post= Post.query.filter_by(id=id).first()
    if post:
        if current_user.id==post.users_id:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for("index"))
        else:
            return redirect(url_for("404"))
    else:
        flash("la nota no existe")
    return redirect(url_for("index"))


@app.route("/index/see/<int:id>", methods=["POST"])
@login_required
def see_note(id):
    post= Post.query.filter_by(id=id).first()
    return render_template("post.html",post=post)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(form)
        if user is None:
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Usuario creado exitosamente")

        else:
            flash("El usuario ya existe")
            return redirect(url_for("signup"))
        
        
        return redirect("/index")
    return render_template("signup.html", title="Signup",form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
