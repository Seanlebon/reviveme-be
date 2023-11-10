# reviveme-be
## Setting Up App
**1. Make sure Python 3 is installed:**
    `python3 --version`
    If not install it using this command(this will also install pip): 
    `sudo apt-get install python3.8 python3-pip`
    `alias python=python3`
**2. Create a virtual environment:**
    `pip install virtualenv`
    `python -m venv .venv`
    To use the virtual environment use:
    `source .venv/bin/activate`
    To deactivate it use:
    `deactivate`
**3. Install all requirements:**
    `pip install -r requirements.txt`
**4. Run the flask app:**
    `flask --app hello run`
    Or using a environment variable:
    export FLASK_APP=sample
    export FLASK_ENV=development
    flask run

## Setting Up Postgres
### Linux(WSL):
First Download Postgres along with postgres-contriblib for some useful tools:
    `sudo apt install postgresql postgresql-contrib`
Then download the python adaptor for postgres **psycopg2**
**1.  Download a C compiler, to do so you can use:**
    `sudo apt install build-essential`
**2.  Then make sure **libpq** header files are installed: **
    `sudo apt install libpq-dev`
**3.  Confirm the **pg_config** program is installed:**
    `pg_config --version`
    if there is an error then make sure to add it to path: 
    `export PATH=/usr/lib/postgresql/X.Y/bin/:$PATH`