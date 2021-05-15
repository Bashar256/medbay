from website import app
from website.models import Hospital
from website.temp_create_objects import create_stuff

if __name__ == "__main__":
    if not Hospital.query.all():
        create_stuff()
    app.run(debug=True, host="0.0.0.0", port=5000)
