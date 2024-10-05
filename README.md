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

You can access it as http://<ip_address>:5000. Admin Credential (Make sure change admin password.):
```
username: admin
username: Admin@123
```

Create a service to run at startup by following below -

###########################
1. Create script that execute required steps

```
 sudo nano /full_path_to_ctf/ctf_app/start_ctf.sh

 #!/bin/bash
 source ctf_env/ctf_env/bin/activate
 cd /full_path_to_ctf/ctf_app/
 python3 app.py
```
2. Allow execute permission
```
 chmod +x /path_to_ctf/ctf_app/start_ctf.sh
```
3. Create service file
```
sudo nano /etc/systemd/system/ctf.service

[Unit]
Description=CTF Service
After=network.target

[Service]
User=<user_name>
ExecStart=/full_path_to_ctf/ctf_app/start_ctf.sh
WorkingDirectory=/full_path_to_ctf/ctf_app/
Restart=always
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
```
4. Enable and start service
```
sudo systemctl daemon-reload
sudo systemctl start ctf.service
sudo systemctl status ctf.service
sudo systemctl enable ctf.service

```
###########################
