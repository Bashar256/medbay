from website import db
from website.models import Hospital,Department,Appointment,User,Patient,Medical_Staff,Management_Staff,patients,Shift,Schedule,Schedules
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
today = datetime.datetime.today().weekday()
def create_stuff():
    
    name = 'Shmeisani hospital'
    new_patient = Hospital(name=name)
    db.session.add(new_patient)
    db.session.commit()


    name = 'Radiology'
    new_patient = Department(name=name, hospital=1)
    db.session.add(new_patient)
    db.session.commit()


    name = 'Oncology'
    new_patient = Department(name=name, hospital=1)
    db.session.add(new_patient)
    db.session.commit()


    email = 'admin@gmail.com'
    first_name = 'admin'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='a', registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()

    email = 'management@gmail.com'
    first_name = 'management'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Management_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='ms', hospital=1, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()

    new_patient = Schedule(hospital=1, name="A")
    db.session.add(new_patient)
    db.session.commit()

    new_patient = Schedule(hospital=1, name="B")
    db.session.add(new_patient)
    db.session.commit()

    start = datetime.time(11,0)
    end = datetime.time(19,0)
    shift = 'Afternoon'

    shift1 = Shift(shift_start=start, shift_end=end, name=shift, hospital=1)
    db.session.add(shift1)
    db.session.commit()

    start = datetime.time(7,0)
    end = datetime.time(15,0)
    shift = 'Morning'

    shift2 = Shift(shift_start=start, shift_end=end, name=shift, hospital=1)
    db.session.add(shift2)
    db.session.commit()

    db.session.execute(Schedules.insert(), params={"shift_id":shift2.id, "schedule_id":2})
    db.session.execute(Schedules.insert(), params={"shift_id":shift2.id, "schedule_id":2})
    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":2})
    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":2})
    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":2})

    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":1})
    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":1})
    db.session.execute(Schedules.insert(), params={"shift_id":shift1.id, "schedule_id":1})
    db.session.execute(Schedules.insert(), params={"shift_id":shift2.id, "schedule_id":1})
    db.session.execute(Schedules.insert(), params={"shift_id":shift2.id, "schedule_id":1})

    db.session.commit()

    email = 'doctor1@gmail.com'
    first_name = 'doctor1'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Medical_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='md', hospital=1, department=1, schedule=2, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    # db.session.execute(doctors_shifts.insert(), params={"shift_id":1, "medical_staff_id":3, "day":datetime.datetime.today()})
    db.session.commit()


    email = 'doctor2@gmail.com'
    first_name = 'doctor2'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Medical_Staff(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='md', hospital=1, department=2, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    # db.session.execute(doctors_shifts.insert(), params={"shift_id":2, "medical_staff_id":4, "day":datetime.datetime.today()})    
    db.session.commit()

    email = 'patient1@gmail.com'
    first_name = 'patient1'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '1999-01-01'

    new_patient = Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.execute(patients.insert(), params={"patient_id":5, "medical_staff_id":3,"timeout":datetime.datetime.today() + datetime.timedelta(days=3)})
    db.session.add(new_patient)
    db.session.commit()
    new_patient.create_patient_file()
    db.session.commit()


    email = 'patient2@gmail.com'
    first_name = 'patient2'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'F'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Patient(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.execute(patients.insert(), params={"patient_id":6, "medical_staff_id":4, "timeout":datetime.datetime.today() + datetime.timedelta(days=1)})
    db.session.add(new_patient)
    db.session.commit()
    new_patient.create_patient_file()
    db.session.commit()

    new_patient =  Appointment(appointment_date_time=datetime.datetime(2021,4,14,1,30), medical_staff=3, patient=5, department=1, hospital=1)
    db.session.add(new_patient)
    db.session.commit()

    new_patient =  Appointment(appointment_date_time=datetime.datetime(2021,4,14,2,30), medical_staff=4, patient=6, department=2, hospital=1)
    db.session.add(new_patient)
    db.session.commit()