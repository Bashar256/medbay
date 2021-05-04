from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask import Flask
import os

DB_NAME = "database.db"
BASE = "website"
UPLOAD_FOLDER = "static"
PATIENTS_FOLDERS = "patients"
base_directory = os.path.join(BASE, UPLOAD_FOLDER)
directory = os.path.join(base_directory, PATIENTS_FOLDERS)
if not os.path.isdir(directory):
    os.mkdir(directory)

patient_sidebar = {'My Appointments':'calendar-1','Lab Results':'notepad-2','diagnoses':'heart'}
medical_staff_sidebar = {'My Appointments':'television', 'Patients':'heart', 'Shifts':'pad'}
department_head_sidebar = {'My Appointments':'television', 'Staff':'notepad-2', 'Patients':'heart', 'Shifts':'pad', 'Rooms':'reading'}
management_staff_sidebar = {'Departments':'network', 'Staff':'notepad-2', 'Shifts':'pad', 'Rooms':'reading'}
admin_sidebar = {'Hospitals':'television', 'Staff':'networking', 'Rooms':'reading'}

os.environ['SECRET_KEY_FLASK'] =  'SecretKey'

app = Flask(__name__, static_folder='static')
app.secret_key = '0930444342a12c461c38d7c0837e39eff978504b64b1d765'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app=app)
db.init_app(app)

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD")
mail = Mail(app)

from .auth import auth_view
from .users import user_view, bad_request, unauthorized,forbidden, page_not_found, method_not_allowed, server_error, service_unavaiable
#from .admin import admin_view

app.register_error_handler(400, bad_request)
app.register_error_handler(401, unauthorized)
app.register_error_handler(403, forbidden)
app.register_error_handler(404, page_not_found)
app.register_error_handler(405, method_not_allowed)
app.register_error_handler(500, server_error)
app.register_error_handler(503, service_unavaiable)

app.register_blueprint(auth_view, url_prefix="/")
app.register_blueprint(user_view, url_prefix="/")
#app.register_blueprint(admin_view, url_prefix="/admin")   

from .models import User

with app.app_context():
    db.create_all(app=app)



from website import users, auth