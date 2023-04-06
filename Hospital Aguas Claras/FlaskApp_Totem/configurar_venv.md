# create venv:
virtualenv -p python3 venv

# run venv:
.\venv\Scripts\activate.ps1

# install pip components:
pip install -r requirements.txt

# Database relation


# Create database commands
flask db init
flask db migrate
flask db upgrade