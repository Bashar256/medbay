# # Importing Require Module

# from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField, DateField, SelectField
# from wtforms.validators import DataRequired

# # Creating Login Form contains email and password
# class LoginForm(Form):
#     email = StringField("Email", validators=[validators.Length(min=7, max=50), validators.DataRequired(message="Please Enter Your Email")])
#     password = PasswordField("Password", validators=[validators.DataRequired(message="Please Enter Your Password")])

# # Creating Registration Form contains username, name, email, password and confirm password.

# class RegisterForm(Form):
#     first_name = StringField("First Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Enter Your First Name")], render_kw={"placeholder": "First Name"})
#     last_name = StringField("Last Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Enter Your Last Name")], render_kw={"placeholder": "Last Name"})
#     gender = SelectField(u'Gender', choices=[('M', 'Male'), ('F', 'Female')])
#     phone_no = StringField("Phone_No", validators=[validators.Length(13)], render_kw={"value": "+9627"})
#     date_of_birth = DateField("Date Of Birth", validators=[validators.DataRequired(message="Please Enter Your Birthdate")],format='%Y-%M-%D')
#     email = StringField("Email", validators=[validators.Email(message="Please Enter A Valid Email Address")], render_kw={"placeholder": "Email"})
#     password = PasswordField("Password", validators=[
#         validators.DataRequired(message="Please Enter A Password"),
#         validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
#     ], render_kw={"placeholder": "Password"})
#     confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Confirm Your Password")], render_kw={"placeholder": "Confirm Password"})
from werkzeug.security import check_password_hash,generate_password_hash
from website.models import Patient, User,Medical_Staff,Management_Staff
from flask import flash
from flask_login import login_user, current_user
import datetime
from website import db

def validate_login(request):
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        if check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return True
    return False


def validate_patient_register(request):
    email = request.form.get('email')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    gender = request.form.get('gender')
    phone_no = request.form.get('phone_no')
    dob = request.form.get('dob')

    patient = Patient.query.filter_by(email=email).first()

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
        return True
    return False


def validate_staff_register(request):
    email = request.form.get('email')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    gender = request.form.get('gender')
    phone_no = request.form.get('phone_no')
    dob = request.form.get('dob')
    role = request.form.get('role')
    department = request.form.get('department')
    shift = request.form.get('shift')
    submit = request.form.get('submit')

    staff = User.query.filter_by(email=email).first()

    if staff:
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
        print(submit,role)
        if submit == "Create Management Staff" and role.lower() == "ms":
            new_staff = Management_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now())
        elif submit == "Create Medical Staff" and role.lower() == 'md':
            new_staff = Medical_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, department=department, shift=shift, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now())
        else:
            flash("Please Submit fro m the correct form and Specify role", category="error")
            return False
        db.session.add(new_staff)
        db.session.commit()
        return True
    return False