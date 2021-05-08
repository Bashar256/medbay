from website import db, app, UPLOAD_FOLDER, ADMIN_SIDEBAR, PATIENT_SIDEBAR, MEDICAL_STAFF_SIDEBAR, MANAGEMENT_STAFF_SIDEBAR, DEPARTMENT_HEAD_SIDEBAR, APPOINTMENT_TIMEOUT, MAX_APPOINTMENT_DATE, SESSION_TIMEOUT, WEEKEND
from website.models import  Hospital, Department, Appointment, Management_Staff, Medical_Staff, Patient, Patients, Diagnosis, User, Lab_Result, Room, Bed, Appointment_Times, Time_Slot
from flask import Blueprint, render_template, url_for, redirect, request, flash, abort, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from website.validate import validate_staff_register
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_login import LoginManager
import datetime
import base64
import os

user_view = Blueprint("user_view", __name__, static_folder="static", template_folder="templates")
today = datetime.datetime.today()

login_manager = LoginManager()
login_manager.login_view = "auth_view.login_view"
login_manager.refresh_view = "auth_view.login_view"
login_manager.needs_refresh_message = "Session Timedout. Please Login Again"
login_manager.needs_refresh_message_category = "info"
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


@user_view.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = SESSION_TIMEOUT

#Home View
@user_view.route("/")
@user_view.route("/home")
@login_required
def home_view():
    if current_user.is_patient():
        return render_template("home.html",user=current_user, sidebar=PATIENT_SIDEBAR)
    elif current_user.is_management_staff():
        return render_template("home.html",user=current_user, sidebar=MANAGEMENT_STAFF_SIDEBAR)
    elif current_user.is_medical_staff():
        if not current_user.is_department_head():
            return render_template("home.html",user=current_user, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("home.html",user=current_user, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    elif current_user.is_admin():
        return render_template("home.html",user=current_user, sidebar=ADMIN_SIDEBAR)    
    abort(401)


#About_Us View
@user_view.route("/about_us")
@login_required
def about_us_view():
    if current_user.is_patient():
        return render_template("about_us.html",user=current_user, sidebar=PATIENT_SIDEBAR)    
    elif current_user.is_medical_staff():
        if not current_user.is_department_head():
            return render_template("about_us.html",user=current_user, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("about_us.html",user=current_user, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    elif current_user.is_management_staff():
        return render_template("about_us.html",user=current_user, sidebar=MANAGEMENT_STAFF_SIDEBAR)
    elif current_user.is_admin():
        return render_template("about_us.html",user=current_user, sidebar=ADMIN_SIDEBAR)
    abort(401) 


#Profile View
@user_view.route("/profile")
@login_required
def profile_view():
    if current_user.is_patient():
        information = patient_appointments(current_user.id)  
        return render_template("profile.html",user=current_user, information=information, today=today, sidebar=PATIENT_SIDEBAR)    
    elif current_user.is_medical_staff():
        information = medical_staff_appointments(current_user.id)
        if not current_user.is_department_head():
            return render_template("profile.html",user=current_user, information=information, today=today, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("profile.html",user=current_user, information=information, today=today, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    elif current_user.is_management_staff():
        return render_template("profile.html",user=current_user, sidebar=MANAGEMENT_STAFF_SIDEBAR)
    elif current_user.is_admin():
        return render_template("profile.html",user=current_user, sidebar=ADMIN_SIDEBAR)
    abort(401)


@user_view.route("/profile_phone")
@login_required
def profile_view_phone():
    if request.mimetype == 'application/json':
            if load_user_request(request):
                if current_user.is_patient():
                    print('Is Patient')
                    return jsonify({'firstname':current_user.first_name,'lastname':current_user.last_name,'age':current_user.age(),'phone':current_user.phone_no,'email':current_user.email})
                elif current_user.is_medical_staff():
                    print('Is medical staff')
                    return jsonify({'firstname':current_user.first_name,'lastname':current_user.last_name,'age':current_user.age(),'phone':current_user.phone_no,'email':current_user.email})
                    

@user_view.route("/appointment_history")
@login_required
def appointment_history():
    day=[]
    month=[]
    year=[]
    firstname=[]
    lastname=[]
    hospital_name=[]
    department_name=[]
    hour=[]
    minute=[]
    weekday=[]
    wdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] 
    
    if request.mimetype == 'application/json':
            if load_user_request(request):
                if current_user.is_patient():
                    information = patient_appointments(current_user.id) 
                    for appointment,hospital,department,usr,diagnoses,lab_results in information:
                        if appointment.appointment_date_time < today:
                            print("We IN")
                            day.append(appointment.appointment_date_time.day)
                            month.append(appointment.appointment_date_time.month)
                            year.append(appointment.appointment_date_time.year)
                            firstname.append(usr.first_name)
                            lastname.append(usr.last_name)
                            hospital_name.append(hospital.name)
                            department_name.append(department.name)
                            hour.append(appointment.appointment_date_time.hour)
                            minute.append(appointment.appointment_date_time.minute)
                            weekday.append(wdays[appointment.appointment_date_time.weekday()])
                    if day:
                        return jsonify({'day':day,'month':month,'year':year,'firstname':firstname,'lastname':lastname,'hospital':hospital_name,'department':department_name,'hour':hour,'minute':minute,'weekday':weekday})

@user_view.route("/appointment_upcoming")
@login_required
def appointment_upcoming():
    day=[]
    month=[]
    year=[]
    firstname=[]
    lastname=[]
    hospital_name=[]
    department_name=[]
    hour=[]
    minute=[]
    weekday=[]
    wdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] 
    
    if request.mimetype == 'application/json':
            if load_user_request(request):
                if current_user.is_medical_staff():
                    information = medical_staff_appointments(current_user.id)
                        for appointment,hospital,department,usr,diagnoses,lab_results in information:
                            if appointment.appointment_date_time > today:
                                print("We IN")
                                day.append(appointment.appointment_date_time.day)
                                month.append(appointment.appointment_date_time.month)
                                year.append(appointment.appointment_date_time.year)
                                firstname.append(usr.first_name)
                                lastname.append(usr.last_name)
                                hospital_name.append(hospital.name)
                                department_name.append(department.name)
                                hour.append(appointment.appointment_date_time.hour)
                                minute.append(appointment.appointment_date_time.minute)
                                weekday.append(wdays[appointment.appointment_date_time.weekday()])
                        if day:
                            return jsonify({'day':day,'month':month,'year':year,'firstname':firstname,'lastname':lastname,'hospital':hospital_name,'department':department_name,'hour':hour,'minute':minute,'weekday':weekday})



#Edit_Profile View
@user_view.route("/edit_profile", methods=["POST", "GET"])
@login_required
def edit_profile_view():
    if request.method == 'POST':
        count = 0
        email = request.form.get('email')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        password1=request.form.get('password1')
        password2 = request.form.get('password2')
        password3 = request.form.get('password3')
        gender = request.form.get('gender')
        phone_no = request.form.get('phone_no')
        dob = request.form.get('dob')

        user = User.query.filter_by(email=current_user.email).first()
        if user.email != email:
            old_user = User.query.filter_by(email=email).first()
            if old_user:
                flash("Email already exists", category="error")
            else:
                user.email = email
                user.confirmed = False
                user.confirmed_on = None
                count = count + 1

        if user.first_name != first_name:
            if len(first_name) < 2:
                flash('First name must be greater than 2 character.', category='error')
            else:
                user.first_name = first_name
                count = count + 1

        if user.last_name != last_name:
            if len(last_name) < 2:
                flash('Last name must be greater than 2 character.', category='error')
            else:
                user.last_name = last_name
                count = count + 1

        if user.date_of_birth != dob:
            user.date_of_birth = dob
            count = count + 1
        
        if user.gender != gender:
            user.gender = gender
            count = count + 1
        
        if user.phone_no != phone_no:
            if len(phone_no) != 13:
                flash("Enter a correct phone number format", category="error")
            else:
                user.phone_no = phone_no
                count = count + 1

        if password1:
            if check_password_hash(user.password, password1):
                if password2 != password3:
                    flash('Passwords don\'t match.', category='error')
                elif len(password2) < 7:
                    flash('Password must be at least 7 characters.', category='error')
                user.password = generate_password_hash(password2, method="sha256")
                count = count + 1
            else:
                flash("Your must enter your old password correctly", category="error")

        if count != 0:
            flash("Your Information was changed", category="update")
            db.session.commit()

        return redirect(url_for("user_view.edit_profile_view"))

    elif current_user.is_patient():
        return render_template("edit_profile.html",user=current_user, sidebar=PATIENT_SIDEBAR)

    elif current_user.is_medical_staff():
        if not current_user.is_department_head():
            return render_template("edit_profile.html",user=current_user, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("edit_profile.html",user=current_user, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    elif current_user.is_management_staff():
        return render_template("edit_profile.html",user=current_user, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        
    elif current_user.is_admin():
        return render_template("edit_profile.html",user=current_user, sidebar=ADMIN_SIDEBAR)    
        
@user_view.route("/edit_profile_phone", methods=["POST", "GET"])
@login_required
def edit_profile_view_phone():
    if request.method == 'POST':
        if request.mimetype=='application/json':
            data=request.json
            email = data['email']
            first_name = data['firstname']
            last_name = data['lastname']
            password1 = data['password1']
            password2 = data['password2']
            password3 = data['password3']
            gender = data['gender']
            phone_no = data['phone_no']
            dob = data['dob']

        count = 0
        error = 0
        user = User.query.filter_by(email=current_user.email).first()
        if user.email != email:
            old_user = User.query.filter_by(email=email).first()
            if old_user:
                return jsonify({'status':'Email already exists'})
            else:
                user.email = email
                user.confirmed = False
                user.confirmed_on = None
                count = count + 1

        if user.first_name != first_name:
            if len(first_name) < 2:
                return jsonify({'status':'First name must be greater than 1 character.'})
            else:
                user.first_name = first_name
                count = count + 1

        if user.last_name != last_name:
            if len(last_name) < 2:
                return jsonify({'status':'Last name must be greater than 1 character.'})
            else:
                user.last_name = last_name
                count = count + 1

        if user.date_of_birth != dob:
            user.date_of_birth = dob
            count = count + 1
        
        if user.gender != gender:
            user.gender = gender
            count = count + 1
        
        if user.phone_no != phone_no:
            if len(phone_no) != 13:
                return jsonify({'status':'Enter a correct phone number format'})
            else:
                user.phone_no = phone_no
                count = count + 1

        if password1:
            if check_password_hash(user.password, password1):
                if password2 != password3:
                    return jsonify({'status':'Passwords don\'t match.'})
                elif len(password2) < 7:
                    return jsonify({'status':'Password must be at least 7 characters.'})
                user.password = generate_password_hash(password2, method="sha256")
                count = count + 1
            else:
                return jsonify({'status':'Your must enter your old password correctly'})

        if count != 0:
            db.session.commit()
            return jsonify({'status':'Your Information was changed'})

        #return jsonify({'status':status})

    # elif current_user.is_patient():
    #     return render_template("edit_profile.html",user=current_user, sidebar=PATIENT_SIDEBAR)

    # elif current_user.is_medical_staff():
    #     if not current_user.is_department_head():
    #         return render_template("edit_profile.html",user=current_user, sidebar=MEDICAL_STAFF_SIDEBAR)
    #     return render_template("edit_profile.html",user=current_user, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    # elif current_user.is_management_staff():
    #     return render_template("edit_profile.html",user=current_user, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        
    # elif current_user.is_admin():
    #     return render_template("edit_profile.html",user=current_user, sidebar=ADMIN_SIDEBAR)    
        

#Appointment_Booking View
#Selecting Hospital
@user_view.route("/book_appointment")
@login_required
def book_appointment_view():
    if current_user.is_patient(): 
        hospitals = Hospital.query.all()
        departments = Department.query.all()

        if request.mimetype == 'application/json':
            if load_user_request(request):
                Hosp_name = []
                Hosp_id=[]
                for hospital in hospitals:
                    Hosp_name.append(str(hospital))
                    Hosp_id.append(hospital.id)
                return jsonify({'name':Hosp_name,'id':Hosp_id})
            abort(401)
             
        return render_template("book_appointment.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=PATIENT_SIDEBAR)
    abort(401)


##hello
@user_view.route("/book_appointment_department")
@login_required
def book_appointment_view_department():
    if current_user.is_patient(): 
        hospitals = Hospital.query.all()
        departments = Department.query.all()
        dept_name=[]
        dept_id=[]
        dept_hosp=[]
        if request.mimetype == 'application/json':
            if load_user_request(request):
                for department in departments:
                    dept_name.append(str(department))
                    dept_id.append(department.id)
                    dept_hosp.append(department.hospital)
                return  jsonify({'name':dept_name,'id':dept_id,'hospital':dept_hosp})
    abort(401)
# for department in departments:
#     dept_name.append({'name':str(department)})
#     dept_id.append({'id':department.id})
###############################
# for department in departments:
#     dept_name.append(str(department)})
#     dept_id.append(department.id)


#Selecting Doctor
@user_view.route("/book_appointment/<int:hospital_id>/<int:department_id>/doctors")
@login_required
def choose_medical_staff_view(hospital_id,department_id):
    if current_user.is_patient(): 
        medical_staff = Medical_Staff.query.filter(Medical_Staff.department==department_id, Medical_Staff.hospital==hospital_id)
        return render_template("doctors.html", user=current_user, hospital_id=hospital_id, department_id=department_id, medical_staff=medical_staff, sidebar=PATIENT_SIDEBAR)
    abort(401)


#Doctor Details
@user_view.route("/book_appointment/<int:hospital_id>/<int:department_id>/staff_details_<int:staff_id><string:role>", methods=["POST", "GET"])
@login_required
def doctor_details_view(hospital_id, department_id, staff_id,role="md"):  
    if current_user.is_patient():
        if request.method == 'POST':
            if not current_user.confirmed:
                appointment_date = request.form.get('appointment_date')
                time_slot_id = request.form.get('appointment_time')
                medical_staff = Medical_Staff.query.filter_by(id=staff_id).first()
                appointment_time = Appointment_Times.query.filter_by(id=medical_staff.appointment_times).first()
                time_slot = db.session.query(Time_Slot).filter_by(id=int(time_slot_id)).first()
                if (not time_slot) or time_slot[-1]:
                    flash("Please select one of the provided time slots", category='error')
                    return redirect(url_for("user_view.doctor_details_view", hospital_id=hospital_id, department_id=department_id, staff_id=staff_id, role=role))


                appointment_date = html_date_to_python_date(appointment_date)
                appointment_date_time = datetime.datetime.combine(appointment_date,time_slot[2])
                department = Department.query.filter_by(id=department_id).first()
                hospital = Hospital.query.filter_by(id=hospital_id).first()
                appointment = Appointment.query.filter(Appointment.appointment_date_time==appointment_date_time, Appointment.medical_staff==staff_id, Appointment.patient==current_user.id).all()
                
                if appointment:
                    flash("The doctor has an appointment at that time", category='warning')
                    return redirect(url_for("user_view.doctor_details_view", hospital_id=hospital_id, department_id=department_id, staff_id=staff_id, role=role))

                appointment = Appointment.query.filter(Appointment.appointment_date_time==appointment_date_time, Appointment.patient==current_user.id).all()
                if appointment:
                    flash("You have an appointment at that time", category='warning')
                    return redirect(url_for("user_view.doctor_details_view", hospital_id=hospital_id, department_id=department_id, staff_id=staff_id, role=role))

                new_appointment = Appointment(appointment_date_time=appointment_date_time, hospital=hospital_id, department=department_id, medical_staff=staff_id, patient=current_user.id)
                medical_staff.patients.append(current_user)
                db.session.execute(Patients.insert(), params={"patient_id":current_user.id, "medical_staff_id":staff_id, "timeout":appointment_date_time + datetime.timedelta(days=APPOINTMENT_TIMEOUT) })            
                temp_slot = time_slot
                db.session.query(Time_Slot).filter_by(id=time_slot[0]).delete()
                db.session.add(new_appointment)
                db.session.commit()
                db.session.execute(Time_Slot.insert(), params={"id": temp_slot[0], "appointment_time_id":temp_slot[1], "start":temp_slot[2], "end":temp_slot[3], "date":temp_slot[4], "appointment_id":new_appointment.id, "taken":True})
                db.session.commit()
                flash('Appointment created!', category='success')  
                return redirect(url_for("user_view.doctor_details_view", hospital_id=hospital_id, department_id=department_id, staff_id=staff_id, role=role))
                 
            flash("Please confirm your email to make an appointment", category="warning")
            return redirect(url_for("user_view.doctor_details_view", hospital_id=hospital_id, department_id=department_id, staff_id=staff_id, role=role))
        medical_staff = Medical_Staff.query.filter_by(id=staff_id).first()
        appointment_time = Appointment_Times.query.filter_by(id=medical_staff.appointment_times).first()
        return render_template("staff_details.html", user=current_user, max_appointment_date=today + datetime.timedelta(days=MAX_APPOINTMENT_DATE), today=today, staff=medical_staff, appointment_time=appointment_time, sidebar=PATIENT_SIDEBAR)
    abort(401)



#Change Appointment_Times View
@user_view.route("/appointment_time_select")
@login_required
def appointment_time_select_View():
    medical_staff_id = request.args.get('medical_staff_id')
    appointment_date = request.args.get('appointment_date')
    appointment_date = html_date_to_python_date(appointment_date)
    data = [{"id": -1}]

    if appointment_date.weekday() in WEEKEND:
        return jsonify(data)
    
    time_slots = db.session.query(Time_Slot).filter_by(date=appointment_date.date()).all()
    if time_slots:
        available_times = []
        for slot in time_slots:
            if slot[-1] == False:
                if slot not in available_times:
                    available_times.append(slot)
        
        data = [{"id": time_slot[0], "start": (time_slot[2].strftime("%H:%M")).__str__()} for time_slot in available_times]
        return jsonify(data)

    doctor = Medical_Staff.query.filter_by(id=medical_staff_id).first()
    appointment_times = Appointment_Times.query.filter_by(id=doctor.appointment_times).first()
    appointment_times.create_slots(date=appointment_date)
    time_slots = db.session.query(Time_Slot).filter_by(date=appointment_date.date()).all()
    data = [{"id": time_slot[0], "start": (time_slot[2].strftime("%H:%M")).__str__()} for time_slot in time_slots]
    return jsonify(data)  


#My_Appointments(View/Edit/Delete)  View
@user_view.route("/my_appointments", methods=["POST", "GET"])
@login_required
def my_appointments_view():
    if current_user.is_patient():
        if request.method == "POST":
            form_no = request.form.get('form_no')
            appointment_id = request.form.get('appointment_id')
            appointment_date = request.form.get('appointment_date')
            time_slot_id = request.form.get('appointment_time')
            appointment = Appointment.query.filter_by(id=appointment_id).first()
            if appointment:
                if current_user.id == appointment.patient:
                    if form_no == "1":
                        db.session.query(Patients).filter(Patients.c.patient_id==current_user.id, Patients.c.medical_staff_id==appointment.medical_staff, Patients.c.timeout==(appointment.appointment_date_time + datetime.timedelta(days=APPOINTMENT_TIMEOUT))).delete()
                        time_slot = db.session.query(Time_Slot).filter_by(appointment_id=appointment_id).first()
                        print(appointment_id)
                        print(time_slot)
                        temp_slot = time_slot
                        db.session.query(Time_Slot).filter_by(id=time_slot[0]).delete()      
                        db.session.execute(Time_Slot.insert(), params={"id": temp_slot[0], "appointment_time_id":temp_slot[1], "start":temp_slot[2], "end":temp_slot[3], "date":temp_slot[4], "taken":False})          
                        db.session.delete(appointment)
                        db.session.commit()
                        flash("Appointment Deleted!", category='update')
                        return redirect(url_for("user_view.my_appointments_view"))
                    
                    elif form_no =="2":
                        medical_staff = Medical_Staff.query.filter_by(id=appointment.medical_staff).first()
                        print(medical_staff.appointments)
                        appointment_time = Appointment_Times.query.filter_by(id=medical_staff.appointment_times).first()
                        time_slot = db.session.query(Time_Slot).filter_by(appointment_id=appointment_id).first()
                        free_appointment_time = db.session.query(Time_Slot).filter_by(id=time_slot_id).first()
                        print(db.session.query(Time_Slot).filter_by(id=time_slot_id).first())
                        if (not free_appointment_time) or free_appointment_time[-1]:
                            flash("Please select one of the provided time slots", category='error')
                            return redirect(url_for("user_view.my_appointments_view"))
                        
                        appointment_date = html_date_to_python_date(appointment_date)
                        appointment_date_time = datetime.datetime.combine(appointment_date,free_appointment_time[2])
                        appointment.appointment_date_time = appointment_date_time

                        temp_slot = time_slot
                        db.session.query(Time_Slot).filter_by(id=time_slot[0]).delete()
                        db.session.execute(Time_Slot.insert(), params={"id": temp_slot[0], "appointment_time_id":temp_slot[1], "start":temp_slot[2], "end":temp_slot[3], "date":temp_slot[4], "taken":False})

                        free_temp_slot = free_appointment_time
                        db.session.query(Time_Slot).filter_by(id=free_appointment_time[0]).delete()
                        db.session.execute(Time_Slot.insert(), params={"id": free_temp_slot[0], "appointment_time_id":free_temp_slot[1], "start":free_temp_slot[2], "end":free_temp_slot[3], "date":free_temp_slot[4], "appointment_id":appointment_id, "taken":True})                           

                        db.session.query(Patients).filter(Patients.c.patient_id==current_user.id, Patients.c.medical_staff_id==appointment.medical_staff, Patients.c.timeout==(appointment.appointment_date_time + datetime.timedelta(days=APPOINTMENT_TIMEOUT))).delete()                        
                        db.session.execute(Patients.insert(), params={"patient_id":current_user.id, "medical_staff_id":medical_staff.id, "timeout":appointment_date_time + datetime.timedelta(days=APPOINTMENT_TIMEOUT) })              
                        
                        db.session.commit()             
                        flash("Appointment Changed!", category='update')
                        return redirect(url_for("user_view.my_appointments_view"))

                    flash("Please submit a correct form", category='error')
                    return redirect(url_for("user_view.my_appointments_view"))

                flash("You can only modify your appointments", category='error')
                return redirect(url_for("user_view.my_appointments_view"))

            flash("Appointment Does not exist", category='error')
            return redirect(url_for("user_view.my_appointments_view"))

        information = patient_appointments(current_user.id)
        return render_template("my_appointments.html", user=current_user, information=information, today=today, max_appointment_date=today + datetime.timedelta(days=MAX_APPOINTMENT_DATE), sidebar=PATIENT_SIDEBAR)

    if current_user.is_medical_staff():
        information = medical_staff_appointments(current_user.id)
        if not current_user.is_department_head():
            return render_template("my_appointments.html", user=current_user, information=information, today=today, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("my_appointments.html", user=current_user, information=information, today=today, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    
    abort(401)


#Doctor_Patients View 
@user_view.route("/patients", methods=["GET", "POST"])
@login_required
def patients_view():
    if current_user.is_medical_staff():
        if request.method == 'POST':
            form_no = request.form.get("form_no")
            if form_no == "1":
                patient_id = request.form.get("patient_id")
                patient = Patient.query.filter_by(id=patient_id).first()
                if patient:           
                    rooms = Room.query.filter_by(department=current_user.department).all()
                    for room in rooms:
                        if not room.is_full():
                            for bed in room.beds:
                                if not bed.occupied:
                                    bed.occupy_bed(patient)
                                    patient.bed = bed.id
                                    db.session.commit()
                                    flash("Patient admitted", category="success")
                                    return redirect(url_for("user_view.patients_view"))
                        
                    flash("No free beds were found", category="error")
                    return redirect(url_for("user_view.patients_view"))

                flash("No such patient", category="error")
                return redirect(url_for("user_view.patients_view"))
            elif form_no == "2":
                patient_id = request.form.get("patient_id")
                patient = Patient.query.filter_by(id=patient_id).first()
                if patient:
                    bed = Bed.query.filter_by(id=patient.bed).first()
                    if bed:
                        bed.release_bed()
                        patient.bed = None
                        db.session.commit()
                        flash("Patient disscharged", category="success")
                        return redirect(url_for("user_view.patients_view"))               
            flash("no such form", category="error")
            return redirect(url_for("user_view.patients_view"))
        
        patients_timeouts = db.session.query(Patients).filter_by(medical_staff_id=current_user.id).all()
        timed_out = check_timeouts(patients_timeouts)
        doctors_patients = current_user.patients
        appointments = []
        for patient in doctors_patients:
            appointments.append(patient.last_visit(current_user.id))

        info = zip(doctors_patients, appointments, timed_out)
        if not current_user.is_department_head():
            return render_template("patients.html", user=current_user, info=info, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("patients.html", user=current_user, info=info, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    abort(401)


#File_Upload View
@user_view.route("/upload", methods=["POST"])
@login_required
def upload_file_view():
    if current_user.is_medical_staff():
        if request.method == 'POST':
            diganosis_file = request.files['diagnosis']
            lab_result_file = request.files['lab_result']
            patient_id = request.form.get("patient_id")
            date_time = request.form.get("appointment")
            date_time = date_time.split(' ')
            date = date_time[0].split('-')
            time = date_time[1].split(':')
            appointment_date_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1])) 
            appointment = Appointment.query.filter(Appointment.medical_staff==current_user.id, Appointment.patient==patient_id, Appointment.appointment_date_time==appointment_date_time).first()
            patient = Patient.query.filter_by(id=patient_id).first()
            if diganosis_file.filename:
                filename = secure_filename("Patient" + str(patient_id) + "_" + "Doctor" + str(current_user.id) + "_" + "Diagnosis" + "_" + str(datetime.datetime.today().strftime("%d-%m-%y %H:%M:%S")))
                path = os.path.join(patient.diagnoses_file, filename)
                diganosis_file.save(path)
                new_diagnosis = Diagnosis(path=path, date=datetime.datetime.now(), medical_staff=current_user.id, patient=patient_id, appointment=appointment.id)
                db.session.add(new_diagnosis)
                db.session.commit()
                flash("Diagnosis uploaded successfully", category="success")
                return redirect(url_for("user_view.patients_view"))

            elif lab_result_file:
                filename = secure_filename("Patient" + str(patient_id) + "_" + "Doctor" + str(current_user.id) + "_" + "Lab_result" + "_" + str(datetime.datetime.today().strftime("%d-%m-%y %H:%M:%S")))
                path = os.path.join(patient.lab_results_file, filename)
                lab_result_file.save(path)
                new_lab_result = Lab_Result(path=path, date=datetime.datetime.now(), medical_staff=current_user.id, patient=patient_id, appointment=appointment.id)
                db.session.add(new_lab_result)
                db.session.commit()
                flash("Lab result uploaded successfuly", category="success")
                return redirect(url_for("user_view.patients_view"))

            flash('Plese select a file', category="warning")
            return redirect(url_for("user_view.patients_view")) 
        abort(405)
    abort(401)


#File_Download View
@user_view.route('/download/<path:filename>', methods=['GET', 'POST'])
@login_required
def download_view(filename):
    if os.path.isfile(filename):
        return send_file(get_path(filename), as_attachment=True)
    abort(404)


#Patient_Profile View
@user_view.route("/patient_details<int:patient_id>")
@login_required
def patient_details_view(patient_id):
    if current_user.is_medical_staff():
        patient_timeout = db.session.query(Patients).filter(Patients.c.patient_id==patient_id, Patients.c.medical_staff_id==current_user.id).first()
        if check_timeout(patient_timeout[2]):
            flash("The patient is not in your care anymore", category="error")
            return redirect(url_for("user_view.patients_view"))
        for patient in current_user.patients:
            if patient_id == patient.id:
                diagnoses = Diagnosis.query.filter(Diagnosis.patient==patient_id, Diagnosis.medical_staff==current_user.id).all()
                information = patient_appointments(patient_id)
                if not current_user.is_department_head():
                    return render_template("patient_details.html", user=current_user, medical_staff=current_user, information=information, diagnoses=diagnoses, patient=patient, today=today, sidebar=MEDICAL_STAFF_SIDEBAR)
                return render_template("patient_details.html", user=current_user, medical_staff=current_user, information=information, diagnoses=diagnoses, patient=patient, today=today, sidebar=DEPARTMENT_HEAD_SIDEBAR)

        return redirect(url_for('user_view.patients_view'))
    abort(401)


#Lab_Results View
@user_view.route("/lab_results", methods=["POST", "GET"])
@user_view.route("/lab_results/<int:patient_id>", methods=["POST", "GET"])
@login_required
def lab_results_view(patient_id=None):
    if current_user.is_medical_staff():
        if request.method == "POST":
            lab_result_id = request.form.get("lab_result_id")
            lab_result = Lab_Result.query.filter(Lab_Result.id==lab_result_id, Lab_Result.medical_staff==current_user.id).first()
            if lab_result:
                os.remove(lab_result.path)
                db.session.delete(lab_result)
                db.session.commit()
                flash("Lab result deleted successfuly", category="update")
                return redirect(request.url)
            flash("Already deleted or you're not allowed to delete this file", category="error")
            return redirect(request.url) 
        results = Lab_Result.query.filter(Lab_Result.medical_staff==current_user.id, Lab_Result.patient==patient_id).all()
        patient = medical_staffs_patient(current_user.id, patient_id)
        patients = []
        for i in range(len(results)):
            patients.append(patient)
        info = zip(results, patients)
        if not current_user.is_department_head():
            return render_template("lab_results.html", user=current_user, patient=patient, info=info, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("lab_results.html", user=current_user, patient=patient, info=info, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    elif current_user.is_patient():
        info = patient_lab_results(current_user.id)
        return render_template("lab_results.html", user=current_user, info=info, sidebar=PATIENT_SIDEBAR)
    abort(401)


#Diagnoses View
@user_view.route("/diagnoses", methods=["POST", "GET"])
@user_view.route("/diagnoses/<int:patient_id>", methods=["POST", "GET"])
@login_required
def diagnoses_view(patient_id=None):
    if current_user.is_patient():
        info = patient_diagnoses(current_user.id)
        return render_template("diagnoses.html", user=current_user, info=info, sidebar=PATIENT_SIDEBAR)

    elif current_user.is_medical_staff():
        if request.method == "POST":
            diagnosis_id = request.form.get("diagnosis_id")
            diagnosis = Diagnosis.query.filter(Diagnosis.id==diagnosis_id, Diagnosis.medical_staff==current_user.id).first()
            if diagnosis:
                os.remove(diagnosis.path)
                db.session.delete(diagnosis)
                db.session.commit()
                flash("Diagnosis deleted successfuly", category="update")
                return redirect(request.url)
            flash("Already deleted or you're not allowed to delete this file", category="error")
            return redirect(request.url) 
        diagnoses = Diagnosis.query.filter(Diagnosis.medical_staff==current_user.id, Diagnosis.patient==patient_id).all()
        patient = medical_staffs_patient(current_user.id, patient_id)
        patients = []
        for i in range(len(diagnoses)):
            patients.append(patient)
        info = zip(diagnoses,patients)
        if not current_user.is_department_head():
            return render_template("diagnoses.html", user=current_user,  patient=patient, info=info, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("diagnoses.html", user=current_user,  patient=patient, info=info, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    abort(401)


#Hospitals View
@user_view.route("/hospitals", methods=["POST", "GET"])
@login_required
def hospitals_view():
    if current_user.is_admin():
        if request.method == "POST":
            name = request.form.get('name')
            new_hospital = Hospital.query.filter_by(name=name).first()
            if new_hospital:
                flash('Hospital already exists!', category='error')
                return redirect(url_for('user_view.hospitals_view'))
            new_hospital = Hospital(name=name)
            db.session.add(new_hospital)
            db.session.commit()
            flash('Hospital Added!', category='success')
            return redirect(url_for('user_view.hospitals_view'))
        hospitals = Hospital.query.all()
        departments= Department.query.all()
        return render_template("hospitals.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=ADMIN_SIDEBAR)
    abort(401)


#Departments View
@user_view.route("/departments", methods=["POST", "GET"])
@login_required
def departments_view():
    if current_user.is_management_staff():
        if request.method == "POST":
            name = request.form.get('name')
            hospital = Hospital.query.filter_by(id=current_user.hospital).first()
            department = Department.query.filter(Department.hospital==hospital.id, Department.name==name).first()
            if department:
                flash('Department already exists!', category='error')
                return redirect(url_for("user_view.departments_view"))
            
            new_department = Department(name=name, hospital=hospital.id)
            db.session.add(new_department)
            db.session.commit()
            flash('Department Added!', category='success')
            return redirect(url_for('user_view.departments_view'))
        
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        medical_staff = Medical_Staff.query.filter_by(hospital=current_user.hospital).all()
        management_staff = Management_Staff.query.filter_by(hospital=current_user.hospital).all()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        return render_template("departments.html", user=current_user, hospital=hospital, management_staff=management_staff, doctors=medical_staff, departments=departments, sidebar=MANAGEMENT_STAFF_SIDEBAR)
    abort(401)
    

#Staff View
@user_view.route("/staff", methods=["POST", "GET"])
@login_required
def staff_view():
    if current_user.is_medical_staff() and current_user.is_department_head():
        medical_staff = Medical_Staff.query.filter_by(department=current_user.department).all()
        management_staff = Management_Staff.query.all()
        department = Department.query.filter_by(id=current_user.department).first()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        appointment_times = Appointment_Times.query.all()
        return render_template("staff.html", user=current_user, hospital=hospital, doctors=medical_staff, departments=department, management_staff=management_staff, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    elif current_user.is_management_staff():
        if request.method == 'POST':
            form_no = request.form.get("form_no")
            if form_no =="1":
                if validate_staff_register(request):
                    flash("Staff Added Successfully", category="success")
                    return redirect(url_for("user_view.staff_view"))
            elif form_no == "2":
                staff_id = request.form.get("user_id")
                staff = Medical_Staff.query.filter(Medical_Staff.id==staff_id, Medical_Staff.hospital==current_user.hospital).first()
                if staff:
                    doctors_patients = db.session.query(Patients).filter_by(medical_staff_id=staff.id).all()
                    db.session.delete(doctors_patients)
                    db.session.delete(staff)
                    db.session.commit()
                    flash("Doctor deleteed !", category="update")
                    return redirect(url_for("user_view.staff_view"))
                staff = Management_Staff.query.filter(Management_Staff.id==staff_id, Management_Staff.hospital==current_user.hospital).first()
                if staff:
                    db.session.delete(staff)
                    db.session.commit()
                    flash("Manager deleteed !", category="update")
                    return redirect(url_for("user_view.staff_view"))

                flash("User doesn't exist", category="error")
                return redirect(url_for("user_view.staff_view"))
            
            flash("Use correct form", category="error")
            return redirect(url_for("user_view.staff_view"))
        medical_staff = Medical_Staff.query.all()
        management_staff = Management_Staff.query.all()
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        appointment_times = Appointment_Times.query.all()
        return render_template("staff.html", user=current_user, hospital=hospital, doctors=medical_staff, departments=departments, management_staff=management_staff, appointment_times=appointment_times, sidebar=MANAGEMENT_STAFF_SIDEBAR)

    elif current_user.is_admin():
        if request.method == 'POST':
            form_no = request.form.get("form_no")
            if form_no =="1":
                if validate_staff_register(request):
                    flash("User Added Successfully", category="success")
                    return redirect(url_for("user_view.staff_view"))
            elif form_no == "2":
                staff_id = request.form.get("user_id")
                staff = User.query.filter_by(id=staff_id).first()
                if staff:
                    if staff.is_medical_staff():
                        doctors_patients = db.session.query(Patients).filter_by(medical_staff_id=medical_staff.id).all()
                        db.session.delete(doctors_patients)
                    db.session.delete(staff)
                    db.session.commit()
                    flash("User deleteed!", category="update")
                    return redirect(url_for("user_view.staff_view"))

                flash("The user you're trying to delete doesn't exist", category="error")
                return redirect(url_for("user_view.staff_view"))

            flash("Use correct form", category="error")
            return redirect(url_for("user_view.staff_view"))

        management_staff = Management_Staff.query.all()
        hospitals = Hospital.query.all()
        admins = User.query.filter_by(role=current_user.role).all()
        return render_template("staff.html", user=current_user, hospitals=hospitals, admins=admins, management_staff=management_staff, sidebar=ADMIN_SIDEBAR)    
    abort(401)


#Staff_Details View
@user_view.route("/staff/staff_details_<int:staff_id><string:role>")
@login_required
def staff_details_view(staff_id,role):
    if current_user.is_medical_staff() and current_user.is_department_head():
        information = medical_staff_appointments(staff_id)
        staff = Management_Staff.query.filter_by(id=staff_id).first()
        appointment_time = Appointment_Times.query.filter_by(id=staff.appointment_times).first()
        return render_template("staff_details.html",user=current_user, information=information, shift=shift, staff=staff, appointment_time=appointment_time, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    elif current_user.is_management_staff():
        staff = Management_Staff.query.filter_by(id=staff_id).first()
        if staff:
            return render_template("staff_details.html", user=current_user, staff=staff, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        staff = Medical_Staff.query.filter_by(id=staff_id).first()
        if staff:
            appointment_time = Appointment_Times.query.filter_by(id=staff.appointment_times).first()
            information = medical_staff_appointments(staff_id)
            return render_template("staff_details.html", user=current_user, information=information, staff=staff,  today=today, appointment_time=appointment_time, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        
    elif current_user.is_admin():
        staff = User.query.filter(User.id==staff_id,  User.role==current_user.role).first()
        return render_template("staff_details.html",user=current_user, staff=staff, sidebar=ADMIN_SIDEBAR) 
            
    abort(401)


#Rooms View
@user_view.route("/rooms", methods=['GET', 'POST'])
@login_required
def rooms_view():
    if current_user.is_medical_staff():
        hospitals = Hospital.query.all()
        my_hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        
        return render_template("rooms.html",user=current_user, hospitals=hospitals, my_hospital=my_hospital, departments=departments, sidebar=MEDICAL_STAFF_SIDEBAR)

    elif current_user.is_management_staff():
        if request.method == 'POST':
            room_no = request.form.get("room_no")
            no_of_beds = request.form.get("no_of_beds")
            department_id = request.form.get("department_id")
            hospital_id = current_user.hospital

            if int(no_of_beds) > 4 or int(no_of_beds) < 1:
                flash("Room can have between 1 and 4 beds", category="error")
                return redirect(url_for("user_view.rooms_view"))

            department = Department.query.filter_by(id=department_id).first()
            if department and department.hospital == hospital_id:
                room = Room.query.filter(Room.room_no==room_no, Room.department==department_id).first()
                if room and room.hospital == hospital_id:
                    flash("Room already exists in this hospital", category="error")
                    return redirect(url_for("user_view.rooms_view"))

                new_room = Room(room_no=room_no, hospital=hospital_id, department=department_id, max_no_of_beds=no_of_beds)
                db.session.add(new_room)
                for i in range(int(no_of_beds)):
                    new_bed = Bed(room=new_room.id, hospital=hospital_id)
                    new_room.beds.append(new_bed)
                    db.session.add(new_bed)
                
                hospital = Hospital.query.filter_by(id=hospital_id).first()
                department.rooms.append(new_room)
                hospital.rooms.append(new_room)
                db.session.commit()
                flash("room and beds created!", category="success")
                return redirect(url_for("user_view.rooms_view"))

            flash("Department error",category="error")
            return redirect(url_for("user_view.rooms_view"))

        hospitals = Hospital.query.all()
        my_hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        
        return render_template("rooms.html",user=current_user, hospitals=hospitals, my_hospital=my_hospital, departments=departments, sidebar=MANAGEMENT_STAFF_SIDEBAR)

    elif current_user.is_admin():
        rooms = Room.query.all()
        beds = []
        for room in rooms:
            beds.append(room.beds)
    
        hospitals = Hospital.query.all()
        return render_template("rooms.html",user=current_user, hospitals=hospitals, rooms=rooms, beds=beds, sidebar=ADMIN_SIDEBAR)

    abort(401)


#Custom error pages
user_view.errorhandler(400)
def bad_request(error):
    return render_template("error_400.html"), 400


user_view.errorhandler(401)
def unauthorized(error):
    return render_template("error_401.html"), 401


user_view.errorhandler(403)
def forbidden(error):
    return render_template("error_403.html"), 403


user_view.errorhandler(404)
def page_not_found(error):
    return render_template("error_404.html"), 404


user_view.errorhandler(405)
def method_not_allowed(error):
    return render_template("error_405.html"), 405


user_view.errorhandler(500)
def server_error(error):
    return render_template("error_500.html"), 500


user_view.errorhandler(503)
def service_unavaiable(error):
    return render_template("error_503.html"), 503


#Custom functions
def patient_appointments(patient_id):
    appointments = Appointment.query.filter_by(patient=patient_id).all()
    medical_staff = []
    departments = []
    hospitals = []
    diagnoses = []
    lab_results = []
    for appointment in appointments:
        departments.append(Department.query.filter_by(id=appointment.department).first())
        medical_staff.append(Medical_Staff.query.filter_by(id=appointment.medical_staff).first())
        hospitals.append(Hospital.query.filter_by(id=appointment.hospital).first())
        diagnoses.append(appointment.diagnoses)
        lab_results.append(appointment.lab_results)

    return zip(appointments,hospitals,departments,medical_staff,diagnoses,lab_results)


def medical_staff_appointments(medical_staff_id):
    appointments = Appointment.query.filter_by(medical_staff=medical_staff_id).all()
    patients = []
    departments = []
    hospitals = []
    diagnoses = []
    lab_results = []
    for appointment in appointments:
        departments.append(Department.query.filter_by(id=appointment.department).first())
        patients.append(Patient.query.filter_by(id=appointment.patient).first())
        hospitals.append(Hospital.query.filter_by(id=appointment.hospital).first())
        diagnoses.append(appointment.diagnoses)
        lab_results.append(appointment.lab_results)
    
    information = zip(appointments,hospitals,departments,patients,diagnoses,lab_results)
    return information


def patient_lab_results(patient_id):
    medical_staff_ids = db.session.query(Patients).filter_by(patient_id=patient_id).all()
    results = Lab_Result.query.filter_by(patient=patient_id).all()
    medical_staff_objs = []
    for user_id in medical_staff_ids:
        medical_staff_objs.append(Medical_Staff.query.filter_by(id=user_id[1]).first())
    return zip(results,medical_staff_objs)


def medical_staffs_patient(medical_staff_id, patient_id):
    patient_id = db.session.query(Patients).filter(Patients.c.medical_staff_id==medical_staff_id, Patients.c.patient_id==patient_id).first()
    patient_obj = Patient.query.filter_by(id=patient_id[0]).first()
    return patient_obj


def patient_diagnoses(patient_id):
    medical_staff_ids = db.session.query(Patients).filter_by(patient_id=patient_id).all()
    diagnoses = Diagnosis.query.filter_by(patient=patient_id).all()
    medical_staff_objs = []
    for user_id in medical_staff_ids:
        for diagnosis in diagnoses:
            medical_staff_objs.append(Medical_Staff.query.filter_by(id=user_id[1]).first())
    return zip(diagnoses,medical_staff_objs)


def html_date_to_python_date(date, time=None):
    date = date.split('-')
    if time:
        time = time.split(':')
        return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]))
    return datetime.datetime(int(date[0]), int(date[1]), int(date[2])) 

def check_timeouts(patients_timeouts):
    time_outs = []
    for timeout in patients_timeouts:
        if timeout[2] < datetime.datetime.now():
            time_outs.append(True)
        time_outs.append(False)
    return time_outs


def check_timeout(patient_timeout):
    if patient_timeout < datetime.datetime.now():
        return True
    return False


def get_path(path):
    return path.replace("\\", "/")