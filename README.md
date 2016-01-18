# web_app
Web App in Python using Flask for User management.

This App is tested on Ubuntu 14.04.1


**1. Web User Creation**

First of all create a normal user e.g. web
```
sudo useradd web -m
sudo passwd web
sudo vim /etc/sudoers

web    ALL=(ALL) NOPASSWD: ALL
```

**2. Flask Installation:**

```
su - web
sudo apt-get update
sudo apt-get install python-pip git
sudo pip install virtualenv
mkdir flask
cd flask
virtualenv venv

. venv/bin/activate

sudo pip install Flask
sudo pip install https://github.com/mitsuhiko/flask/tarball/master

```

**3. Starting the App**
```
git clone https://github.com/gkbijarniya/web_app.git
cd web_app
flask -a app run --host=0.0.0.0

Now open browser and access the URL
http://IP_Address:5000
```

**4. Create/Modify/Delete Linux users along with Suodoers entry**

