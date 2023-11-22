# Setup Guide
## Set Up Flask App 
**1. Make sure Python 3 is installed:**

      python3 --version
      
If not install it using this command **(this will also install pip)**:
      Note: Do not install python3.12 as there are issues with pip in that version
      
      sudo apt-get install python3.11.6 python3-pip
      alias python=python3

**2. Create a virtual environment:**

      pip install virtualenv
      python -m venv .venv
      
To use the virtual environment use:

    source .venv/bin/activate
    
To deactivate it use:

    deactivate
    
**3. Install all requirements:**

    pip install -r requirements.txt
    
**4. Run the flask app:**

    flask --app hello run
Or using an environment variable:

    export FLASK_APP=sample
    export FLASK_ENV=development
    flask run

## Setting Up Postgres
### Linux(WSL):
First Download Postgres along with postgres-contriblib for some useful tools:

    sudo apt install postgresql postgresql-contrib
    
Then download the python adaptor for postgres **psycopg2**

**1.  Download a C compiler, to do so you can use:**

    sudo apt install build-essential
      
**2.  Then make sure **libpq** header files are installed:**

    sudo apt install libpq-dev
**3.  Confirm the **pg_config** program is installed:**

    pg_config --version
      
if there is an error then make sure to add it to path:

    export PATH=/usr/lib/postgresql/X.Y/bin/:$PATH

# Development Guide
## Creating tables for your models
The flask_sqlalchemy module provides a way to easily create a new table for any new models you define:

Open the flask shell by running the following from the root of the project:
```sh
flask shell
```

Then run the following lines:
```py
from reviveme import db
from reviveme import models
db.create_all()
```

Note that the `create_all` function won't recreate or update any tables that have already been created. If you make a mistake creating your new model and need to update it, you'll have to drop the table and run `db.create_all()` again. Avoid doing this to update any models we've already committed though; create a database migration instead.
## Creating and Running Migrations
The flask_migrate module allows us to easily generate migrations and run them with ease

**To create migration scripts from the app automatically use:**
```
flask db migrate
OR
flask db migrate -m "{table_name} table"
```
These commands will generate the migration scripts and must be incorporated via source control

**To apply the changes use:**
```
flask db upgrade
```
For more info on using migration commands refer to this [blog](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)
## Running Scripts

To run scripts from the app use:
```
python -m reviveme.scripts.{script_to_run}
```
