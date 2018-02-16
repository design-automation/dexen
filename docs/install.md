---
title: Getting Started with Dexen
---

# Getting Started with Dexen

Installing Dexen either on a local network or on the Amazon is straight forward and requires minimal configuration. The user is then able to interact with Dexen via a web application in a web browser, or via an Application Programming Interface.

## Install Python

Install the latest 2.7.x version of python.
- [Python](https://www.python.org/downloads/)

Make sure that the python executable is on the enironment PATH.

## Install MongoDB

Dexen uses MongoDB as its database.
- [Install Mongodb](http://www.mongodb.org/downloads)
- Create the data folder, which by default is C:\data\db

## Install Dependencies

To install the Dexen dependency libraries, it is recommended to use the pip package manager. It is included in Python, so there is no need to install it.
- [pip](https://pip.pypa.io/en/stable/)

The following libraries are required by Dexen.
- flask (werkzeug, jinja2, markupsafe and itsdangerous packages will be automatically installed when flask is installed since these packages are dependencies of the flask package.)
- flask-login
- flask-wtf
- pymongo
- requests
- rpyc

To install all the 3rd party libraries, type the following at the command prompt:

- `$ pip install -U flask flask-login flask-wtf pymongo requests rpyc`

If you need to uninstall the libraries, you can type the following:

- `$ pip uninstall flask flask-login flask-wtf pymongo requests rpyc`

## Install Dexen

To install Dexen, follow these steps:
- [Download latest release](https://github.com/phtj/dexen/releases)
- Unzip the file anywhere
- Set up your environment. For windows users, double click the file `$ DEXEN/bin/SetWinEnv.bat`

## Start Dexen

To start Dexen:

Open the command window and do the following:
- Start mongodb: `$ start mongod`
- Start back end: `$ db`
- Start front end: `$ df`
- Start node: `$ dn`

There is also a single bat file that does all this in one. It is useful if you are running dexen on just one computer and prefer not to have lots of command windows open.
- Start everything: `$ dxn`

## View Dexen Interface

There is a UI that you can access through the browser. If you are running Dexen locally, you can access the UI at http://localhost:5000/.
- [Register](http://localhost:5000/register) (Any username and password.)
- [Login](http://localhost:5000/login)
- Start running jobs.
