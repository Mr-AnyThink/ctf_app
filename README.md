# ctf_app

Create Virtual Environment
###########################

```
sudo apt install python3-venv -y
mkdir ctf_env
python3 -m venv ctf_env
source ctf_env/ctf_env/bin/activate
```
Install CTF APP
###########################
```
git clone https://github.com/Mr-AnyThink/ctf_app.git
cd ctf_app
pip3 install -r requirement.txt
python3 app.py
```

Admin Credential:
```
username: admin
username: Admin@123
```

To change admin password, find below code in app.py and modify "Admin@123", before running the app first time as it gets created when application get lanuched.

```
# Initialize the database
@app.before_request
def create_admin():
    .
    .
            hashed_password = generate_password_hash('Admin@123')
            new_admin = User(username='admin', password=hashed_password, is_admin=True)  # Include a password field
    .
    .
```

If you want to change it after you lauched the app, delete ctf.db from folder "instance" (It'll get created when you launch the). Update the password and re-run. Note deleting ctf.db will delete all change and start as fresh instance.

###########################
