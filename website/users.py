from website.models import  Hospital, Department, Appointment, Shift, Management_Staff, Medical_Staff, Patient, patients, Diagnosis, User, Lab_Result, Schedule, Schedules, Room, Bed
from website import db, app, UPLOAD_FOLDER, ADMIN_SIDEBAR, PATIENT_SIDEBAR, MEDICAL_STAFF_SIDEBAR, MANAGEMENT_STAFF_SIDEBAR, DEPARTMENT_HEAD_SIDEBAR
from flask import Blueprint, Flask, render_template, url_for, redirect, request, flash, abort, Response, send_from_directory, send_file, jsonify
from website.validate import validate_staff_register, validate_shift_assignment, create_schedule, change_doctor_schedule, create_shift
from werkzeug.security import generate_password_hash, check_password_hash
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


#Edit_Profile View
@user_view.route("/edit_profile", methods=["POST", "GET"])
@login_required
def edit_profile_view():
    if request.method == 'POST':
        count = 0
        email = request.form.get('email')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        password1 = request.form.get('password1')
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
                flash('First name must be greater than 1 character.', category='error')
            else:
                user.first_name = first_name
                count = count + 1

        if user.last_name != last_name:
            if len(last_name) < 2:
                flash('Last name must be greater than 1 character.', category='error')
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
                for name in hospitals:
                    Hosp_name.append({"name":str(name)})
                return jsonify(Host_name) 
        return render_template("book_appointment.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=PATIENT_SIDEBAR)
    abort(401)

@user_view.route("/book_appointment_department")
@login_required
def book_appointment_view_department():
    if current_user.is_patient(): 
        hospitals = Hospital.query.all()
        departments = Department.query.all()
        dept_name=[]
        dept_id=[]
        if request.mimetype == 'application/json':
            if load_user_request(request):
                for department in departments:
                    dept_name.append({'name':str(department)})
                    dept_id.append({'id':department.id})
                return  jsonify(dept_id)
    abort(401)


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
            date = request.form.get('appointment_date')
            time = request.form.get('appointment_time')
            date = date.split('-')
            time = time.split(':')

            appointment_date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]))
            department = Department.query.filter_by(id=department_id).first()
            hospital = Hospital.query.filter_by(id=hospital_id).first()

            appointment = Appointment.query.filter(Appointment.appointment_date_time==appointment_date, Appointment.medical_staff==staff_id, Appointment.patient==current_user.id).all()
            if appointment:
                flash("The doctor has an appointment at that time", category='warning')
                return redirect(url_for("user_view.doctor_details_view"))

            appointment = Appointment.query.filter(Appointment.appointment_date_time==appointment_date, Appointment.patient==current_user.id).all()
            if appointment:
                flash("You have an appointment at that time", category='warning')
                return redirect(url_for("user_view.doctor_details_view"))


            new_appointment = Appointment(appointment_date_time=appointment_date, hospital=hospital_id, department=department_id, medical_staff=staff_id, patient=current_user.id)
            # medical_staff.patients.append(current_user)
            db.session.execute(patients.insert(), params={"patient_id":current_user.id, "medical_staff_id":staff_id, "timeout":appointment_date + datetime.timedelta(days=7) })
            db.session.add(new_appointment)
            db.session.commit()  
            flash('Appointment created!', category='success')  
                   
        medical_staff = Medical_Staff.query.filter_by(id=staff_id).first()
        schedule = Schedule.query.filter_by(id=medical_staff.schedule).first()
        schedule_shifts = db.session.query(Schedules).filter_by(schedule_id=schedule.id).all()
        shifts = []
        for shift_id in schedule_shifts:
            shift = Shift.query.filter_by(id=shift_id[1]).first()
            if shift not in shifts:
                shifts.append(shift) 
        closest_appointment = today + datetime.timedelta(days=1)
        appointment_limit = today + datetime.timedelta(days=30)
        return render_template("staff_details.html", user=current_user, today=today, closest_appointment=closest_appointment, appointment_limit=appointment_limit, shifts=shifts_objs, staff=medical_staff, sidebar=PATIENT_SIDEBAR)

    abort(401)


#My_Appointments View
@user_view.route("/my_appointments", methods=["POST", "GET"])
@login_required
def my_appointments_view():
    if current_user.is_patient():
        if request.method == "POST":
            appointment_id = request.form.get('appointment_id')
            appointment = Appointment.query.filter_by(id=appointment_id).first()
            if appointment:
                flash("Appointment Deleted!", category='update')
                db.session.delete(appointment)
                db.session.commit()
                return redirect(url_for("user_view.my_appointments_view"))

            flash("Appointment Does not exist", category='error')
            return redirect(url_for("user_view.my_appointments_view"))
        information = patient_appointments(current_user.id)
        return render_template("my_appointments.html", user=current_user, information=information, today=today, sidebar=PATIENT_SIDEBAR)

    if current_user.is_medical_staff():
        information = medical_staff_appointments(current_user.id)
        if not current_user.is_department_head():
            return render_template("my_appointments.html", user=current_user, information=information, today=today, sidebar=MEDICAL_STAFF_SIDEBAR)
        return render_template("my_appointments.html", user=current_user, information=information, today=today, sidebar=DEPARTMENT_HEAD_SIDEBAR)
    
    abort(401)


#Edit_Appointment View
@user_view.route("/edit_appointment/<int:appoinment_id>", methods=["POST", "GET"])
@login_required
def edit_appointment(appointment_id):
    if current_user.is_patient():
        if request.method == "POST":
            date = request.form.get('appointment_date')
            time = request.form.get('appointment_time')
            date = date.split('-')
            time = time.split(':')
            appointment_date_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]))
            appointment = Appointment.query.filter_by(id=appointment_id).first()

            if appointment:
                flash("Appointment Changed", category='update')
                appointment.appointment_date_time = appointment_date_time
                db.session.query()
                db.session.commit()
                return redirect(url_for("user_view.my_appointments_view"))
    
            flash("Appointment Does not exist", category='error')
            return redirect(url_for("user_view.my_appointments_view"))
        information = patient_appointments(current_user.id)
        shifts = Shift.query.all()
        return render_template("edit_appointment.html", user=current_user, information=information, shifts=shifts, today=today, sidebar=PATIENT_SIDEBAR)

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
        patients = current_user.patients
        appointments = []
        for patient in patients:
            appointments.append(patient.last_visit(current_user.id))
        info = zip(patients, appointments)
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
def download_view(filename):
    if os.path.isfile(filename):
        return send_file(get_path(filename), as_attachment=True)
    abort(404)

#Patient_Profile View
@user_view.route("/patient_details<int:patient_id>")
@login_required
def patient_details_view(patient_id):
    if current_user.is_medical_staff():
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
        schedules = Schedule.query.filter_by(hospital=current_user.hospital).all()
        medical_staff = Medical_Staff.query.filter_by(department=current_user.department).all()
        management_staff = Management_Staff.query.all()
        department = Department.query.filter_by(id=current_user.department).first()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        return render_template("staff.html", user=current_user, hospital=hospital, schedules=schedules, doctors=medical_staff, departments=department, management_staff=management_staff, sidebar=DEPARTMENT_HEAD_SIDEBAR)

    elif current_user.is_management_staff():
        if request.method == 'POST':
            if validate_staff_register(request):
                flash("Staff Added Successfully", category="success")
            return redirect(url_for("user_view.staff_view"))
        schedules = Schedule.query.filter_by(hospital=current_user.hospital).all()
        medical_staff = Medical_Staff.query.all()
        management_staff = Management_Staff.query.all()
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        return render_template("staff.html", user=current_user, hospital=hospital, schedules=schedules, doctors=medical_staff, departments=departments, management_staff=management_staff, sidebar=MANAGEMENT_STAFF_SIDEBAR)

    elif current_user.is_admin():
        if request.method == 'POST':
            if validate_staff_register(request):
                flash("User Added Successfully", category="success")
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
    if current_user.is_patient():
        return redirect(url_for("user_view.doctor_details"))

    elif current_user.is_medical_staff() and current_user.is_department_head():
        information = medical_staff_appointments(staff_id)
        return render_template("staff_details.html",user=current_user, information=information, shift=shift, staff=staff, sidebar=MEDICAL_STAFF_SIDEBAR)

    elif current_user.is_management_staff():
        staff = Management_Staff.query.filter_by(id=staff_id).first()
        if staff:
            return render_template("staff_details.html", user=current_user, staff=staff, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        staff = Medical_Staff.query.filter_by(id=staff_id).first()
        if staff:
            information = medical_staff_appointments(staff_id)
            return render_template("staff_details.html", user=current_user, information=information, staff=staff, today=today, sidebar=MANAGEMENT_STAFF_SIDEBAR)
        
    elif current_user.is_admin():
        staff = User.query.filter(User.id==staff_id,  User.role==current_user.role).first()
        return render_template("staff_details.html",user=current_user, staff=staff, sidebar=ADMIN_SIDEBAR) 
            
    abort(401)


#Rooms View
@user_view.route("/rooms", methods=['GET', 'POST'])
@login_required
def rooms_view():
    if current_user.is_management_staff():
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


#Shifts View
@user_view.route("/shifts", methods=['GET', 'POST'])
@login_required
def shifts_view():
    if current_user.is_medical_staff():
        if not current_user.is_department_head():
            doctor_schedule = Schedule.query.filter_by(id=current_user.schedule).first()
            doctors = doctor_schedule.medical_staff
            for doctor in Medical_Staff.query.filter_by(department=current_user.department).all():
                if doctor not in doctors: 
                    doctors.append(doctor)
            
            schedules_types = []
            for doctor in doctors:
                schedules_types.append(doctor.schedule)

            doctors_schedules = []
            for schedule_type in schedules_types:
                doctor_schedule = []
                shifts = db.session.query(Schedules).filter_by(schedule_id=schedule_type).all()
                for shift in shifts:
                    doctor_schedule.append(Shift.query.filter_by(id=shift[1]).first()) 
                doctors_schedules.append(doctor_schedule)
            
            all_shifts = Shift.query.filter_by(hospital=current_user.hospital).all()
            return render_template("shifts.html", user=current_user, all_shifts=all_shifts, doctors_schedules=zip(doctors, doctors_schedules), sidebar=MEDICAL_STAFF_SIDEBAR)
        
        if request.method == 'POST':
            if form_no == "4":
                change_doctor_schedule(request)

        all_schedules = Schedule.query.filter_by(hospital=current_user.hospital).all()
        doctors = Medical_Staff.query.filter_by(department=current_user.department).all()
        schedules = []

        for doctor in doctors:
            doctor_shift = []
            for shift in db.session.query(Schedules).filter_by(schedule_id=doctor.schedule).all():
                doctor_shift.append(Shift.query.filter_by(id=shift[1]).first())
            schedules.append(doctor_shift)

        all_shifts = Shift.query.filter_by(hospital=current_user.hospital).all()
        return render_template("shifts.html", user=current_user, all_schedules=all_schedules, all_shifts=all_shifts, doctors_schedules=zip(doctors, schedules), sidebar=DEPARTMENT_HEAD_SIDEBAR)
    
    elif current_user.is_management_staff():
        if request.method == 'POST':
            form_no = request.form.get("form_no")
            if form_no == "1":
                create_schedule(request)
                return redirect(url_for("user_view.shifts_view"))

            elif form_no == "2":
                create_shift(request)
                return redirect(url_for("user_view.shifts_view"))

            elif form_no == "3":
                validate_shift_assignment(request)
                return redirect(url_for("user_view.shifts_view"))

            elif form_no == "4":
                change_doctor_schedule(request)
                return redirect(url_for("user_view.shifts_view"))

        all_schedules = Schedule.query.filter_by(hospital=current_user.hospital).all()
        doctors = Medical_Staff.query.filter_by(hospital=current_user.hospital).all()
        schedules = []

        for doctor in doctors:
            doctor_shift = []
            for shift in db.session.query(Schedules).filter_by(schedule_id=doctor.schedule).all():
                doctor_shift.append(Shift.query.filter_by(id=shift[1]).first())
            schedules.append(doctor_shift)

        all_shifts = Shift.query.filter_by(hospital=current_user.hospital).all() 
        return render_template("shifts.html", user=current_user, all_schedules=all_schedules, all_shifts=all_shifts, doctors_schedules=zip(doctors, schedules), sidebar=MANAGEMENT_STAFF_SIDEBAR)
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
    medical_staff_ids = db.session.query(patients).filter_by(patient_id=patient_id).all()
    results = Lab_Result.query.filter_by(patient=patient_id).all()
    medical_staff_objs = []
    for user_id in medical_staff_ids:
        medical_staff_objs.append(Medical_Staff.query.filter_by(id=user_id[1]).first())
    return zip(results,medical_staff_objs)


def medical_staffs_patient(medical_staff_id, patient_id):
    patient_id = db.session.query(patients).filter(medical_staff_id==medical_staff_id, patient_id==patient_id).first()
    patient_obj = Patient.query.filter_by(id=patient_id[0]).first()
    return patient_obj


def patient_diagnoses(patient_id):
    medical_staff_ids = db.session.query(patients).filter_by(patient_id=patient_id).all()
    diagnoses = Diagnosis.query.filter_by(patient=patient_id).all()
    medical_staff_objs = []
    for user_id in medical_staff_ids:
        for diagnosis in diagnoses:
            medical_staff_objs.append(Medical_Staff.query.filter_by(id=user_id[1]).first())
    return zip(diagnoses,medical_staff_objs)


def get_path(path):
    return path.replace("\\", "/")