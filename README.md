# Studious
Brawns for your Brains!

---

Studious is a note-taking website where you can view all your classes on a calendar and organize all your classes, lectures, and notes at once. 

## Installation instructions

**ASSUMING YOU HAVE PYTHON3, PIP, GIT INSTALLED** (more detailed instructions below)

for Unix
```
git clone https://github.com/StudiousSDD/Studious.git
cd Studious
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

for Windows
```
git clone https://github.com/StudiousSDD/Studious.git
cd Studious
py -m venv env
env\Scripts\activate.bat
pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

You should now be able to access the website at http://127.0.0.1:8000

Python and pip (the Python package manager) are required for this project. To check if you have them,
run the commands:

`python --version` on Unix or `py --version` on Windows

`pip --version`

If they are installed, you should get output like the following:

```
Python 3.10.9
pip 23.1.2 from some/path/here/python/site-packages/pip (python 3.10)
```

If they are NOT installed, you can install Python from [their website](https://www.python.org/) or pip from [here](https://pypi.org/project/pip/)

It is recommended to have a dedicated virtual environment for each project. You can follow the instructions provided [here](https://www.w3schools.com/django/django_create_virtual_environment.php) for help. In general, the command will be `python -m venv [name of env]` on Unix or `py -m venv [name of env]` on Windows. For this example, we'll use the name `env`

Once you have activated the environment (`source env/bin/activate` for Unix or `env\Scripts\activate.bat` for Windows), run the following command to install all required dependencies for the project:

```
pip install -r requirements.txt
```

Django model/database migrations must also be applied (saved using the `py manage.py makemigrations` command when you change the model) before starting the server:

Mac/UNIX: `python manage.py migrate` / Windows: `py manage.py migrate`

The web app can now be started with the following command:

Mac/UNIX: `python manage.py runserver` / Windows: `py manage.py runserver`

This will run the server locally on your computer and can be accessed at http://localhost:8000 (or http://127.0.0.1:8000). The server can safely be stopped and restarted without risk of losing your work as all data is stored in a local SQLite database.
