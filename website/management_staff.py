# from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash
# from flask_login import login_required, current_user
# from .models import User, Management_Staff, Medical_Staff, Patient, Hospital, Department
# from website import management_staff_sidebar
# from . import db


# management_staff_view = Blueprint("management_staff_view", __name__, static_folder="static", template_folder="templates")


# @management_staff_view.route("/staff", methods=["POST", "GET"])
# @login_required
# def staff():
#     user = User.query.filter_by(id=current_user.id).first()
#     if user.is_management_staff():
#         doctors = Medical_Staff.query.all()
#         admins = Management_Staff.query.all()
#         return render_template("staff.html", user=user, doctors=doctors, admins=admins, sidebar=management_staff_sidebar)


# @management_staff_view.route("/staff/details")
# @login_required
# def details():
#     user = User.query.filter_by(id=current_user.id).first()
#     if user.is_management_staff():
#         staff = Management_Staff.query.filter_by(id=current_user.id).first()
#         if staff:
#             return render_template("details.html", user=user, staff=staff, sidebar=management_staff_sidebar)
        
#         staff = Medical_Staff.query.filter_by(id=current_user.id).first()
#         return render_template("details.html", user=user, staff=staff, sidebar=management_staff_sidebar)

        


# # @management_staff_view.route("/staff/<int:staff_id>")
# # @login_required
# # def staff_view(user_id):
# #     staff_id = User.id
# #     return render_template("staff.html", user=current_user, id=staff_id)


# @management_staff_view.route("/add_staff", methods=["POST", "GET"])
# @login_required
# def add_staff():

#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstname')
#         last_name = request.form.get('lastname')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')
#         gender = request.form.get('gender')
#         phone_no = request.form.get('phone_no')
#         dob = request.form.get('dob')
#         medical_staff = request.form.get('medical_staff')
#         management_staff = request.form.get('management_staff')

#         staff = User.query.filter_by(email=email).first()

#         if staff:
#             flash('Email already exists.', category='error')
#         elif len(email) < 4:
#             flash('Email must be greater than 3 characters.', category='error')
#         elif len(first_name) < 2:
#             flash('First name must be greater than 1 character.', category='error')
#         elif len(last_name) < 2:
#             flash('Last name must be greater than 1 character.', category='error')            
#         elif password1 != password2:
#             flash('Passwords don\'t match.', category='error')
#         elif len(password1) < 7:
#             flash('Password must be at least 7 characters.', category='error')
#         else:
#             if management_staff:
#                 new_staff = Management(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, dob=dob, management_user=True)
#             elif medical_staff:
#                 new_staff = Medical(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'), phone_no=phone_no, gender=gender, dob=dob, medical_user=True)
#             else:
#                 flash("Please specify a role", category='error')
#                 return render_template(url_for("staff"))
#             db.session.add(new_staff)
#             db.session.commit()
#             flash('User created!', category='success')
#             return redirect(url_for('management_staff_view.staff'))
    
#     return render_template(url_for("staff"))


# # @management_staff_view.route("/hospitals", methods=["POST", "GET"])
# # @login_required
# # def hospitals():
# #     user = User.query.filter_by(id=current_user.id).first()
# #     if user.is_management_staff():
# #         hospitals = Hospital.query.all()
# #         departments= Department.query.all()
# #         if request.method == "POST":
# #             name = request.form.get('name')
# #             new_hospital = Hospital.query.filter_by(name=name).first()
# #             if new_hospital:
# #                 flash('Hospital already exists!', category='error')
# #                 return render_template("hospitals.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=management_staff_sidebar) 
# #             new_hospital = Hospital(name=name)
# #             db.session.add(new_hospital)
# #             db.session.commit()
# #             flash('Hospital Added!', category='success')
# #             return redirect(url_for('management_staff_view.hospitals'))
# #         else:
# #             return render_template("hospitals.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=management_staff_sidebar)
# #     return render_template("home.html", user=current_user, sidebar=management_staff_sidebar)
    

# # @management_staff_view.route("/hospitals/<int:hospital_id>", methods=["POST", "GET"])
# # @login_required
# # def hospital(hospital_id):
# #     hospital_id = Hospital.id
# #     return render_template("hospitals.html", user=current_user, id=hospital_id)

# # @management_staff_view.route("/add_hospital", methods=["POST", "GET"])
# # @login_required
# # def add_hospital():
# #     if request.method == "POST":
# #         name = request.form.get('name')
# #         new_hospital = Hospital(name=name)
# #         db.session.add(new_hospital)
# #         db.session.commit()
# #         flash('Hospital Added!', category='success')
# #         return redirect(url_for('management_staff_view.hospitals'))
# #     else:
# #         return render_template("add_hospital.html", user=current_user, sidebar=management_staff_sidebar)


# @management_staff_view.route("/departments", methods=["POST", "GET"])
# @login_required
# def departments():
#     user = User.query.filter_by(id=current_user.id).first()
#     if user.is_management_staff():
#         hospitals = Hospital.query.all()
#         departments= Department.query.all()
#         if request.method == "POST":
#             name = request.form.get('name')
#             hospital = request.form.get('hospital')
#             new_department = Department.query.filter_by(hospital=hospital).first()
#             if new_department:
#                 flash('Department already exists!', category='error')
#                 return render_template("hospitals.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=management_staff_sidebar) 
#             new_department = Department(name=name, hospital=hospital)
#             db.session.add(new_department)
#             db.session.commit()
#             flash('Department Added!', category='success')
#             return redirect(url_for('management_staff_view.departments'))
#         else:
#             return render_template("departments.html", user=current_user, hospitals=hospitals, departments=departments, sidebar=management_staff_sidebar)
#     return redirect(url_for('common_view.home'))
    

# @management_staff_view.route("/shifts", methods=["POST", "GET"])
# @login_required
# def shifts():
#     pass
    


# # @management_staff_view.route("/departments/<int:department_id>")
# # @login_required
# # def department(department_id):
# #     department_id = Department.id
# #     return render_template("departments.html", user=current_user, id=department_id)

# # @management_staff_view.route("/add_department", methods=["POST", "GET"])
# # @login_required
# # def add_department():
# #     if request.method == "POST":
# #         name = request.form.get('name')
# #         hospital = request.form.get('hospital')
# #         new_department = Department(name=name, hospital=hospital)
# #         db.session.add(new_department)
# #         db.session.commit()
# #         flash('Department Added!', category='success')
# #         return redirect(url_for('management_staff_view.departments'))
# #     else:
# #         return render_template("add_department.html")


# # @management_staff_view.route("/departments/<int:department_id>/rooms")
# # @login_required
# # def rooms(department_id):
# #     user = User.query.filter_by(id=current_user.id).first()
# #     if user.is_admin():
# #         doctors = Doctor.query.all()
# #         admins = Admin.query.all()
# #         return render_template("staff.html", user=user, doctors=doctors, admins=admins, sidebar=admin_sidebar)

# # @management_staff_view.route("/rooms/<int:room_id>")
# # @login_required
# # def room(room_id):
# #     room_id = Room.id
# #     return render_template("rooms.html", user=current_user, id=room_id)

# # @management_staff_view.route("/add_room", methods=["POST", "GET"])
# # @login_required
# # def add_room():
# #     if request.method == "POST":
# #         room_no = request.form.get('room_no')
# #         no_of_beds = request.form.get('no_of_beds')
# #         new_room = Room(room_no=room_no, no_of_beds=no_of_beds)
# #         db.session.add(new_room)
# #         db.session.commit()
# #         flash('Room Added!', category='success')
# #         return redirect(url_for('management_staff_view.rooms'))
# #     else:
# #         return render_template("add_room.html")


# # @management_staff_view.route("/rooms/<int:room_id>/beds")
# # @login_required
# # def beds(room_id):
# #     if current_user == User:
# #         if current_user.is_management():
# #             beds = Bed.query.filter_by(room=room_id).all()
# #             return render_template("beds.html", user=current_user, beds=beds, sidebar=admin_sidebar)

# # # @management_staff_view.route("/beds/<int:bed_id>")
# # # def bed(bed_id):
# # #     bed_id = Bed.id
# # #     return render_template("beds.html", user=current_user, id=bed_id)

# # @management_staff_view.route("/add_bed", methods=["POST", "GET"])
# # @login_required
# # def add_bed():
# #     if request.method == "POST":
# #         room_no = request.form.get('room_no')
# #         new_bed = Bed(room_no=room_no, occupied=False)
# #         db.session.add(new_bed)
# #         db.session.commit()
# #         flash('Bed Added!', category='success')
# #         return redirect(url_for('management_staff_view.beds'))
# #     else:
# #         return render_template("add_bed.html")
