from website import app

if __name__ == "__main__":
    app.run(debug=True)


# @app.template_global()
# def static_include(filename):
#     fullpath = os.path.join(app.static_folder, filename)
#     print(fullpath)
#     return fullpath