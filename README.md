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
