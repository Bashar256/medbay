from flask import Blueprint, redirect, url_for, render_template, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from website.validate import validate_patient_register, validate_login
from werkzeug.security import generate_password_hash
from website import db, mail, app, SESSION_TIMEOUT
from website.users import load_user_request
from website.models import User, Patient
from flask_mail import Message
from threading import Thread
import datetime
auth_view = Blueprint("auth_view", __name__, static_folder="static", template_folder="templates")



@auth_view.route("/login", methods=["POST", "GET"])
def login_view():
    if request.method == 'POST':
        user = validate_login(request)
        if user:
            login_user(user, remember=True)
            user.last_login = datetime.datetime.now()
            user.last_login_attempt = datetime.datetime.now()
            user.bad_logins = 0
            db.session.commit()
            if request.mimetype=='application/json':
                return jsonify({'status':'Login Successful!','role':user.role})
            return redirect(url_for('user_view.home_view'))
        elif request.mimetype=='application/json':
            return jsonify({'status':'Incorrect email or password.'})
    
    return render_template("login.html")



#Logout View
@auth_view.route("/logout",methods=["POST", "GET"])
@login_required
def logout_view():
    if request.mimetype == 'application/json':
        if load_user_request(request):
            logout_user()
            return jsonify({'status':'Logged out sucessfully!'})
    flash("Logged out successefully!", "logout")
    logout_user()
    return redirect(url_for('auth_view.login_view'))



#Registration View
@auth_view.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == 'POST':
        # if request.mimetype=='application/json':
        #     status=validate_patient_register_phone(request)
        #     return jsonify({'status':status})
        new_patient = validate_patient_register(request) 
        if new_patient:
            new_patient.create_patient_file()
            db.session.add(new_patient)
            db.session.commit()
            login_user(new_patient, remember=True, duration=SESSION_TIMEOUT)
            confirm_email(new_patient)
            flash('Account created successfully !', category='register')
            return redirect(url_for('user_view.home_view'))
        return render_template("register.html")
    return render_template("register.html")

@auth_view.route("/register_phone", methods=["POST", "GET"])
def register_view_phone():
    if request.mimetype=='application/json':
        data=request.json
        email = data['email']
        first_name = data['firstname']
        last_name = data['lastname']
        password1 = data['password1']
        password2 = data['password2']
        gender = data['gender']
        phone_no = data['phone_no']
        dob = data['dob']

        patient = Patient.query.filter_by(email=email).first()
        
        if patient:
            status='Email already exists.'
        elif len(email) < 4:
            status='Email must be greater than 3 characters.'
        elif len(first_name) < 2:
            status='First name must be greater than 1 character.'
        elif len(last_name) < 2:
            status='Last name must be greater than 1 character.'
        elif password1 != password2:
            status='Passwords don\'t match.'
        elif len(password1) < 7:
            status='Password must be at least 7 characters.'
        elif len(phone_no) != 13:
            status='Enter a correct phone number format'
        else:
            status='Success'
            
        if status=='Success':
            new_patient =  Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
            new_patient.create_patient_file()
            db.session.add(new_patient)
            db.session.commit()
            login_user(new_patient, remember=True, duration=SESSION_TIMEOUT)
            confirm_email(new_patient)
        return jsonify({'status':status})



#Password_Reset View
@auth_view.route("/reset_password", methods=["POST", "GET"])
def reset_password_view():
    if request.method == "POST":
        if request.mimetype=='application/json':
            data=request.json
            email = data['email']
        else:
            email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_token()
            msg = Message('Password Reset Request',
                        sender=("MedBay Support", "noreply@medbay.org"),
                        recipients=[user.email])
            msg.body = f'''To change your password please follow the link below:
            {url_for('auth_view.reset_token_view', token=token, _external=True)}'''
            Thread(target=send_email, args=[msg]).start()
            if request.mimetype=='application/json':
                return jsonify({'status':'An Email was sent with the reset link'})
            flash("An Email was sent with the reset link", category="info")
            return redirect(url_for("auth_view.reset_password_view")) 
             
        if request.mimetype=='application/json':
                return jsonify({'status':'No such email'})
        flash("No such email", category="error")
        return redirect(url_for("auth_view.reset_password_view"))
    return render_template("reset_password.html")


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
                return redirect(url_for('auth_view.login_view'))
            else:
                flash('Passwords must match', category='error')
                return render_template("reset_token.html")
        flash('That is an invalid or expired token', category='warning')
        return redirect(url_for('auth_view.reset_password_view'))
    return render_template('reset_token.html')


#Sending_Confirmation_Email View
@auth_view.route('/confirm_email')
@login_required
def email_confirmation_View():
    confirm_email(current_user)
    if request.mimetype=='application/json':
        return jsonify({'status':'A confirmation email was sent to you.'})
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
                recipients=[user.email])
    msg.body = f'''To confirm your email please follow the link below:
    {url_for('auth_view.verify_email_view', token=token, _external=True)}'''
    Thread(target=send_email, args=[msg]).start()


#Sending_Email Function
def send_email(msg):
    with app.app_context():
        mail.send(msg)
