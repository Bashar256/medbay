import datetime
from website import CIPHER_SUIT, TIME
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
    if 'website/' in path:
        path = path.replace('website/', '')
    return path.replace("\\", "/")

def save_path(path):
    return path.replace("\\", "/")


def string_to_bytes(string):
    return bytes(string, 'utf-8')


def bytes_to_string(bytes):
    return str(bytes, "utf-8")


def encrypt_email(email):
    return CIPHER_SUIT.encrypt_at_time(string_to_bytes(email), TIME)

    
def decrypt_email(email):
    return bytes_to_string(CIPHER_SUIT.decrypt(email))