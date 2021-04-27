# from flask import Blueprint, Flask, redirect, url_for, render_template, request, flash
# from flask_login import current_user, login_manager, login_required
# from .models import Medical_Staff, Patient, Diagnosis, Appointment
# from website import medical_staff_sidebar
# from . import db

# medical_staff_view = Blueprint("medical_staff_view", __name__, static_folder="static", template_folder="templates")


# # @medical_staff_view.route("/", methods=["POST", "GET"])
# # @medical_staff_view.route("/home", methods=["POST", "GET"])
# # @login_required
# # def home():
# #     staff = Doctor.query.filter_by(id=current_user.id).first()
# #     print(current_user.is_admin())
# #     return render_template("home.html", user=current_user, sidebar=medical_staff_sidebar)

# # @medical_staff_view.route("/profile", methods=["POST", "GET"])
# # @login_required
# # def profile():
# #     staff = Doctor.query.filter_by(id=current_user.id).first()
# #     return render_template("profile.html", user=current_user)


# @medical_staff_view.route("/diagnoses")
# @login_required
# def diagnoses():

#     if current_user.is_medical_staff():
#         diagnoses = Diagnosis.query.filter_by(medical_staff=current_user.id).all()
#         patients = Patient.query.filter_by(doctor=current_user.id).all()
#         return render_template("diagnoses.html",diagnoses=diagnoses, patients=patients, sidebar=medical_staff_sidebar)
#     return redirect(url_for('common_view.home'))
 

# # @medical_staff_view.route("/appointments")
# # @login_required
# # def appointments():
# #     if current_user.is_management():
# #         return render_template('home.html')

# #     appointments = Appointment.query.filter_by(doctor=current_user.id).all()
# #     patients = User.query.filter_by(doctor=current_user.id).all()
# #     return render_template(url_for("appointments.html",appointments=appointments, patients=patients))


# @medical_staff_view.route("/patients")
# @login_required
# def patients():
#     if current_user.is_medical_staff():
#         patients = Patient.query.filter_by(doctor=current_user.id).all()
#         return render_template("patients.html", user=current_user, patients=patients, sidebar=medical_staff_sidebar)
#     return redirect(url_for('common_view.home'))


# @medical_staff_view.route("/patient details<int:patient_id>")
# @login_required
# def patient_details(patient_id):
#     if current_user.is_medical_staff():
#         if patient_id in current_user.patients:
#             diagnoses = Diagnosis.query.filter(Diagnosis.patient==patient_id, Diagnosis.doctor==current_user.id).all()
#             diseases = Patient.query.filter_by(id=patient_id).all()
#             return render_template("patients.html", user=current_user, diseases=diseases, diagnoses=diagnoses)
#         return redirect(url_for('medical_staff_view.patients'))
#     return redirect(url_for('common_view.home'))


# # @medical_staff_view.route("/patients/<int:patient_id>/diagnoses/<int:diagnosis_id>")
# # @login_required
# # def diagnosis():
# #     diagnosis_id = Diagnosis.id
# #     return render_template(url_for("diagnoses.html", user=current_user))

# # @medical_staff_view.route("/add_diagnosis", methods=["POST", "GET"])
# # @login_required
# # def add_diagnosis():
# #     if current_user == Staff:
# #         if current_user.is_management():
# #             return redirect(url_for('common_view.home'))
        
# #         if request.method == "POST":
# #             if current_user.is_management():
# #                 flash('Only Doctors can do that', category='error')
# #                 return render_template("diagnoses.html")

# #             description = request.form.get('description')
# #             patient = request.form.get('patient')
# #             new_diagnosis = Diagnosis(description=description, patient=patient, doctor=current_user.id)
# #             db.session.add(new_diagnosis)
# #             db.session.commit()
# #             flash('Diagnosis Added!', category='success')
# #             return redirect(url_for('diagnoses'))
        
# #         return render_template("add_diagnosis.html")
    
# #     return redirect(url_for('common_view.home'))