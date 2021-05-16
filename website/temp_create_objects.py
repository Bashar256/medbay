from website.models import Hospital,Department,Appointment,User,Patient,Medical_Staff,Management_Staff,Patients, Appointment_Times,Time_Slot
from website.functions import html_date_to_python_date, string_to_bytes, encrypt_email
from werkzeug.security import generate_password_hash
from website import db
import datetime

def create_stuff():
    today = datetime.datetime.today()
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

    new_patient = User(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='a', registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()

    email = 'management@gmail.com'
    first_name = 'management'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Management_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='ms', hospital=1, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()


    new_patient1 =  Appointment_Times(start=datetime.datetime(1,1,1,7,0), end=datetime.datetime(1,1,1,15,0), hospital=1)
    db.session.add(new_patient1)
    db.session.commit()


    new_patient2 =  Appointment_Times(start=datetime.datetime(1,1,1,9,0), end=datetime.datetime(1,1,1,17,0), hospital=1)
    db.session.add(new_patient2)
    db.session.commit()

    new_patient3 =  Appointment_Times(start=datetime.datetime(1,1,1,11,0), end=datetime.datetime(1,1,1,19,0), hospital=1)
    db.session.add(new_patient3)
    db.session.commit()



    email = 'doctor1@gmail.com'
    first_name = 'doctor1'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    medical_staff = Medical_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='md', hospital=1, department=1, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(medical_staff)
    medical_staff.appointment_times = new_patient1.id
    new_patient1.medical_staff.append(medical_staff)
    db.session.commit()


    email = 'doctor2@gmail.com'
    first_name = 'doctor2'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Medical_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='md', hospital=1, department=2, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    new_patient.appointment_times = new_patient2.id
    new_patient2.medical_staff.append(new_patient)
    db.session.commit()



    email = 'doctor3@gmail.com'
    first_name = 'doctor3'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Medical_Staff(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='md', hospital=1, department=2, registered_on=datetime.datetime.now(), confirmed=True, confirmed_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    new_patient.appointment_times = new_patient2.id
    new_patient2.medical_staff.append(new_patient)
    db.session.commit()

    email = 'patient1@gmail.com'
    first_name = 'patient1'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'M'
    phone_no = '+962111111111'
    dob = '1999-01-01'

    new_patient = Patient(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()
    new_patient.create_patient_file()
    db.session.commit()

    appointment_times = Appointment_Times.query.filter_by(id=1).first()
    appointment_times.create_slots(date=html_date_to_python_date("2021-4-20"))
    time_slot = db.session.query(Time_Slot).filter_by(id=3).first()
    new_appointment = Appointment(appointment_date_time=datetime.datetime(2021, 4, 20,5,30), hospital=1, department=1, medical_staff=3, patient=6)
    medical_staff.patients.append(new_patient)
    db.session.execute(Patients.insert(), params={"patient_id":6, "medical_staff_id":3, "timeout":datetime.datetime(2021, 4, 20,5,30) + datetime.timedelta(days=50) })            
    temp_slot = time_slot
    db.session.query(Time_Slot).filter_by(id=time_slot[0]).delete()
    db.session.add(new_appointment)
    db.session.commit()
    db.session.execute(Time_Slot.insert(), params={"id": temp_slot[0], "appointment_time_id":temp_slot[1], "start":temp_slot[2], "end":temp_slot[3], "date":temp_slot[4], "appointment_id":new_appointment.id, "taken":True})
    db.session.commit()



    email = 'patient2@gmail.com'
    first_name = 'patient2'
    last_name = 'user'
    password1 = 'pass1234'
    gender = 'F'
    phone_no = '+962111111111'
    dob = '2000-01-01'

    new_patient = Patient(email=encrypt_email(email), first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, date_of_birth=dob, role='p', registered_on=datetime.datetime.now(), last_login=datetime.datetime.now(), last_login_attempt=datetime.datetime.now())
    db.session.add(new_patient)
    db.session.commit()
    new_patient.create_patient_file()
    db.session.commit()

def html_date_to_python_date(date, time=None):
    date = date.split('-')
    if time:
        time = time.split(':')
        return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]))
    return datetime.datetime(int(date[0]), int(date[1]), int(date[2])) 
