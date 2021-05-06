from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime, timedelta
from flask_login import UserMixin
from website import db, app, UPLOAD_DIRECTORY
from time import time
import math
import os

today = datetime.today()

#Hospital Table
class Hospital(db.Model):
    __tablename__ = 'hospital'
    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='', unique=True)
    departments = db.relationship('Department', backref='hospital_department')
    managers = db.relationship('Management_Staff', backref='hospital_managers')
    medical_staff = db.relationship('Medical_Staff', backref='hospital_medical_staff')
    shifts = db.relationship("Shift", backref="hospital_shifts")
    rooms = db.relationship("Room", backref="hospital_rooms")
    beds = db.relationship("Bed", backref="hospital_beds")
    
    def __repr__(self):
        return f"{self.name}"

    def hospital_beds_stats(self,hospital_id):
        total_beds = 0
        available_beds = 0
        if self.id == hospital_id:
            for room in self.rooms:
                total_beds = total_beds + room.max_no_of_beds
                for bed in room.beds:
                    if not bed.occupied:
                        available_beds = available_beds + 1

        return total_beds,available_beds


#Department Table
class Department(db.Model):
    __tablename__ = 'department'
    __table_args__= (
        db.UniqueConstraint(name, hospital)
    )
    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    medical_staff = db.relationship('Medical_Staff', backref='department_medical_staff')
    rooms = db.relationship('Room', backref='department_rooms')

    def __repr__(self):
        return f"{self.name}"

    def department_beds_stats(self,department_id):
        total_beds = 0
        available_beds = 0
        if self.id == department_id:
            for room in self.rooms:
                total_beds = total_beds + room.max_no_of_beds
                for bed in room.beds:
                    if not bed.occupied:
                        available_beds = available_beds + 1
                        
        return total_beds,available_beds


#Appointment Table
class Appointment(db.Model):
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True) 
    appointment_date_time = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(255,collation='NOCASE'), nullable=True)
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    department = db.Column(db.Integer, db.ForeignKey('department.id'))
    medical_staff = db.Column(db.Integer, db.ForeignKey('medical_staff.id'))
    patient = db.Column(db.Integer, db.ForeignKey('patient.id'))
    diagnoses = db.relationship('Diagnosis', backref='appointment_diagnosis')
    lab_results = db.relationship('Lab_Result', backref='appointment_lab_result')
    
    def __repr__(self):
        return f"{self.appointment_date_time}"

    def __gt__(self, other):
        return self.appointment_date_time > other.appointment_date_time


#Schdules-Shifts Many-To-Many relationship Table
Schedules = db.Table('schedules',
    db.Column('schedule_id', db.Integer, db.ForeignKey('schedule.id')),
    db.Column('shift_id', db.Integer, db.ForeignKey('shift.id')),
)  


#Schedule Table
class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__= (
        db.UniqueConstraint(name, hospital)
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20,collation='NOCASE'), nullable=False, default='A')
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    medical_staff = db.relationship('Medical_Staff', backref="schedule_medical_staff")
    shifts = db.relationship('Shift', secondary=Schedules, lazy='subquery', backref=db.backref('medical_staff_shifts', lazy=True))
    # month = db.Column(db.Integer, nullable=False)
    def __gt__(self, other):
        return self.name > other.name


#Shift Table
class Shift(db.Model):
    __tablename__ = 'shift'
    __table_args__= (
        db.UniqueConstraint(name, hospital)
    )
    
    id = db.Column(db.Integer, primary_key=True)
    shift_start = db.Column(db.Time(timezone=True), nullable=False)
    shift_end = db.Column(db.Time(timezone=True), nullable=False)
    name = db.Column(db.String(20,collation='NOCASE'), nullable=False)
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))


#Diagnosis Table
class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'
    
    id = db.Column(db.Integer, primary_key=True) 
    path = db.Column(db.String(255, collation='NOCASE'))
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    appointment = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    medical_staff = db.Column(db.Integer, db.ForeignKey('medical_staff.id'))
    patient = db.Column(db.Integer, db.ForeignKey('patient.id'))


#Lab_Result Table
class Lab_Result(db.Model):
    __tablename__ = 'lab_results'
    
    id = db.Column(db.Integer, primary_key=True) 
    path = db.Column(db.String(255, collation='NOCASE'))
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    appointment = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    medical_staff = db.Column(db.Integer, db.ForeignKey('medical_staff.id'))
    patient = db.Column(db.Integer, db.ForeignKey('patient.id'))


#Room Table
class Room(db.Model):
    __tablename__ = 'room'
    __table_args__= (
        db.UniqueConstraint(room_no, hospital)
    )

    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(15, collation='NOCASE'))
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    department = db.Column(db.Integer, db.ForeignKey('department.id'))
    beds =  db.relationship('Bed', backref='room_beds')
    max_no_of_beds = db.Column(db.Integer, nullable=False, default=4)
    
    def is_full(self):
        count = 0
        for bed in self.beds:
            if bed.occupied:
                count = count + 1
        return count == self.max_no_of_beds

    def room_stats(self, room_id):
        total_beds = 0
        available_beds = 0
        if self.id == room_id:
            total_beds = len(self.beds)
            for bed in self.beds:
                if not bed.occupied:
                    available_beds = available_beds + 1

        return total_beds, available_beds


#Bed Table
class Bed(db.Model):
    __tablename__ = 'bed'
    
    id = db.Column(db.Integer, primary_key=True) 
    room = db.Column(db.Integer, db.ForeignKey('room.id'))
    occupied = db.Column(db.Boolean, nullable=False, default=False)
    patient = db.relationship('Patient', uselist=False, backref='patient_bed')
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    
    def occupy_bed(self, patient):
        self.patient = patient
        self.occupied = True

    def release_bed(self):
        self.patient is None
        self.occupied = False


#User Table
class User(db.Model, UserMixin):

    type = db.Column(db.String(32)) 

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type,
    }

    id = db.Column(db.Integer, primary_key=True)
    
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # Class information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    gender = db.Column(db.String(1,collation='NOCASE'), nullable=False)
    date_of_birth = db.Column(db.String(11,collation='NOCASE'), nullable=False)
    phone_no = db.Column(db.String(13,collation='NOCASE'))
    role = db.Column(db.String(2), nullable=False, default='p')
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.now())
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    bad_logins = db.Column(db.Integer, nullable=False, default=0)
    last_login_attempt = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=False)
    block_login = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.first_name}"

    def is_patient(self):
        if self.role.lower() == 'p':
            return True
        return False

    def is_medical_staff(self):
        if self.role.lower() == 'md':
            return True
        return False

    def is_management_staff(self):
        if self.role.lower() == 'ms':
            return True
        return False
    
    def is_admin(self):
        if self.role.lower() == 'a':
            return True
        return False

    def age(self):
        dob = self.date_of_birth.split('-')
        years = int(dob[0])
        month = int(dob[1])
        days = int(dob[2])
        today = datetime.today()
        birthdate = datetime(years,month,days)
        if today > birthdate: 
            age_time = today - birthdate
            return math.floor((age_time.days)/365)

    def get_token(self, expires_sec=600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __eq__(self, other):
        return self.email == other.email
    
    # def no_of_bad_logins(self):
    #     if self.last_login_attempt < today - timedelta(minutes=5) and self.bad_logins >= 3:
    #         return


#Mangement_Staff (Uses the User Table since it is derivd from the user) 
class Management_Staff(User):
    __tablename__ = 'management_staff'  # Add table name to be None
    __mapper_args__ = {
        'polymorphic_identity': 'management_staff'
    }

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)



Patients = db.Table('patients',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id')),
    db.Column('medical_staff_id', db.Integer, db.ForeignKey('medical_staff.id')),
    db.Column('timeout', db.DateTime(timezone=True), nullable=False, default=datetime.today() + timedelta(days=7))
)    


#Medical (Uses the User Table since it is derivd from the user)
class Medical_Staff(User):
    __tablename__ = 'medical_staff'  # Add table name to be None
    __mapper_args__ = {
        'polymorphic_identity': 'medical_staff'
    }
    
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    specialty = db.Column(db.String(50,collation='NOCASE'))
    department_head = db.Column(db.Boolean, default=False)

    hospital = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    department = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    schedule = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False, default=1)
    appointments = db.relationship('Appointment', backref='medical_staff_appointment')
    diagnoses = db.relationship('Diagnosis', backref='medical_staff_diagnosis')
    patients = db.relationship('Patient', secondary='patients', lazy='subquery', backref=db.backref('medical_staff_patients', lazy=True))
    def is_department_head(self):
        return self.department_head
    

#Patient (Uses the User Table since it is derivd from the user)
class Patient(User):
    __tablename__ = 'patient'  # Add table name to be None
    __mapper_args__ = {
        'polymorphic_identity': 'patient'
    }

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    patient_file = db.Column(db.String(255,collation='NOCASE'))
    appointments = db.relationship('Appointment', backref='patient_appointment')
    diagnoses = db.relationship('Diagnosis', backref='patient_diagnosis')
    lab_results = db.relationship('Lab_Result', backref='patient_lab_result')
    diagnoses_file = db.Column(db.String(255,collation='NOCASE'))
    lab_results_file = db.Column(db.String(255,collation='NOCASE'))
    bed = db.Column(db.Integer, db.ForeignKey('bed.id'), nullable=True)    

    def create_patient_file(self):
        #Patient folder
        name = "PatientNo"+str(self.id)
        directory = os.path.join(UPLOAD_DIRECTORY, name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.patient_file = directory
        
        #Diagnoses folder
        path = self.patient_file
        name = "Diagnoses"
        directory = os.path.join(path, name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.diagnoses_file = directory

        #Lab Results folder
        path = self.patient_file
        name = "Lab results"
        directory = os.path.join(path, name)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.lab_results_file = directory

    def last_visit(self,medical_staff_id):
        last_visit = datetime.today()
        appointments = Appointment.query.filter(Appointment.patient==self.id, Appointment.medical_staff==medical_staff_id).all()
        for appointment in appointments:
            if appointment.appointment_date_time < last_visit:
                last_visit = appointment.appointment_date_time

        if last_visit.date() == datetime.today().date() and last_visit.hour == datetime.today().hour: 
            return
        return last_visit



