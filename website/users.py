from flask import Blueprint, Flask, render_template, url_for, redirect, request, flash, abort, Response, send_from_directory, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import  Hospital, Department, Appointment, Shift, Management_Staff, Medical_Staff, Patient, patients, Diagnosis, User, Lab_Result, doctors_shifts
from website import admin_sidebar, patient_sidebar, medical_staff_sidebar, management_staff_sidebar
from website import db, UPLOAD_FOLDER
import datetime
import os
from website.validate import validate_staff_register

user_view = Blueprint("user_view", __name__, static_folder="static", template_folder="templates")
today = datetime.datetime.today()

@user_view.route("/shifts")
@login_required
def view_shifts():
    if current_user.is_medical_staff() or current_user.is_management_staff():
        shifts = []
        dates = []
        doctors = Medical_Staff.query.all()
        for doctor in doctors:
            days = db.session.query(doctors_shifts).filter_by(medical_staff_id=doctor.id).all()
            for day in days:
                if not day[2].date() in dates:
                    dates.append(day[2].date())
            shifts.append(doctor.shifts)
        doctors_info = zip(doctors,shifts)
        return render_template("shifts.html", user=current_user, doctors_info=doctors_info, dates=dates, sidebar=medical_staff_sidebar)
    elif current_user.is_management_staff():
        return render_template("shifts.html", user=current_user, sidebar=management_staff_sidebar)


@user_view.route("/assign shifts", methods=['GET', 'POST'])
@login_required
def assign_shifts():
    if current_user.is_management_staff():
        if request.method == "POST":
            pass
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        return render_template("assign shifts.html", user=current_user, departments=departments, sidebar=management_staff_sidebar)
    abort(401)


# @user_view.route("/Patients/PatientNo#<int:patient_id>/diagnoses/<str:filename>")
# def download(patient_id, filename):
#     file_path =  "/Patients/PatientNo#" + patient_id + "/diagnoses/" + filename
#     return send_file(file_path, as_attachment=True, attachment_filename='')



#@patient_view.route("/add_appointment", methods=["POST", "GET"])
# @login_required
# def add_appointment():
#     if current_user == User:
#         if request.method == "POST":
#             hospital = request.form.get('hospital')
#             department = request.form.get('department')
#             patient = request.form.get('patient')
#             medical_staff = request.form.get('medical_staff')
#             time = request.form.get('time')
#             new_appointment = Appointment(time=time, hospital=hosptial, department=department, patient=patient, medical_staff=medical_staff)
#             db.session.add(new_appointment)
#             db.session.commit()
#             flash('Appointment Added!', category='success')
#             return redirect(url_for('common_viewappointments'))
#         else:
#             return render_template("add_appointment.html")
#     return redirect(url_for('common_view.appointments'))

# @user_view.route("/diagnoses")
# @login_required
# def diagnoses():
#     user = User.query.filter_by(roles=current_user.roles).first()
#     if user.roles == 1:
#         return redirect(url_for("home"))
#     elif user.roles == 2:
#         diagnoses = Diagnosis.query.filter_by(medical_staff=current_user.id).all()
#         patients = User.query.filter_by(medical_staff=current_user.id).all()
#         return render_template(url_for("diagnoses.html",diagnoses=diagnoses, patients=patients))
        
#     return render_template("home.html",user=user, sidebar=patient_sidebar)

#     if current_user == User:
#         if current_user.is_management():
#             return redirect(url_for("home"))

#         diagnoses = Diagnosis.query.filter_by(medical_staff=current_user.id).all()
#         patients = User.query.filter_by(medical_staff=current_user.id).all()
#         return render_template(url_for("diagnoses.html",diagnoses=diagnoses, patients=patients))
    
#     diagnoses = Diagnoses.query.filter_by(patient=current_user.id).all()
#     patients = User.query.filter_by(patient=current_user.id).first()
#     return render_template(url_for("diagnoses.html",diagnoses=diagnoses, patients=patients))
    

# @user_view.route("/appointments")
# @login_required
# def appointments():
#     if current_user == User:
#         if current_user.is_management():
#             return render_template('home.html')

#         appointments = Appointment.query.filter_by(medical_staff=current_user.id).all()
#         patients = User.query.filter_by(medical_staff=current_user.id).all()
#         return render_template(url_for("appointments.html",appointments=appointments, patients=patients))
    
#     appointments = Appointment.query.filter_by(patient=current_user.id).all()
#     return render_template(url_for("diagnoses.html", appointments=appointments, patients=current_user))


#Common view

@user_view.route("/")
@user_view.route("/home")
@login_required
def home():
    print(request.from_values)
    appointments = Appointment.query.filter_by(medical_staff=current_user.id).all()
    if current_user.is_admin():
        return render_template("home.html",user=current_user, sidebar=admin_sidebar)    
    if current_user.is_management_staff():
        return render_template("home.html",user=current_user, sidebar=management_staff_sidebar)
    elif current_user.is_medical_staff():
        return render_template("home.html",user=current_user, appointments=appointments, sidebar=medical_staff_sidebar)
    
    appointments = Appointment.query.filter_by(patient=current_user.id).all()
    return render_template("home.html",user=current_user, appointments=appointments, sidebar=patient_sidebar)


@user_view.route("/profile")
@login_required
def profile():
    if current_user.is_patient():
        information = patient_appointments(current_user.id)  
        return render_template("profile.html",user=current_user, information=information, today=today, sidebar=patient_sidebar)    
    elif current_user.is_medical_staff():
        information = medical_staff_appointments(current_user.id)
        return render_template("profile.html",user=current_user, information=information, today=today, sidebar=medical_staff_sidebar)
    elif current_user.is_management_staff():
        return render_template("profile.html",user=current_user, sidebar=management_staff_sidebar)
    elif current_user.is_admin():
        return render_template("profile.html",user=current_user, sidebar=admin_sidebar)
    abort(401)


@user_view.route("/edit profile", methods=["POST", "GET"])
@login_required
def edit_profile():
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

        if not check_password_hash(user.password, password1):
            if password2 != password3:
                flash('Passwords don\'t match.', category='error')
            elif len(password2) < 7:
                flash('Password must be at least 7 characters.', category='error')
            user.password = generate_password_hash(password2, method="sha256")
            count = count + 1

        if not count:
            flash("Your Information was changed", category="success")
        db.session.commit()
        return redirect(url_for("user_view.profile"))

    elif current_user.is_patient():
        return render_template("edit profile.html",user=current_user, sidebar=patient_sidebar)

    elif current_user.is_medical_staff():
        return render_template("edit profile.html",user=current_user, sidebar=medical_staff_sidebar)

    elif current_user.is_management_staff():
        return render_template("edit profile.html",user=current_user, sidebar=management_staff_sidebar)
        
    elif current_user.is_admin():
        return render_template("edit profile.html",user=current_user, sidebar=admin_sidebar)    
        

#Common view END


#Appointment booking

@user_view.route("/book appointment")
@login_required
def book_appointment():
    if current_user.is_patient(): 
        hospitals = Hospital.query.all()
        departments = Department.query.all()
        print(request.content_type)
        if request.content_type == 'application/json':
           return jsonify({'hospital':hospitals})
        return render_template("book appointment.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=patient_sidebar)
    abort(401)


@user_view.route("/book appointment/<int:hospital_id>/<int:department_id>/doctors")
@login_required
def choose_medical_staff(hospital_id,department_id):
    if current_user.is_patient(): 
        medical_staff = Medical_Staff.query.filter(Medical_Staff.department==department_id, Medical_Staff.hospital==hospital_id)
        return render_template("doctors.html", user=current_user, hospital_id=hospital_id, department_id=department_id, medical_staff=medical_staff, sidebar=patient_sidebar)
    abort(401)



#Appointment medical_staff details

@user_view.route("/book appointment/<int:hospital_id>/<int:department_id>/staff details-<int:staff_id><string:role>", methods=["POST", "GET"])
@login_required
def doctor_details(hospital_id, department_id, staff_id,role="md"): 
    medical_staff = Medical_Staff.query.filter_by(id=staff_id).first()
    # schedule = Schedule.query.filter_by(id=medical_staff.schedule).first()
    # shifts_ids = db.session.query(shifts).filter_by(schedule_id=schedule.id).all()
    shifts_objs = []
    for shift_id in shifts_ids:
        shift = Shift.query.filter_by(id=shift_id[0]).first()
        if shift not in shifts_objs:
            shifts_objs.append(shift)  
    # print(schedule,shifts_ids)
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
                flash("There is already an appointment at that time", category='error')
                return redirect(url_for("user_view.doctor_details"))

            appointment = Appointment.query.filter(Appointment.appointment_date_time==appointment_date, Appointment.patient==current_user.id).all()
            if appointment:
                flash("There is an  appointment at that time", category='error')
                return redirect(url_for("user_view.doctor_details"))


            new_appointment = Appointment(appointment_date_time=appointment_date, hospital=hospital_id, department=department_id, medical_staff=staff_id, patient=current_user.id)
            # medical_staff.patients.append(current_user)
            db.session.execute(patients.insert(), params={"patient_id":current_user.id, "medical_staff_id":staff_id, "timeout":appointment_date + datetime.timedelta(days=7) })
            db.session.add(new_appointment)
            db.session.commit()  
            flash('Appointment created!', category='success')         

        closest_appointment = today + datetime.timedelta(days=1)
        appointment_limit = today + datetime.timedelta(days=30)
        return render_template("staff details.html", user=current_user, today=today, closest_appointment=closest_appointment, appointment_limit=appointment_limit, shifts=shifts_objs, staff=medical_staff, sidebar=patient_sidebar)

    abort(401)

#Appointment medical_staff details END
#Appointment booking END


#Appointments page

@user_view.route("/my appointments", methods=["POST", "GET"])
@login_required
def my_appointments():
    if current_user.is_patient():
        if request.method == "POST":
            appointment_id = request.form.get('appointment_id')
            appointment = Appointment.query.filter_by(id=appointment_id).first()
            if appointment:
                flash("Appointment Deleted!", category='success')
                db.session.delete(appointment)
                db.session.commit()
                return redirect(url_for("user_view.my_appointments"))

            flash("Appointment Does not exist", category='error')
            return redirect(url_for("user_view.my_appointments"))
        information = patient_appointments(current_user.id)
        # schedules = Shift.query.all()
        return render_template("my appointments.html", user=current_user, information=information, shifts=shifts, today=today, sidebar=patient_sidebar)

    if current_user.is_medical_staff():
        information = medical_staff_appointments(current_user.id)
        return render_template("my appointments.html", user=current_user, information=information, today=today, sidebar=medical_staff_sidebar)
    
    abort(401)

#Appointments page END



@user_view.route("/edit appointment/<int:appoinment_id>", methods=["POST", "GET"])
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
                flash("Appointment Changed", category='success')
                appointment.appointment_date_time = appointment_date_time
                db.session.query()
                db.session.commit()
                return redirect(url_for("user_view.my_appointments"))
    
            flash("Appointment Does not exist", category='error')
            return redirect(url_for("user_view.my_appointments"))
        information = patient_appointments(current_user.id)
        shifts = Shift.query.all()
        return render_template("edit appointment.html", user=current_user, information=information, shifts=shifts, today=today, sidebar=patient_sidebar)

    abort(401)




#Patient Info
	
@user_view.route("/patients")
@login_required
def view_patients():
    if current_user.is_medical_staff():
        patients_ids = db.session.query(patients).filter_by(medical_staff_id=current_user.id).all()
        patients_obj = []
        appointments = []
        count=0
        for p_id in patients_ids:
            patient = Patient.query.filter_by(id=p_id[0]).first()
            if patient not in patients_obj:
                patients_obj.append(patient) 
                appointments.append(patients_obj[count].last_visit())
            count = count + 1    
        info = zip(patients_obj, appointments)
        return render_template("patients.html", user=current_user, info=info, sidebar=medical_staff_sidebar)
    abort(401)

@user_view.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if request.method == 'POST':
        diganosis_file = request.files['diagnosis']
        lab_result_file = request.files['lab_result']
        patient_id = request.form.get("patient_id")
        patient = Patient.query.filter_by(id=patient_id).first()
        if diganosis_file.filename:
            filename = secure_filename("Patient" + str(patient_id) + "_" + "Doctor" + str(current_user.id) + "_" + "Diagnosis" + "_" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
            path = os.path.join(patient.diagnoses, filename)
            diganosis_file.save(path)
            new_diagnosis = Diagnosis(path=path, date=datetime.datetime.now(), medical_staff=current_user.id, patient=patient_id)
            db.session.add(new_diagnosis)
            db.session.commit()
            flash("Diagnosis uploaded successfuly", category="success")
            return redirect(url_for("user_view.view_patients"))
        if lab_result_file:
            filename = secure_filename("Patient" + str(patient_id) + "_" + "Doctor" + str(current_user.id) + "_" + "Lab_result" + "_" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
            path = os.path.join(patient.lab_results, filename)
            lab_result_file.save(path)
            new_lab_result = Lab_Result(path=path, date=datetime.datetime.now(), medical_staff=current_user.id, patient=patient_id)
            db.session.add(new_lab_result)
            db.session.commit()
            flash("Lab result uploaded successfuly", category="success")
            return redirect(url_for("user_view.view_patients"))

        flash('Plese select a file', category="error")
        return redirect(url_for("user_view.view_patients")) 
    abort(405)

@user_view.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    if os.path.isfile(filename):
        return send_file(get_path(filename), as_attachment=True)
    abort(404)

@user_view.route("/patient details<int:patient_id>")
@login_required
def patient_details(patient_id):
    if current_user.is_medical_staff():
        for patient in current_user.patients:
            if patient_id == patient.id:
                diagnoses = Diagnosis.query.filter(Diagnosis.patient==patient_id, Diagnosis.medical_staff==current_user.id).all()
                information = patient_appointments(patient_id)

                return render_template("patient details.html", user=current_user, medical_staff=current_user, information=information, diagnoses=diagnoses, patient=patient, today=today, sidebar=medical_staff_sidebar)
        return redirect(url_for('user_view.view_patients'))
    abort(401)

#Patient Info END


@user_view.route("/lab results", methods=["POST", "GET"])
@user_view.route("/lab results/<int:patient_id>", methods=["POST", "GET"])
@login_required
def lab_results(patient_id=None):
    if current_user.is_medical_staff():
        if request.method == "POST":
            lab_result_id = request.form.get("lab_result_id")
            lab_result = Lab_Result.query.filter(Lab_Result.id==lab_result_id, Lab_Result.medical_staff==current_user.id).first()
            if lab_result:
                os.remove(lab_result.path)
                db.session.delete(lab_result)
                db.session.commit()
                flash("Lab result deleted successfuly", category="success")
                return redirect(request.url)
            flash("Already deleted or you're not allowed to delete this file", category="error")
            return redirect(request.url) 
        results = Lab_Result.query.filter(Lab_Result.medical_staff==current_user.id, Lab_Result.patient==patient_id).all()
        patient = medical_staffs_patient(current_user.id, patient_id)
        patients = []
        for i in range(len(results)):
            patients.append(patient)
        info = zip(results, patients)
        return render_template("lab results.html", user=current_user, patient=patient, info=info, sidebar=medical_staff_sidebar)
    elif current_user.is_patient():
        info = patient_lab_results(current_user.id)
        current_user.lab_results
        return render_template("lab results.html", user=current_user, info=info, sidebar=patient_sidebar)
    abort(401)


@user_view.route("/diagnoses", methods=["POST", "GET"])
@user_view.route("/diagnoses/<int:patient_id>", methods=["POST", "GET"])
@login_required
def diagnoses(patient_id=None):
    if current_user.is_medical_staff():
        if request.method == "POST":
            diagnosis_id = request.form.get("diagnosis_id")
            diagnosis = Diagnosis.query.filter(Diagnosis.id==diagnosis_id, Diagnosis.medical_staff==current_user.id).first()
            if diagnosis:
                os.remove(diagnosis.path)
                db.session.delete(diagnosis)
                db.session.commit()
                flash("Diagnosis deleted successfuly", category="success")
                return redirect(request.url)
            flash("Already deleted or you're not allowed to delete this file", category="error")
            return redirect(request.url) 
        diagnoses = Diagnosis.query.filter(Diagnosis.medical_staff==current_user.id, Diagnosis.patient==patient_id).all()
        patient = medical_staffs_patient(current_user.id, patient_id)
        patients = []
        for i in range(len(diagnoses)):
            patients.append(patient)
        info = zip(diagnoses,patients)
        return render_template("diagnoses.html", user=current_user,  patient=patient, info=info, sidebar=medical_staff_sidebar)
    elif current_user.is_patient():
        info = patient_diagnoses(current_user.id)
        return render_template("diagnoses.html", user=current_user, info=info, sidebar=patient_sidebar)
    abort(401)


@user_view.route("/rooms", methods=["POST", "GET"])
@login_required
def rooms():
    pass

@user_view.route("/departments", methods=["POST", "GET"])
@login_required
def departments():
    if current_user.is_management_staff():
        if request.method == "POST":
            name = request.form.get('name')
            hospital = Hospital.query.filter_by(id=current_user.hospital).first()
            department = Department.query.filter(Department.hospital==hospital.id, Department.name==name).first()
            if department:
                flash('Department already exists!', category='error')
                return redirect(url_for("user_view.departments"))
            
            new_department = Department(name=name, hospital=hospital.id)
            db.session.add(new_department)
            db.session.commit()
            flash('Department Added!', category='success')
            return redirect(url_for('user_view.departments'))
        
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        medical_staff = Medical_Staff.query.filter_by(hospital=current_user.hospital).all()
        management_staff = Management_Staff.query.filter_by(hospital=current_user.hospital).all()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        return render_template("departments.html", user=current_user, hospital=hospital, management_staff=management_staff, doctors=medical_staff, departments=departments, sidebar=management_staff_sidebar)
    abort(401)
    

@user_view.route("/staff", methods=["POST", "GET"])
@login_required
def staff():
    if current_user.is_management_staff():
        if request.method == 'POST':
            if validate_staff_register(request):
                flash("Staff Added Successfully", category="success")
            return redirect(url_for("user_view.staff"))
        shifts = Shift.query.filter_by(hospital=current_user.hospital).all()
        medical_staff = Medical_Staff.query.all()
        management_staff = Management_Staff.query.all()
        departments = Department.query.filter_by(hospital=current_user.hospital).all()
        hospital = Hospital.query.filter_by(id=current_user.hospital).first()
        return render_template("staff.html", user=current_user, hospital=hospital, shifts=shifts, doctors=medical_staff, departments=departments, management_staff=management_staff, sidebar=management_staff_sidebar)


@user_view.route("/staff/staff details-<int:staff_id><string:role>")
@login_required
def staff_details(staff_id,role):
    if current_user.is_patient():
        return redirect(url_for("user_view.doctor_details"))

    elif current_user.is_medical_staff() and current_user.is_department_head():
        information = medical_staff_appointments(staff_id)
        return render_template("staff details.html",user=current_user, information=information, shift=shift, staff=staff, sidebar=medical_staff_sidebar)

    elif current_user.is_management_staff():
        staff = Management_Staff.query.filter_by(id=staff_id).first()
        if staff:
            return render_template("staff details.html", user=current_user, staff=staff, sidebar=management_staff_sidebar)
        staff = Medical_Staff.query.filter_by(id=staff_id).first()
        if staff:
            dates = []
            days = db.session.query(doctors_shifts).filter_by(medical_staff_id=staff_id).all()
            for day in days:
                if not day[2].date() in dates:
                    dates.append(day[2].date())
            shifts=staff.shifts
            information = medical_staff_appointments(staff_id)
            return render_template("staff details.html", user=current_user, shifts=shifts, dates=dates, information=information, staff=staff, today=today, sidebar=management_staff_sidebar)
        
    elif current_user.is_admin():
        return render_template("staff details.html",user=current_user, shift=shift, staff=medical_staff, sidebar=admin_sidebar) 
            
    abort(401)

#Custom error pages


user_view.errorhandler(400)
def bad_request(error):
    return render_template("error-400.html"), 400

user_view.errorhandler(401)
def unauthorized(error):
    return render_template("error-401.html"), 401

user_view.errorhandler(403)
def forbidden(error):
    return render_template("error-403.html"), 403


user_view.errorhandler(404)
def page_not_found(error):
    return render_template("error-404.html"), 404


user_view.errorhandler(405)
def method_not_allowed(error):
    return render_template("error-405.html"), 405


user_view.errorhandler(500)
def server_error(error):
    return render_template("error-500.html"), 500


user_view.errorhandler(503)
def service_unavaiable(error):
    return render_template("error-503.html"), 503

#Custom error pages END


def patient_appointments(patient_id):
    appointments = Appointment.query.filter_by(patient=patient_id).all()
    medical_staff = []
    departments = []
    hospitals = []
    for appointment in appointments:
        departments.append(Department.query.filter_by(id=appointment.department).first())
        medical_staff.append(Medical_Staff.query.filter_by(id=appointment.medical_staff).first())
        hospitals.append(Hospital.query.filter_by(id=appointment.hospital).first())
    
    information = zip(appointments,hospitals,departments,medical_staff)
    return information


def medical_staff_appointments(medical_staff_id):
    appointments = Appointment.query.filter_by(medical_staff=medical_staff_id).all()
    patients = []
    departments = []
    hospitals = []
    for appointment in appointments:
        departments.append(Department.query.filter_by(id=appointment.department).first())
        patients.append(Patient.query.filter_by(id=appointment.patient).first())
        hospitals.append(Hospital.query.filter_by(id=appointment.hospital).first())
    
    information = zip(appointments,hospitals,departments,patients)
    return information


# def medical_staff_lab_results(medical_staff_id, patient_id):
#     patient_id = db.session.query(patients).filter(medical_staff_id==medical_staff_id, patient_id==patient_id).first()
#     patient_obj = Patient.query.filter_by(id=patient_id[0]).first()
#     return patient_obj


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
        medical_staff_objs.append(Medical_Staff.query.filter_by(id=user_id[1]).first())
    return zip(diagnoses,medical_staff_objs)

def get_path(path):
    return path.replace("\\", "/")
