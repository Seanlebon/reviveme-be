from flask import Flask, send_from_directory
import os
app = Flask(__name__)

react_folder = 'src'
directory = os.getcwd() + f'f{react_folder}/build/static'

@app.route('/')
def index():
    '''Landing page'''
    build_dir = os.getcwd() + f'/{react_folder}/build'
    return send_from_directory(directory=build_dir, path='index.html')

@app.route('/static/<folder>/<file>')
def static_files(folder, file):
    '''Serves the contents of the static directory'''
    path = os.path.join(folder, file)
    return send_from_directory(directory=directory, path=path)
