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
import base64
from flask_login import LoginManager

auth_view = Blueprint("auth_view", __name__, static_folder="static", template_folder="templates")


login_manager = LoginManager()
login_manager.login_view = "auth_view.login_view"
login_manager.init_app(app=app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_manager.request_loader
def load_user_request(request):
    api_key = request.headers.get('authorization')
    if api_key:
        
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key).decode('utf-8')
        except TypeError:
            pass
        user = User.query.filter_by(email=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


#Login View
@auth_view.route("/login", methods=["POST", "GET"])
def login_view():
    if request.method == 'POST':
        user = validate_login(request)
        if user:
            login_user(user, remember=True)
            if request.mimetype=='application/json':
                return jsonify({'status':'Login Successful!'})
            return redirect(url_for('user_view.home_view'))
        elif request.mimetype=='application/json':
            return jsonify({'status':'Incorrect email or password.'})
        flash('Invalid Information', category='error')

    return render_template("login.html")

# if request.method == 'POST':
#         if validate_login(request):
#             if request.mimetype=='application/json':
#                 return jsonify({'status':'Login Successful!'})
#             return redirect(url_for('user_view.home_view'))
#         elif request.mimetype=='application/json':
#             return jsonify({'status':'Incorrect email or password.'})
#         flash('Invalid Information', category='error')
        
#     return render_template("login.html") 


#Logout View
@auth_view.route("/logout")
@login_required
def logout_view():
    flash("Logged out successefully!", "logout")
    logout_user()
    return redirect(url_for('auth_view.login_view'))


#Registration View
@auth_view.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == 'POST':
        new_patient = validate_patient_register(request) 
        if new_patient:
            new_patient.create_patient_file()
            db.session.add(new_patient)
            db.session.commit()
            login_user(new_patient, remember=True)
            confirm_email(new_patient)
            flash('Account created successfully !', category='register')
            return redirect(url_for('user_view.home_view'))
        return render_template("register.html")
    #create_stuff()
    return render_template("register.html")


#Password_Reset View
@auth_view.route("/reset_password", methods=["POST", "GET"])
def reset_password_view():
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
            flash("An Email was sent with the reset link", category="info")
            return redirect(url_for("auth_view.reset_password"))  

        flash("No such email", category="error")
        return redirect(url_for("auth_view.reset_password"))
    return render_template("reset password.html")


#Password_Reset_Token View
@auth_view.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token_view(token):
    if request.method == "POST":
        user = User.verify_token(token)
        if user:
            password = request.form.get("password1")
            confirm_password = request.form.get("password2")
            if password == confirm_password:
                hashed_password = generate_password_hash(password)
                user.password = hashed_password
                db.session.commit()
                flash('Your password has been updated! You are now able to log in', category='update')
                return redirect(url_for('auth_view.login'))
            else:
                flash('Passwords must match', category='error')
                return render_template("reset token.html")
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('auth_view.reset_password'))
    return render_template('reset token.html')


#Sending_Confirmation_Email View
@auth_view.route('/confirm_email')
@login_required
def email_confirmation_View():
    confirm_email(current_user)
    flash("A confirmation email was sent to you.", category="info")
    return redirect(url_for("user_view.profile_view"))


#Email_Confirmation_Token View
@auth_view.route('/confirm_email/<token>')
@login_required
def verify_email_view(token):
    user = User.verify_token(token)
    if user:
        if not user.confirmed:
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()
            db.session.commit()
            flash('Account Confirmed', category='success')
            return redirect(url_for("user_view.home_view"))

        flash('Account already confirmed', category='info')
        return redirect(url_for("user_view.home_view"))

    flash('That is an invalid or expired token', category='warning')
    return redirect(url_for("user_view.home_view"))


#Crafting_Confirmation_Email Function
def confirm_email(user):
    token = user.get_token()
    msg = Message('Email Confirmation',
                sender=("MedBay Support", "noreply@medbay.org"),
                recipients=["sebire3932@hype68.com"])
    msg.body = f'''To confirm your email please follow the link below:
    {url_for('auth_view.verify_email', token=token, _external=True)}'''
    Thread(target=send_email, args=[msg]).start()


#Sending_Email Function
def send_email(msg):
    with app.app_context():
        mail.send(msg)