# NAVIGATION_APP2

**Author:** C. Mauricio Arteaga-Escamilla from "Robotica Posgrado"
**Contact email:** cmauricioae8@gmail.com<br>


Flet application to manage modes of control for an autonomous mobile robot. Since it is assumed that octy_bridge2 ROS 2 package is running (Server for both HTTP and SocketIO communications methods), ROS 2 is NOT required. 


## Installation using a virtual environment (recommended)

Pre-requisites:
```
python3 -m pip install --upgrade pip venv
sudo apt install libmpv1
```

_libmpv1_ is installed to solve the following error:<br>
"error while loading shared libraries: libmpv.so.1: cannot open shared object file: No such file or directory"


Change directory to this path (~/navigation_app2)
```
cd ~/navigation_flet_app
python3 -m venv venv            #Create virtual env called venv
source venv/bin/activate        #Activate the venv
pip install -r requirements.txt #Install requirements
```

For a simple flet app, a virtual environment is not necessary, flet is required only. It can be installed using `pip3 install install flet==0.28.3`.

If your project grows, use `pip freeze > requirements.txt` to generate the corresponding requirements.txt file.


## Run the app

In order to run this app as a desktop app, use:

```
cd ~/navigation_app2            #change directory
source flet_env/bin/activate    #active virtual env, if applicable
flet main.py                    #run as a desktop application
```

To run this application, using another port, or as a web server, or as a mobile app, use:

```
flet main.py --port 8551 --<web,android,ios>
```

To connect to the android app from phone, first it is required to install flet in the phone.
Then, open flet app and scan the QR code or type the following url:

`
http://<server_ip>:<port>/navigation_app2/main.py
`

For example
```
http://10.4.40.200:8551/navigation_app2/main.py
```
