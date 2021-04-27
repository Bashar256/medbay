from flask import Blueprint, Flask, redirect, url_for, render_template, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.models import User, Patient, Management_Staff, Medical_Staff, Hospital, Department, Shift, Appointment,patients
from flask_mail import Message
from threading import Thread
from website import db, mail,app
import os
import datetime
from website.temp_create_objects import create_stuff
from website.validate import validate_patient_register, validate_login


auth_view = Blueprint("auth_view", __name__, static_folder="static", template_folder="templates")

@auth_view.route("/login", methods=["POST", "GET"])
def login():

    if request.method == 'POST':
        if validate_login(request):
            return redirect(url_for('user_view.home'))
                
        flash('Invalid Information', category='error')

    return render_template("login.html")

@auth_view.route("/logout")
@login_required
def logout():
    flash("Logged out successefully!", "success")
    logout_user()
    return redirect(url_for('auth_view.login'))


@auth_view.route("/reset password", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_token()
            msg = Message('Password Reset Request',
                        sender=("MedBay Support", "noreply@medbay.org"),
                        recipients=["dgkxsktjectbd@nucleant.org"])
            msg.body = f'''To change your password please follow the link below:
            {url_for('auth_view.reset_token', token=token, _external=True)}'''
            Thread(target=send_email, args=[msg]).start()
            flash("An Email was sent with the reset link", category="success")
            return redirect(url_for("auth_view.reset_password"))  

        flash("No such email", category="error")
        return redirect(url_for("auth_view.reset_password"))
    return render_template("reset password.html")


@auth_view.route("/reset password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if request.method == "POST":
        user = User.verify_token(token)
        if user:
            password = request.form.get("password1")
            confirm_password = request.form.get("password2")
            if password == confirm_password:
                hashed_password = generate_password_hash(password)
                user.password = hashed_password
                db.session.commit()
                flash('Your password has been updated! You are now able to log in', category='success')
                return redirect(url_for('auth_view.login'))
            else:
                flash('Passwords must match', category='error')
                return render_template("reset token.html")
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('auth_view.reset_password'))
    return render_template('reset token.html')



@auth_view.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':

        if validate_patient_register(request):
            new_patient = Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p')
            new_patient.create_patient_file()
            db.session.add(new_patient)
            db.session.commit()
            login_user(new_patient, remember=True)
            confirm_email(new_patient)
            flash('Account created!', category='success')
            return redirect(url_for('user_view.home'))
        return render_template("register.html")
    #create_stuff()
    return render_template("register.html")


@auth_view.route('/confirm email/<token>')
@login_required
def verify_email(token):
    user = User.verify_token(token)
    if user:
        if not user.confirmed:
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()
            db.session.commit()
            flash('Account Confirmed', category='success')
            return redirect(url_for("user_view.home"))

        flash('Account already confirmed', category='info')
        return redirect(url_for("user_view.home"))

    flash('That is an invalid or expired token', category='warning')
    return redirect(url_for("user_view.home"))


@auth_view.route('/confirm email')
@login_required
def email_confirmation():
    confirm_email(current_user)
    flash("A confirmation email was sent to you.", category="success")
    return redirect(url_for("user_view.profile"))


def confirm_email(user):
    token = user.get_token()
    msg = Message('Email Confirmation',
                sender=("MedBay Support", "noreply@medbay.org"),
                recipients=["sebire3932@hype68.com"])
    msg.body = f'''To confirm your email please follow the link below:
    {url_for('auth_view.verify_email', token=token, _external=True)}'''
    Thread(target=send_email, args=[msg]).start()

def send_email(msg):
    with app.app_context():
        mail.send(msg)