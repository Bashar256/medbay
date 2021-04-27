# from flask import Blueprint, Flask, redirect, url_for, render_template, request, flash
# from flask_login import login_required, current_user
# from .models import  Patient, Hospital, Department, Appointment, Medical_Staff, Shift
# from website import patient_sidebar
# from . import db

# patient_view = Blueprint("patient_view", __name__, static_folder="static", template_folder="templates") 

# # @patient_view.route("/")
# # @patient_view.route("/home")
# # @login_required
# # def home():  
# #     patient = Patient.query.filter_by(id=current_user.id).first()
# #     return render_template("home.html",user=patient_sidebar, sidebar=patient_sidebar)

# # @patient_view.route("/profile", methods=["POST", "GET"])
# # @login_required
# # def profile(): 
# #     patient = Patient.query.filter_by(id=current_user.id).first()
# #     return render_template("home.html",user=patient, sidebar=patient_sidebar)


# # @patient_view.route("/my appointments")
# # @login_required
# # def appointments():
# #     if current_user.is_patient(): 
# #         hospitals = Hospital.query.all()
# #         departments = Department.query.all()
# #         return render_template("my appointments.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=patient_sidebar)
# #     return redirect(url_for('common_view.home'))

# @patient_view.route("/book appointment")
# @login_required
# def book_appointment():
#     if current_user.is_patient(): 
#         hospitals = Hospital.query.all()
#         departments = Department.query.all()
#         return render_template("book appointment.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=patient_sidebar)
#     return redirect(url_for('common_view.home'))


# @patient_view.route("/book appointment/<int:hospital_id>/<int:department_id>")
# @login_required
# def choose_doctor(hospital_id,department_id):
#     if current_user.is_patient(): 
#         doctors = Medical_Staff.query.filter(Medical_Staff.department==department_id, Medical_Staff.hospital==hospital_id)
#         return render_template("doctors.html", user=current_user, doctors=doctors, sidebar=patient_sidebar)
#     return redirect(url_for('common_view.home'))


# @patient_view.route("/add_appointment", methods=["POST", "GET"])
# @login_required
# def add_appointment():
#     if current_user == User:
#         if request.method == "POST":
#             hospital = request.form.get('hospital')
#             department = request.form.get('department')
#             patient = request.form.get('patient')
#             doctor = request.form.get('doctor')
#             time = request.form.get('time')
#             new_appointment = Appointment(time=time, hospital=hosptial, department=department, patient=patient, doctor=doctor)
#             db.session.add(new_appointment)
#             db.session.commit()
#             flash('Appointment Added!', category='success')
#             return redirect(url_for('common_viewappointments'))
#         else:
#             return render_template("add_appointment.html")
#     return redirect(url_for('common_view.appointments'))