# BattleSnek - Idzol 

![Battlesnake Logo](https://media.battlesnake.com/social/StarterSnakeGitHubRepos_Python.png)

---
## Resources

BattleSnake References
* [Docs](https://docs.battlesnake.com)
* [APIs](https://docs.battlesnake.com/references/api)
* [Getting started](https://docs.battlesnake.com/guides/getting-started) 
* [Snake Personalization](https://docs.battlesnake.com/references/personalization) 
* [Game Rules](https://docs.battlesnake.com/references/rules) 

IDE / Hosting 
* [Replit](https://repl.it)
* [GCP](https://console.google.com)

Files
* [server.py](server.py#L37)

Dependencies
* [Python3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/)

Gameplay 
* [Challenges](https://docs.battlesnake.com/guides/quick-start-challenges-guide)
* [Global Arena](https://play.battlesnake.com/arena/global) 

---
## Installing on server 

GCP 
* Operating System: Ubuntu 18.04.4 LTS
* Kernel: Linux 5.4.0-1053-gcp
* Architecture: x86-64
* f1-micro (1 vCPU, 0.6 GB memory)
* Intel Broadwell 

```shell
gcloud beta compute machine-images create battlesnake-image --project=eco-analog-273204 --source-instance=kubik-image-1 --source-instance-zone=us-west1-b --storage-location=us-west1`
```

SSH to VM  

Install Pyenv (optional -- not sure if rqd)
```shell
#install pyenv to install python on persistent home directory
curl https://pyenv.run | bash

# add to path
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# install python 3.7.4 and make default
pyenv install 3.7.4 # ??
pyenv global 3.7.4  # ?? 

#Update with source
source ~/.bashrc
```

Install Python 3.9

```shell
# python 3.9
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
# Enter 
sudo apt update 
sudo apt install python3.9 python3.9-venv python3.9-dev
python3.9 -V

alias python3=python3.9
# unalias python3 
python3 -V
```

Install PIP 21

```shell
# pip - #1  
python3 -m ensurepip --upgrade

# pip - #2
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py 
pip -V 			# eg. pip 21.2.4 from ..  (python 3.9)
```

Install Python vENV 

```shell
sudo apt-get install python3-venv
```

Dependencies 

```shell
pip install poetry
pip install wheel
# python3 -m poetry install
```

Code (github)

```shell
cd /home/p_kubik
mkdir battlesnake
git clone https://github.com/idzol/battlesnake temp
mv temp/* battlesnake
rm -rf temp
```

Packager

```shell
cd /home/p_kubik/battlesnake
pip install -r requirements.txt
# python3 -m pip install -r requirements.txt
```
=== Use poetry vs pip install ? ===

Permissions 
```shell
cd /home/p_kubik/battlesnake
touch games.log
sudo chown p_kubik * 
chmod 755 -R * 
```

Virtual environment 

```shell
sudo python3 -m venv env
python3 server.py
``` 

Access site 

```shell
curl http://35.213.207.57:8080
```

Healthchecks 
* [GCP Uptime Checks](https://console.cloud.google.com/monitoring/uptime?project=eco-analog-273204)
* [health.sh]

References
* [Python 3.9](https://linuxtut.com/en/cbecdf4f84f0b73ff96e/)
* [Python Alias](https://askubuntu.com/questions/320996/how-to-make-python-program-command-execute-python-3)
* [PIP v21]( https://stackoverflow.com/questions/10919569/install-a-module-using-pip-for-specific-python-version)
* [Flask](https://flask.palletsprojects.com/en/2.0.x/tutorial/deploy/)

---
## Running server (prod)

*Deploy & Run*

```shell
sudo ./build.sh
```
or
```shell
# Get code 
cd /home/p_kubik
mkdir battlesnake
git clone https://github.com/idzol/battlesnake temp
mv temp/* battlesnake
rm -rf temp
# Dependencies 
cd /home/p_kubik/battlesnake
pip install -r requirements.txt
# Permissions 
touch games.log
sudo chown p_kubik * 
chmod 755 -R * 
# Run 
cd /home/p_kubik
sudo ./kill.sh
sudo ./kill.sh
``` 

*Kill* 

```shell
sudo ./kill.sh
``` 

*Run*

```shell
sudo ./run.sh
```
or 
```shell
cd /home/p_kubik/battlesnake
sudo python3 -m venv env & 
sudo gunicorn -w 4 -b 0.0.0.0:8080 server:app &
```

---
## Running local (dev)

Run server  

```shell
# sudo python3 -m venv env
python server.py
```

```shell
python -m unittest tests.py -v
```

---
## Code Overview 

etc... 

```python
return {
    "apiversion": "1",
    "author": "",
    "color": "#888888",
    "head": "default",
    "tail": "default",
}
```
