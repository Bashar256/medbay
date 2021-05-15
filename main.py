from website import app,db
from website.temp_create_objects import create_stuff

if __name__ == "__main__":
    if not db.session.query():
        create_stuff()
    app.run(debug=True, host="0.0.0.0", port=5000)
