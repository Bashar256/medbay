from cryptography.fernet import Fernet
from website import KEY
from website.models import User
from threading import Thread
import datetime
import os
import time

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
    path = str(path)
    if 'website/' in path:
        path = path.replace('website/', '')
    return path.replace("\\", "/")

def save_path(path):
    path = str(path)
    return path.replace("\\", "/")


def string_to_bytes(string):
    return bytes(string, 'utf-8')


def bytes_to_string(bytes):
    return str(bytes, "utf-8")


def encrypt_email(email):
    f = Fernet(KEY)
    return f.encrypt(string_to_bytes(email))

    
def decrypt_email(email):
    f = Fernet(KEY)
    return bytes_to_string(f.decrypt(email))


def search_user_by_email(email):
    users = User.query.all()
    for user in users:
        if decrypt_email(user.email) == email:
            return user

def encrypt_file(file):
    f = Fernet(KEY)
    return f.encrypt(file)

    
def decrypt_file(file):
    f = Fernet(KEY)
    return f.decrypt(file)


def decrypted_filename(path):
    with open(path, 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = decrypt_file(encrypted)
    name = path.split(".")[0]
    name = name + "_D"
    filename = name + "." + path.split(".")[-1] 
    with open(filename, 'wb') as dec_file:
        dec_file.write(decrypted)
    Thread(target=delete_temp_file, args=[filename]).start()
    return filename

def delete_temp_file(filename):
    time.sleep(15)
    if os.path.isfile(filename):
        os.remove(filename)