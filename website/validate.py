from website.models import Patient, User,Medical_Staff,Management_Staff, Schedule, Shift, Schedules, Hospital
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import current_user,login_user
from flask import flash
from website import db
import datetime


def validate_login(request):
    if request.mimetype=='application/json':
        data=request.json
        email = data['email']
        password = data['password']
    else:
        email = request.form.get('email')
        password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        if check_password_hash(user.password, password):
            flash('Logged in successfully!', category='login')
            return user
    return None


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
        return Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now())
    return 

# def validate_patient_register_phone(request):
#     data=request.json
#     email = data['email']
#     first_name = data['firstname']
#     last_name = data['lastname']
#     password1 = data['password1']
#     password2 = data['password2']
#     gender = data['gender']
#     phone_no = data['phone_no']
#     dob = data['dob']


#     patient = Patient.query.filter_by(email=email).first()
    
#     if patient:
#         status='Email already exists.'
#     elif len(email) < 4:
#         status='Email must be greater than 3 characters.'
#     elif len(first_name) < 2:
#         status='First name must be greater than 1 character.'
#     elif len(last_name) < 2:
#         status='Last name must be greater than 1 character.'
#     elif password1 != password2:
#         status='Passwords don\'t match.'
#     elif len(password1) < 7:
#         status='Password must be at least 7 characters.'
#     elif len(phone_no) != 13:
#         status='Enter a correct phone number format'
#     else:
#         return Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p')
#     return status


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
    schedule = request.form.get('schedule')
    submit = request.form.get('submit')
    dpt_head = request.form.get('dpt_head')
    hospital_id = request.form.get('hospital_id')
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
        if submit == "Create Management Staff" and role.lower() == "ms":
            if hospital_id:
                if Hospital.query.filter_by(id=hospital_id).first():
                    new_user = Management_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=hospital_id, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now())
                else:
                    flash("Please specify an existing hospital", category="error")
                    return False
            else:
                new_user = Management_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now())
        elif submit == "Create Medical Staff" and role.lower() == 'md':
            if dpt_head.lower() == 'false':
                department_head = False
            elif dpt_head.lower() == 'true':
                department_head = True
            else:
                flash("Please specify if the doctor is a department head", category="error")
                return False
            new_user = Medical_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, hospital=current_user.hospital, department=department, schedule=schedule, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), department_head=department_head)
        elif submit == "Create Admin" and role.lower() == "a":
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role=role, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now())
        else:
            flash("Please Submit from the correct form and Specify role", category="error")
            return False
        db.session.add(new_user)
        db.session.commit()
        return True
    return False


def validate_shift_assignment(request):
    shift1 = request.form.get("shift1")
    shift2 = request.form.get("shift2")
    shift3 = request.form.get("shift3")
    shift4 = request.form.get("shift4")
    shift5 = request.form.get("shift5")
    schedule_id = request.form.get("schedule")
    schedule = Schedule.query.filter_by(id=schedule_id).first()

    if schedule:
        try:
            db.session.query(Schedules).filter_by(schedule_id=schedule_id).delete()
        except:
            db.session.rollback() 
        try:
            db.session.execute(Schedules.insert(), params={"shift_id":shift1, "schedule_id":schedule_id})
            db.session.execute(Schedules.insert(), params={"shift_id":shift2, "schedule_id":schedule_id})
            db.session.execute(Schedules.insert(), params={"shift_id":shift3, "schedule_id":schedule_id})
            db.session.execute(Schedules.insert(), params={"shift_id":shift4, "schedule_id":schedule_id})
            db.session.execute(Schedules.insert(), params={"shift_id":shift5, "schedule_id":schedule_id})
            db.session.commit()
            flash("Shifts Assigned to schedule",category='success')
            return 
        except:
            db.session.rollback()
            flash("Undifined Shift",category='error')
            return 

    flash("Shifts not assigned",category='error')
    return 

def create_schedule(request):
    schedule_name = request.form.get("schedule_name")
    if not Schedule.query.filter(Schedule.name==schedule_name, Schedule.hospital==current_user.hospital).first():
        new_schedule = Schedule(name=schedule_name, hospital=current_user.hospital)
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule created successfully', category='success')
        return 
    
    flash('Schedule already exists', category='error')
    return


def change_doctor_schedule(request):
    schedule_id = request.form.get("schedule_id")
    doctor_id = request.form.get("doctor_id")
    doctor = Medical_Staff.query.filter_by(id=doctor_id).first()
    if doctor:
        if doctor.schedule == schedule_id:
            flash("Schedule Already selected", category="info")
            return
        schedule = Schedule.query.filter_by(id=schedule_id).first()
        if schedule:
            doctor_schedule = Schedule.query.filter_by(id=doctor.schedule).first()
            if doctor not in schedule.medical_staff:
                schedule.medical_staff.append(doctor)
            doctor.schedule = schedule_id
            if doctor in doctor_schedule.medical_staff:
                doctor_schedule.medical_staff.remove(doctor)
            flash("Schedule Changed", category="update")
            db.session.commit()
            return

        flash("This schedule doesn't exist", category="error")
        return

    flash("This doctor doesn't exist", category="error")
    return

    flash("No such form", category="error")
    return

def create_shift(request):
    shift_name = request.form.get("shift_name")
    start = request.form.get("shift_start")
    end = request.form.get("shift_end")
    if not Shift.query.filter(Shift.name==shift_name, Shift.hospital==current_user.hospital).first():
        end = end.split(":")
        start = start.split(":")
        shift_start = datetime.time(int(start[0]),int(start[1]))
        shift_end = datetime.time(int(end[0]),int(end[1]))
        new_shift = Shift(name=shift_name, shift_start=shift_start, shift_end=shift_end, hospital=current_user.hospital)
        db.session.add(new_shift)
        db.session.commit()
        flash('Shift created successfully', category='success')
        return

    flash('A shift with the same name already exists', category='error')
    return