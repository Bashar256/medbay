from website.models import Patient, User, Medical_Staff, Management_Staff, Hospital, Appointment_Times
from werkzeug.security import check_password_hash, generate_password_hash
from website import db, app, mail, BAD_LOGINS_LIMIT
from website.functions import  search_user_by_email, encrypt_email
from flask_login import current_user
from flask import flash, url_for
from flask_mail import Message
import datetime
import string
import random


def validate_login(request):
    if request.mimetype=='application/json':
        data=request.json
        email = data['email']
        password = data['password']
    else:
        email = request.form.get('email')
        password = request.form.get('password')

    user = search_user_by_email(email)
    if user:
        if datetime.datetime.now() >= (user.last_login_attempt + datetime.timedelta(minutes=5)):
            user.block_login = False
            user.last_login_attempt = datetime.datetime.now()
            user.bad_logins = 0

        if user.block_login:
            flash("Please wait for the 5 min block to end", category="warning")
            return 

        if check_password_hash(user.password, password):
            flash('Logged in successfully!', category='login')
            return user

        if datetime.datetime.now() < (user.last_login_attempt + datetime.timedelta(minutes=5)):
            user.last_login_attempt = datetime.datetime.now()
            user.bad_logins = user.bad_logins + 1

        if user.bad_logins >= BAD_LOGINS_LIMIT:
            flash("To many bad attempts access will be blocked for 5 mins", category="warning")
            user.block_login = True
            user.bad_logins = 0
            
        db.session.commit()
    flash('Invalid Information', category='error')
    return 


def validate_patient_register(request):
    email = request.form.get('email')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    gender = request.form.get('gender')
    phone_no = request.form.get('phone_no')
    dob = request.form.get('dob')

    patient = search_user_by_email(email)

    if patient:
        flash('Email already exists.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif len(last_name) < 2:
        flash('Last name must be greater than 1 character.', category='error')
    elif password1 != password2:
        flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
        flash('Password must be at least 7 characters.', category='error')
    elif len(phone_no) != 13:
        flash("Enter a correct phone number format", category="error")
    else:
        return Patient(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    return 


def validate_staff_register(request):
    email = request.form.get('email')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    gender = request.form.get('gender')
    phone_no = request.form.get('phone_no')
    dob = request.form.get('dob')
    role = request.form.get('role')
    department = request.form.get('department')
    appointment_times_id = request.form.get('appointment_times')
    dpt_head = request.form.get('dpt_head')
    hospital_id = request.form.get('hospital_id')
    appointment_time = Appointment_Times.query.filter_by(id=appointment_times_id).first()
    staff = search_user_by_email(email)
    password = create_random_password()

    if staff:
        flash('Email already exists.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif len(last_name) < 2:
        flash('Last name must be greater than 1 character.', category='error')
    elif len(phone_no) != 13:
        flash("Enter a correct phone number format", category="error")
    else:
        if role.lower() == "ms":
            if hospital_id:
                if Hospital.query.filter_by(id=hospital_id).first():
                    new_user = Management_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=hospital_id, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
                else:
                    flash("Please specify an existing hospital", category="error")
                    return False
            else:
                new_user = Management_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
        elif role.lower() == 'md':
            if dpt_head.lower() == 'false':
                department_head = False
            elif dpt_head.lower() == 'true':
                department_head = True
            else:
                flash("Please specify if the doctor is a department head", category="error")
                return False
            if appointment_time:
                new_user = Medical_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, department=department, appointment_times=appointment_times_id, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), department_head=department_head, last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
                appointment_time.medical_staff.append(new_user)
            else:
                flash("Please Specify times for this doctor", category="error")
                return False
        elif role.lower() == "a":
            new_user = User(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
        else:
            flash("Please Submit from the correct form and Specify role", category="error")
            return False
        db.session.add(new_user)
        db.session.commit()
        new_staff_welcome_email(new_user, email, password)
        return True
    return False


def new_staff_welcome_email(user, email, password):
    token = user.get_token()
    msg = Message('Welcome To The Team',
                sender=("MedBay Support", "noreply@medbay.org"),
                recipients=[email ,"bashar.n.bader@gmail.com"])
    msg.body = f'''Welcome to our humble abode.
    Your credentials are:
    Email: {email}
    Password: {password}
    We strongly recommend that you change your randomly generated password.
    To change your password please follow the link below:
    {url_for('auth_view.reset_token_view', token=token, _external=True)}'''
    with app.app_context():
        mail.send(msg)
    return

def create_random_password():
    all_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ""
    for _ in range(12):
        password += random.choice(all_chars)
    return password