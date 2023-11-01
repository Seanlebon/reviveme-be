from flask import Flask, send_from_directory
import os
app = Flask(__name__)

static_directory = os.getcwd() + f'/build/static'

@app.route('/')
def index():
    '''Landing page'''
    build_dir = os.getcwd() + f'/build'
    return send_from_directory(directory=build_dir, path='index.html')

@app.route('/static/<folder>/<file>')
def static_files(folder, file):
    '''Serves the contents of the static directory'''
    path = os.path.join(folder, file)
    return send_from_directory(directory=static_directory, path=path)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
