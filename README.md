# Studious

## Brawns for your Brains!

Studious is a note-taking website where you can view all your classes on a calendar and organize all your classes, lectures, and notes at once. 

### Development instructions

Python and pip (the Python package manager) are required for this project. To check if you have them,
run the commands:

```
python --version
pip --version
```

If they are installed, you should get output like the following:

```
Python 3.10.9
pip 23.1.2 from some/path/here/python/site-packages/pip (python 3.10)
```

If not, you can install Python from [their website](https://www.python.org/) or pip from [here](https://pypi.org/project/pip/)

It is recommended to have a dedicated virtual environment for each project. You can follow the instructions provided [here](https://www.w3schools.com/django/django_create_virtual_environment.php) for help.

Once you have activated the environment (`env\Scripts\activate.bat` for Windows, `source env/bin/activate` for Mac/UNIX), run the following command to install all required dependencies for the project:

```
pip install -r requirements.txt
```

Django model/database migrations must also be applied (saved using the `py manage.py makemigrations` command when you change the model) before starting the server:

Windows: `py manage.py migrate` / Mac/UNIX: `python manage.py migrate`

The web app can now be started with the following command:

Windows: `py manage.py runserver` / Mac/UNIX: `python manage.py runserver`
