from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import math

class Hospital(db.Model):
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, collation='NOCASE'), unique=True)
    departments = db.relationship('Department')
    
    def __repr__(self):
        return f"{self.name}"


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    hostpital = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    doctors = db.relationship('User')
    rooms = db.relationship('Room')
    appointments = db.relationship('Appointment')

    def __repr__(self):
        return f"{self.name}"
    
    def is_head_of_department(self):
        return self.doctors.head_of_department


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    #active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # Class information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    gender = db.Column(db.String(1,collation='NOCASE'),nullable=False, server_default='')
    date_of_birth = db.Column(db.String(11,collation='NOCASE'),nullable=False, server_default='')
    phone_no = db.Column(db.String(13,collation='NOCASE'))
    department = db.Column(db.Integer, db.ForeignKey('departments.id'))
    room = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    bed = db.Column(db.Integer, db.ForeignKey('beds.id'))

    # Define relationships
    roles = db.Column(db.Integer,db.ForeignKey('roles.id'))
    diagnosis = db.relationship('Diagnosis')

    def __repr__(self):
        return f"{self.first_name}"

    def age(self):
        dob = self.dob.split('-')
        years = dob[0]
        months = dob[1]
        days = dob[2]
        today = datetime.today()
        birthdate = datetime(years,month,days)
        if today > birthdate: 
            age_time = today - birthdate
            return math.floor((age_time.days)/365)

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    user_id = db.relationship('User', backref=db.backref('Role'))
    
    def __repr__(self):
        return f"{self.name}"

# Define the UserRoles association table
# class UserRoles(db.Model):
#     __tablename__ = 'user_roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
#     role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# class Staff(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     title = db.Column(db.String(50))
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String)
#     dob = db.Column(db.String(11))
#     phone_no = db.Column(db.String(13))
#     gender = db.Column(db.String(1))
#     management = db.Column(db.Boolean(), default=False)
#     department = db.Column(db.Integer, db.ForeignKey('department.id'))
#     diagnosis = db.relationship('Diagnosis')
#     patient = db.relationship('User')
#     head_of_department = db.Column(db.Boolean, default=False)

#     def __repr__(self):
#         return f"{self.name}"

#     def is_management(self):
#         return self.management
    
#     def age(self):
#         dob = self.dob.split('-')
#         years = dob[0]
#         months = dob[1]
#         days = dob[2]
#         today = datetime.today()
#         birthdate = datetime(years,month,days)
#         if today > birthdate: 
#             age_time = today - birthdate
#             return math.floor((age_time.days)/365)


class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'

    id = db.Column(db.Integer, primary_key=True)
    
    description = db.Column(db.String(2048), unique=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    doctor = db.Column(db.Integer, db.ForeignKey('users.id'))
    #patient = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"{self.doctor + self.description}"


# class Patient(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String)
#     dob = db.Column(db.String(11))
#     phone_no = db.Column(db.String(13))
#     gender = db.Column(db.String(1))
#     room = db.Column(db.Integer, db.ForeignKey('room.id'))
#     bed = db.Column(db.Integer, db.ForeignKey('bed.id'))
#     diagnosis = db.relationship('Diagnosis')
#     doctor = db.Column(db.Integer, db.ForeignKey('staff.id'))

#     def __repr__(self):
#         return f"{self.name}"
    

#     def age(self):
#         dob = self.dob.split('-')
#         years = dob[0]
#         months = dob[1]
#         days = dob[2]
#         today = datetime.today()
#         birthdate = datetime(years,month,days)
#         if today > birthdate: 
#             age_time = today - birthdate
#             return math.floor((age_time.days)/365)


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    time = db.Column(db.DateTime, nullable=False) 
    department = db.Column(db.Integer, db.ForeignKey('departments.id'))
    patient = db.Column(db.Integer, db.ForeignKey('users.id'))
    doctor = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"{self.patient + self.doctor + self.time}"


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)

    room_no = db.Column(db.Integer)
    department = db.Column(db.Integer, db.ForeignKey('departments.id'))
    patients = db.relationship('User')
    beds = db.relationship('Bed')
    no_of_beds = db.Column(db.Integer)
    occupied_beds = db.Column(db.Integer, default=0)

    def is_full(self):
        if self.no_of_beds == self.occupied_beds:
            return True
        return False

    def is_empty(self):
        if self.occupied_beds == 0:
            return True
        return False

    def bed_count(self):
        return self.no_of_beds

    def free_beds(self):
        return self.no_of_beds - self.occupied_beds

    def __repr__(self):
        return f'{room_no}'


class Bed(db.Model):
    __tablename__ = 'beds'

    id = db.Column(db.Integer, primary_key=True)
    
    room_no = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    occupied = db.Column(db.Boolean, default=False)
    patient = db.relationship("User", uselist=False, backref="Bed")

    def is_occupied(self):
        return self.occupied

    def book(self):
        self.occupied = True

    def free(self):
        self.occupied = False 
    
    def get_id(self):
        return self.id
