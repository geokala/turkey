from turkey.models import User
from turkey import app
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from flask import request, render_template, redirect, url_for, flash, abort
from wtforms import Form, TextField, PasswordField, validators
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
import hmac


login_manager = LoginManager(app)
login_manager.login_view = 'login'


class LoginForm(Form):
    username = TextField(
        'Username',
        [
            validators.Length(max=64),
            validators.Required()
        ],
    )
    password = PasswordField(
        'Password',
        [
            validators.Required(),
        ],
    )


class RegisterForm(Form):
    username = TextField(
        'Username',
        [
            validators.Length(max=64),
            validators.Required(),
        ],
    )
    password = PasswordField(
        'Password',
        [
            validators.Required(),
            validators.EqualTo('password_confirm',
                               message='Passwords must match.'),
        ],
    )
    password_confirm = PasswordField('Confirm Password')
    email = TextField(
        'E-mail',
        [
            validators.Length(max=255),
            validators.Email(),
            validators.Required(),
            validators.EqualTo('email_confirm',
                               message='E-mail addresses must match.'),
        ],
    )
    email_confirm = TextField('Confirm E-mail')


def secure_redirect(next, digest, fallback):
    try:
        if hmac.compare_digest(generate_hmac(next), digest):
            return next
    except:
        pass
    return fallback


def generate_hmac(message):
    return hmac.new(
        bytes(app.config["SECRET_KEY"], "utf8"),
        bytes(message, "utf8"), "sha256"
    ).hexdigest()


def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User.query.filter(
                or_(User.name == form.username.data,
                    User.email == form.username.data)
            ).one()
        except NoResultFound:
            # The user does not exist
            user = None
        if user and user.validate_password(form.password.data):
            # The user exists and the password is valid
            login_user(user)
            flash('Welcome back, %s!' % user.name, 'success')
            # TODO: We need to make sure that 'next' points to something on our
            # site to avoid malicious redirects
            return redirect(
                secure_redirect(
                    request.args.get('next'),
                    request.args.get('hmac'),
                    url_for('home'),
                )
            )
        else:
            flash('Login failed!', 'danger')
            return redirect(url_for('login'))
    else:
        return render_template("login.html", form=form)


@login_manager.unauthorized_handler
def unauthorized():
    if not login_view:
        abort(401)

    if login_manager.login_message:
        if login_manager.localize_callback is not None:
            flash(login_manager.localize_callback(login_manager.login_message),
                  category=login_manager.login_message_category)
        else:
            flash(
                login_manager.login_message,
                category=login_manager.login_message_category
            )

    return redirect(url_for(
        login_manager.login_view,
        next=request.url,
        hmac=generate_hmac(request.url)
    ))


@login_manager.needs_refresh_handler
def needs_refresh():
    if not login_manager.refresh_view:
        abort(403)

    if login_manager.localize_callback is not None:
        flash(
            login_manager.localize_callback(
                login_manager.needs_refresh_message
            ),
            category=login_manager.needs_refresh_message_category,
        )
    else:
        flash(login_manager.needs_refresh_message,
              category=login_manager.needs_refresh_message_category)

    return redirect(url_for(
        login_manager.login_view,
        next=request.url,
        hmac=generate_hmac(request.url)
    ))


def logout_view():
    logout_user()
    # TODO: We need to make sure that 'next' points to something on our
    # site to avoid malicious redirects
    return redirect(
        secure_redirect(
            request.args.get('next'),
            request.args.get('hmac'),
            url_for('home'),
        )
    )


def register_view():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        new_user = User.create(
            name=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        print(new_user)

        if new_user is None:
            # TODO: Put the error on the form validation instead
            # TODO: Make this still give a message afterwards, but link it to
            # the forgotten email password reset thing?
            user_exists_message = ' '.join([
                'A user called %s already exists!',
                'Please select a different username.',
            ]) % form.username.data
            flash(user_exists_message, 'danger')
            return redirect(url_for('register'))
        else:
            login_user(new_user)
            flash('Welcome to the Turkey, %s!' % form.username.data,
                  'success')
            validation_message = ' '.join([
                'Your email account %s will receive a validation mail.',
                'Please click the link in that mail to validate your mail.',
            ]) % form.email.data
            flash(validation_message, 'info')
            # TODO: Redirect to /me (current user's account page)?
            return redirect(url_for('home'))
    else:
        return render_template("register.html", form=form)


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)


@login_required
def my_account_view():
    try:
        User.query.filter(User.name == current_user.name).one()
        return render_template("me.html", user=current_user)
    except NoResultFound:
        # The user does not exist, this should not happen
        flash(
            'Error accessing your account page. Please try logging in again.',
            'danger'
        )
        return redirect(url_for('home'))
