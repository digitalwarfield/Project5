# Linux Deployment - Project 5

IP of server: 3.90.185.173
Website URL: http://project5.digitalwarfield.com

#### These are the changes that were required from Project 4 to 5
Packages Added
- Needed for Python / Postgres integration - `sudo pip install psycopg2`
- Needed for Python / Postgres - `sudo pip install psycopg2-binary`
- Needed to fix datetime in Postgres - `sudo pip install pytz`
- Flask - `sudo pip install flask`
- Requests - `sudo pip install requests`
- SQLAlchemy - `sudo pip install sqlalchemy`
- Apache - `sudo apt-get install apache2`
- Libapache2-mod-wsgi - `sudo apt-get install libapache2-mod-wsgi`
- Postgres - `sudo apt-get install postgresql`

Postres Setup Summary
- STEP 1: Switch the running user to postgres and then run psql
- STEP 2: Create the catalog database
- STEP 3: Create the catalog user with a password
- STEP 4: GRANT the catalog user to the catalog database
- STEP 5: Modify the database_setup.py script to account for changes from SQLite to Postgres
- STEP 6: Run database_setup.py to create the tables and relationships

Apache and WSGI setup summary:
- STEP 1: Create project5.wsgi to import the flask application (placing the html directory into the path)
- STEP 2: Edit /etc/apache2/sites-enabled/000-default.conf to point WSGIScriptAlias to the project5.wsgi
- STEP 3: Restart apache2

Script change summary:
- justin_warfield_project_5.py - Needed the path added to import database_setup
- justin_warfield_project_5.py - The engine needed updated with the correct DSN
- justin_warfield_project_5.py - Needed to add pytz/utc to datetime to allow for item updates
- justin_warfield_project_5.py - Removed hardcoded credentials and app.secret into app_config.json and added it to .gitignore
- database_setup.py - Removed hardcoded credentials and app.secret into app_config.json and added it to .gitignore
- database_setup.py - Removed collation='NOCASE'.  Postgres didn't like it and it wasn't needed to keep column unique
- client_secrets.json - A new oAuth key was generated and used http://project5.digitalwarfield.com instead of localhost

Device change summary:
- Change the SSH port from 22 to 2200
- Enable UFW and only allow 80, 123 and 2200
- Run apt-get update and apt-get upgrade to collect/install package updates
- Create a grader user and generate an ssh keypair for their access
- Install git to push and pull updates as required


# Item Catalog - Project 4

This project was created for Udacity Project 5.  The requirements for this project were:  

  - To create and read a SQLite database for a catalog project.
  - Provide CRUD functions for items and read functions for categories
  - Provide a JSON endpoint with the categories and their items
  - An external authentication provider should be used (Google Accounts or Mozilla Persona)
  - Only allow CUD functions when the user is logged in
  - Provide a login/logoff button
  - Must follow pep8 coding standards
  - Must include this README file
# Requirements
-[Virtualbox](https://www.virtualbox.org)
-[Vagrant](https://www.vagrantup.com/downloads.html)
-[Configuration File]("https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant")
-[client_secret.json]("https://developers.google.com/api-client-library/python/auth/web-app#creatingcred")
-An external internet connection is required for the included css and js

# External Dependencies
Login Button - https://github.com/lipis/bootstrap-social
Web formatting - https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css
Fonts - ttps://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css
JavaScript - https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js

# Environment Setup
1) Install Virtualbox
2) Install Vagrant
3) Create a Vagrant working directory
3) Download the files from "Vagrant" from "Requirements" and place the files into the Vagrant working directory
4) `cd` into the Vagrant working directory
5) Run `vagrant up` from the command line **First run will take many minutes to complete**
6) Once completed, run `vagrant ssh`
7) `cd` into /vagrant
8) Use the command `python database_setup.py` to create a new database or use the one included in the zip

# If not using Vagrant
The following dependencies are required to run this application.
1) `sudo pip install flask`
2) `sudo pip install requests`
3) `sudo pip install sqlalchemy`
# Follow Google instructions on setting up the client_secrets.json file
1) Run through the latest instructions on how to create the client_secret.json file from the "Requirements" section.  Once that has been created place that file in the same directory as justin_warfield_project_5.py
1a) For authorized JavaScript origins add http://localhost:8080
1b) For authorized redirect URIs add http://localhost:8080/gconnect

# Running the script
1) To run the script, execute `python justin_warfield_project_5.py` from the command-line

# Accessing the site
1) Open a web browser and go to http://localhost:8080

README.md created with help by dillinger.io
