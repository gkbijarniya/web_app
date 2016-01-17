from flask import Flask, render_template, request, url_for
import sys
import subprocess
import re
import os
import tempfile

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('form_submit.html')

@app.route('/user', methods=['POST'])
def user():
#get the form data
    username=request.form['username']
    shell=request.form['shell']
    homedir=request.form['homedir']
    passwd=request.form['password']
    sudo=request.form['sudo']
    action=request.form['dropdown']

# check if user is already exist or not
    userExist=isUserExist(request.form['username'])

# take the action
    if action == "Create":
        if userExist: #if user already exist nothing to do
            msg1="User " + str(username) + " already exist!"
        else: #add requested user
            returnCode=addUser(username,shell,homedir,passwd)
            if returnCode:
                msg1="User " + str(username) + " added!"
            else:
                msg1="User " + str(username) + " doesn't added!"
          
    elif action == "Modify":
        if userExist: # modify the user if exist
            returnCode=modUser(username,shell,homedir,passwd)
            if returnCode:
                msg1="User " + str(username) + " modified!"
            else:
                msg1="User " + str(username) + " doesn't modified!"
        else:
            msg1="User " + str(username) + " doesn't exist!"

    elif action == "Delete":
        if userExist: # delete user if exist
            returnCode=delUser(username)
            if returnCode:
                msg1="User " + str(username) + " deleted!"
            else:
                msg1="User " + str(username) + " doesn't deleted!"
        else:
            msg1="User " + str(username) + " doesn't exist!"

#now it's time for sudo
    msg2=""
    userExist=isUserExist(request.form['username']) # for sudo check if user exist
    temp=tempfile.NamedTemporaryFile()
    sudoersFile=temp.name
    os.system("sudo cp /etc/sudoers " + temp.name) # normal user doesn't have permission to read and modify so first create a temp file for sudoers
    sudo_entry= username + "\tALL=(ALL) ALL\n" # if sudo entry need to insert use it.
    sudoer = open(sudoersFile, "r")
    regex = re.compile(username + ".+=.+ALL")
    for line in sudoer: #check if a sudo entry is exist of not
        sudo_entryMatch = regex.findall(line)
        if sudo_entryMatch: # if sudo entry found exit the loop
            break
    sudoer.close
    if action == "Create" and sudo == "Yes" and userExist:
        if sudo_entryMatch: #if sudo entry found then no need to add it
            msg2="sudo entry Found: " + str(sudo_entryMatch)
        else: #else if sudo entry not found then add it
            msg2="Sudo entry Not Found, adding entry: " + sudo_entry 
            add_sudo(sudo_entry,sudoersFile)
            os.system("sudo cp " + temp.name +" /etc/sudoers")

    elif action == "Modify" and userExist:
        if sudo_entryMatch and sudo == "No": # if sudo entry found but selected NO for sudo then delete it.
            msg2="sudo entry Found, deleting: " + str(sudo_entryMatch)
            del_sudo(regex,sudo_entryMatch,sudoersFile)
            os.system("sudo cp " + temp.name +" /etc/sudoers")
        elif not sudo_entryMatch and sudo == "Yes":
            msg2="Sudo entry Not Found, adding entry: " + sudo_entry 
            add_sudo(sudo_entry,sudoersFile)
            os.system("sudo cp " + temp.name +" /etc/sudoers")
        elif sudo_entryMatch and sudo == "Yes":
            msg2="Sudo entry Found" 
        elif not sudo_entryMatch and sudo == "No":
            msg2="Sudo not required" 

    elif action == "Delete" and userExist:
        if sudo_entryMatch: # if action is user delete then delete sudo entry 
            msg2="sudo entry Found, deleting: " + str(sudo_entryMatch)
            del_sudo(regex,sudo_entryMatch,sudoersFile)
            os.system("sudo cp " + temp.name +" /etc/sudoers")
        else:
            msg2="nothing for sudo entry"

    temp.close() 
    
    return render_template('form_action.html', message1=msg1, message2=msg2, username=username)

def command(cmd): # method to execute the system commands
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out,err = p.communicate()
    if p.returncode == 0:
        return True
    else:
        return False

def passencrypt(cmd): # encrypt the password 
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out,err = p.communicate()
    return out 

def isUserExist(user): # check if user is exist or not
    cmd = ["id", user]
    rcode=command(cmd)
    print rcode
    return rcode

def addUser(username,shell,homedir,passwd): # add a system user using system commands
    passoutput=passencrypt(["/usr/bin/sudo", "/usr/bin/openssl", "passwd", "-crypt", str(passwd)])
    returnCode=command(["/usr/bin/sudo", "/usr/sbin/useradd", "-m", "-d", str(homedir), "-s", str(shell), "-p", str(passoutput.strip()), username])
    print username,shell,homedir,passwd
    return returnCode

def modUser(username,shell,homedir,passwd): # modify a system user using system commands
    passoutput=passencrypt(["/usr/bin/sudo", "/usr/bin/openssl", "passwd", "-crypt", str(passwd)])
    returnCode=command(["/usr/bin/sudo", "/usr/sbin/usermod", "-d", str(homedir), "-s", str(shell), "-p", str(passoutput.strip()), username])
    print username,shell,homedir,passwd
    return returnCode

def delUser(username): # delete user
    returnCode=command(["/usr/bin/sudo", "/usr/sbin/userdel", "-r", username])
    return returnCode

def add_sudo(sudo_entry,sudoersFile): # add sudo entry
    sudoer = open(sudoersFile, "a")
    sudoer.write(sudo_entry)
    sudoer.close()

def del_sudo(regex,sudo_entryMatch,sudoersFile): # delete sudo entry 
    sudoer = open(sudoersFile, "r")
    lines = sudoer.readlines()
    sudoer.close()
    sudoer = open(sudoersFile, "w")
    matchLine=sudo_entryMatch[0] + "\n"
    for line in lines:
        if line != matchLine:
            sudoer.write(line)
    sudoer.close()


# Run the app :)
if __name__ == '__main__':
    app.run 

