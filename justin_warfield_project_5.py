from flask import (Flask,
                   render_template,
                   url_for,
                   request,
                   redirect,
                   jsonify,
                   flash)
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import string
import os
from flask import session as login_session
from functools import wraps
from datetime import datetime
from sqlalchemy.pool import SingletonThreadPool

import sys
# Add the working path so we can call database_setup
working_path = "/var/www/html"
sys.path.append(working_path)

from database_setup import Categories, Items, Users
import uuid


app = Flask(__name__)
# Collect db logins and flask secret key from config file
try:
    app_config_file = open("/var/www/html/app_config.json", "r")
    app_config = json.load(app_config_file)
    user = app_config["db_user"]
    password = app_config["db_pass"]
    database = app_config["db_database"]
    app.secret_key = app_config["app_secret"]
except Exception:
    print("Failed to open app_config.json file")
    raise

#engine = create_engine('sqlite:///catalog.db',
#                       connect_args={'check_same_thread': False})
database_params = "postgresql://{}:{}@localhost/{}".format(user,password,database)
Session = sessionmaker(bind=engine)
session = Session()


# http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
def authorized(calling_function):
    """
    Performs a check to make sure the login_session["email"] is set.
    If that variable is set then we know the user authenticated.  If
    the user gets to this page and isn't logged in they will be shown
    a json message stating as such.

    Returns:
    The paramaters that were sent to the authorized function.
    """
    @wraps(calling_function)
    def authorized_function(*args, **kwargs):

        if 'email' not in login_session:
            return jsonify({'Error': 'You must be logged in to access \
                            this page'}), 401
        return calling_function(*args, **kwargs)
    return authorized_function


@app.route("/login", methods=['GET'])
def login():
    """
    https://developers.google.com/identity/protocols/OpenIDConnect#sendauthrequest
    Step 1: Create state state variable, login_session["state"],
    for anti-forgery token protection
    Step 2: Redirect the user to Google to have them authenticate their login

    Returns:
    None: Redirect to Google.  Google will send them back to /gconnect
    """
    try:
        secrets_file = open("client_secrets.json", "r")
        json_secrets = json.load(secrets_file)
        client_id = json_secrets["web"]["client_id"]
        redirect_uri = json_secrets["web"]["redirect_uris"][0]
    except Exception:
        return (jsonify({"Error": "Failed to read client_secrets.json"}
                        ), 500)
    login_session["state"] = str(uuid.uuid4()).replace("-", "")
    nonce = str(uuid.uuid4()).replace("-", "")
    request = "https://accounts.google.com/o/oauth2/v2/auth\
               ?client_id={}\
               &response_type=code\
               &access_type=offline\
               &scope=openid%20email%20profile\
               &redirect_uri={}\
               &state={}\
               &nonce={}".format(client_id,
                                 redirect_uri,
                                 login_session["state"],
                                 nonce)
    return redirect(request.replace(" ", ""))


@app.route("/gconnect", methods=['GET', 'POST'])
def gconnect():
    """
    https://developers.google.com/identity/protocols/OpenIDConnect#sendauthrequest
    Step 3: Validate anti-forgery state token is the same we know about
    Step 4: Exchange the code received for the access and ID token
    Call https://www.googleapis.com/oauth2/v1/userinfo with the access_token
    from "Step 4" to retreive the users information
    Save those variables into login_session so we can reference them throughout
    the portal.
    Returns:
    sets login_session["email|picture|full_name"] and returns to the main page
    """
    if request.args.get("state") == login_session["state"]:
        try:
            secrets_file = open("client_secrets.json", "r")
            json_secrets = json.load(secrets_file)
            client_id = json_secrets["web"]["client_id"]
            client_secret = json_secrets["web"]["client_secret"]
            redirect_uri = json_secrets["web"]["redirect_uris"][0]
        except Exception:
            return (jsonify({"Error": "Failed to read client_secrets.json"}
                            ), 500)
        code = request.args["code"]
        post_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post("https://www.googleapis.com/oauth2/v4/token",
                                 post_data)
        try:
            login_session["credentials"] = response.json()
            get_user_info_data = {
                "access_token": response.json()["access_token"]
            }
            user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            response = requests.get(user_info_url,
                                    get_user_info_data)
            if (response.status_code == 200):
                response = response.json()
                login_session["email"] = response["email"]
                login_session["picture"] = response["picture"]
                login_session["full_name"] = "{} {}"\
                                             .format(response["given_name"],
                                                     response["family_name"])
                try:
                    user_id = session.query(Users)\
                                     .filter_by(email=login_session["email"])\
                                     .one()
                except Exception:
                    user_info = Users(email=login_session["email"],
                                      full_name=login_session["full_name"],
                                      picture=login_session["picture"])
                    session.add(user_info)
                    session.commit()
                    user_id = session.query(Users)\
                                     .filter_by(email=login_session["email"])\
                                     .one()
                print(user_id.user_id)
                login_session["user_id"] = user_id.user_id
                flash("Login Successful", "info")
            else:
                flash("Did not get a valid response from Google. \
                      Please try again", "error")
        except Exception:
            flash("Login to get access_token.  Please try again", "error")
    return redirect(url_for('mainPage'))


@app.route('/revoke')
def revoke():
    """
    https://developers.google.com/identity/protocols/OAuth2WebServer#tokenrevoke
    This is the logout function.  This will attempt to revoke the oauth
    token Google knows about as well as destry to login_session varaibles
    that are used to keep the user logged in.

    Returns:
    Redirect to the homepage
    """
    try:
        revoke_url = "https://accounts.google.com/o/oauth2/revoke?token={}"\
                     .format(login_session["credentials"]["access_token"])
        revoke = requests.get(revoke_url,
                              headers={'content-type':
                                       'application/x-www-form-urlencoded'})
        if (revoke.status_code == 200):
            flash("Logout Successful", "info")
        else:
            flash("Google token no longer valid.", "error")
        if 'credentials' in login_session:
            del login_session['credentials']
            del login_session['email']
            del login_session['picture']
            del login_session['full_name']
            del login_session['user_id']
    except Exception:
        flash("Logout Failed", "error")
    return redirect(url_for('mainPage'))


@app.route("/", methods=['GET'])
def mainPage():
    """
    This is the main homepage for the application.  It'll display the
    current known categories as well as the last 10 modified items.  If
    the user is logged in it'll also display the ability to add an item
    or category.

    Returns:
    Homepage
    """
    categories = session.query(Categories).order_by(Categories.name)
    latest_items = session.query(Items.title, Categories.name)\
                          .join(Categories,
                                Items.cat_id == Categories.cat_id)\
                          .order_by(Items.last_update.desc())\
                          .limit(10).all()
    return (render_template("main.html",
                            categories=categories,
                            login_session=login_session,
                            latest_items=latest_items))


@app.route("/addCategory", methods=['GET', 'POST'])
@authorized
def addCategories():
    """
    This page is used to add a category to the portal.  The user must
    be logged in to access this page.

    Returns:
    The add category page will be displayed if the page was accessed
    through a GET request.  If it was a POST request the new category
    will attempt to be added and then the user redirect to the main
    page.
    """
    if request.method == 'POST':
        if request.form["category"]:
            category = Categories(name=request.form["category"],
                                  user_id=login_session["user_id"])
            try:
                session.add(category)
                session.commit()
                flash("New category created!", 'info')
                return redirect(url_for('mainPage'))
            except Exception:
                session.rollback()
                flash("Category already exists.  Please choose a new name.",
                      "error")
                session.rollback()
        else:
            flash("Category Name is a required field", "error")
    return (render_template("addcategory.html", login_session=login_session))


@app.route("/removeCategory/<cat_name>", methods=['GET', 'POST'])
@authorized
def removeCategory(cat_name):
    """
    This page is used to remove a category from the portal.  The user must
    be logged in to access this page.

    Returns:
    The remove category page will be displayed if the page was accessed
    through a GET request.  If it was a POST request the category
    will attempt to be removed and then the user redirect to the main
    page.
    """
    if request.method == 'POST':
        try:
            category = session.query(Categories).filter_by(name=cat_name).one()
            # Validate that the user is removing a category that they created
            # and not attempting to delete one they didn't create
            if login_session["user_id"] == category.user_id:
                session.delete(category)
                session.commit()
                flash("Category was removed!", 'info')
            else:
                flash("You can only remove a category you created!", "error")
            return redirect(url_for('mainPage'))
        except Exception:
            session.rollback()
            flash("Failed to remove category", 'error')
    return (render_template("removecategory.html",
                            cat_name=cat_name,
                            login_session=login_session))


@app.route("/addItem", methods=['GET', 'POST'])
@authorized
def addItem():
    """
    This page is used to add an item to an existing category.  The user must
    be logged in to access this page.

    Returns:
    The add item page will be displayed if the page was accessed
    through a GET request.  If it was a POST request the new item
    will attempt to be added and then the user redirect to the main
    page.
    """
    if request.method == 'POST':
        # Validate if the user is attempting to add and item to a
        # category that they own
        try:
            session.query(Categories)\
                   .filter_by(user_id=login_session["user_id"],
                              cat_id=request.form['category'])\
                   .one()
        except Exception:
            flash("Items can only be added to your categories!", "error")
            return redirect(url_for('mainPage'))
        # Used to see if all the required fields were in the POST request
        error = 0
        if not request.form['title']:
            flash("Title is a required field", "error")
            error = 1
        if not request.form['description']:
            flash("Description is a required field", "error")
            error = 1
        if not request.form['category']:
            flash("Category is a required field", "error")
            error = 1
        # All required fields added, proceed
        if error == 0:
            item = Items(title=request.form['title'],
                         description=request.form['description'],
                         cat_id=request.form["category"],
                         last_update=datetime.now(),
                         user_id=login_session["user_id"])
            try:
                session.add(item)
                session.commit()
                flash("Item Added!", "info")
                return redirect(url_for('mainPage'))
            except Exception:
                session.rollback()
                flash("Duplicate item found or category doesn't exist.",
                      "error")
    categories = session.query(Categories)\
                        .filter_by(user_id=login_session["user_id"])\
                        .order_by(Categories.name).all()
    if not categories:
        flash("No categories found.  Please set one up first.", 'error')
        return redirect(url_for('addCategories'))
    return (render_template("additem.html",
                            categories=categories,
                            form_data=request.form,
                            login_session=login_session))


@app.route("/viewCategory/<cat_name>")
def viewCategory(cat_name):
    """
    This page is used to view the items in a category.

    Returns:
    The items associated to this category will be displayed on the screen.
    """
    try:
        category = session.query(Categories).filter_by(name=cat_name).one()
    except Exception:
        flash("Failed to find category with the requested name", 'error')
        return redirect(url_for('mainPage'))
    items = session.query(Items).join(Categories,
                                      Items.cat_id == Categories.cat_id)\
                                .filter_by(name=cat_name).all()
    return (render_template('viewcategory.html',
                            category=category,
                            items=items,
                            login_session=login_session))


@app.route("/catalog.json")
def jsonOutput():
    """
    This page is used to display the Catalog as a JSON output.

    Returns:
    It will be a JSON output of the Categories and the Items in them.
    """
    catalog = session.query(Categories,
                            Items)\
                     .outerjoin(Items,
                                Categories.cat_id == Items.cat_id)\
                     .order_by(Categories.cat_id,
                               Items.item_id).all()
    # The dictionary used to append categories/items for the final jsonify call
    dict = []
    # This is used to add all items for a category so
    # we can add them all at the end
    items = []
    # Used to combine the category and item information into one object
    json_element = {}
    # Used to see if this is the first category so we don't
    # display a empty JSON object
    first = True
    # Used to remember what the last category was so we
    # know when we see a new one.
    last_catagory = ""
    for result in catalog:
        # Checking if it is a new category
        if last_catagory != result.Categories.name:
            # Make sure this isn't the first change in category
            if not first:
                if items:
                    json_element.update({"Items": items})
                    dict.append(json_element)
                    items = []
                # No items found.  Just append the category information
                else:
                    dict.append(json_element)
            first = False
            json_element = result.Categories.serialize
            if result.Items is not None:
                # Item found, add it to the array for later use.
                items.append(result.Items.serialize)
            last_catagory = result.Categories.name
        # Item found and is the same category, add it to
        # the array for later use.
        else:
            if result.Items is not None:
                items.append(result.Items.serialize)
    # Add the information from the last category
    # now that we're out of the loop.
    if items:
        json_element.update({"Items": items})
        dict.append(json_element)
        items = []
    else:
        dict.append(json_element)
    return jsonify(dict)


@app.route("/item/<cat_name>/<item_name>/<action>", methods=['GET', 'POST'])
def item(cat_name, item_name, action):
    """
    This page is used to display, update or delete an item from the portal.

    Returns:
    ACTION/view: Display the item with it's description
    ACTION/edit: Display the item with editable fields and attempt to update
                 if it was a POST request.
    ACTION/delete: Display a confirmation page and if it's a POST attempt to
                   delete the item.
    """
    try:
        item = session.query(Items.item_id,
                             Items.title,
                             Items.description,
                             Items.cat_id,
                             Items.user_id,
                             Categories.name)\
                      .join(Categories,
                            Items.cat_id == Categories.cat_id)\
                      .filter(Categories.name == cat_name,
                              Items.title == item_name).one()
    except Exception:
        flash("No item was found", 'error')
        return redirect(url_for('mainPage'))
    if request.method == "POST":
        try:
            # Validate that the category and item are both owned
            # by the same user that created them
            item = session.query(Items.item_id,
                                 Items.title,
                                 Items.description,
                                 Items.cat_id,
                                 Items.user_id,
                                 Categories.name)\
                          .join(Categories,
                                Items.cat_id == Categories.cat_id)\
                          .filter(Categories.name == cat_name,
                                  Items.title == item_name,
                                  Categories.user_id ==
                                  login_session["user_id"],
                                  Items.user_id ==
                                  login_session["user_id"])\
                          .one()
        except Exception:
            if action == "delete":
                flash("You can only delete items you created!", "error")
            else:
                flash("You can only edit items/categories you created!",
                      "error")
            return redirect(url_for('mainPage'))
        if action == "delete":
            try:
                found_item = session.query(Items).filter_by(
                                           item_id=item.item_id).one()
                session.delete(found_item)
                session.commit()
                flash("Item was removed", "info")
                return redirect(url_for('viewCategory', cat_name=item.name))
            except Exception:
                session.rollback()
                flash("Item removal failed!", "error")
                return redirect(url_for('viewCategory', cat_name=item.name))
        if action == "edit":
            found_item = session.query(Items).filter_by(
                                       item_id=item.item_id).one()
            if request.form['title']:
                found_item.title = request.form['title']
            if request.form['description']:
                found_item.description = request.form['description']
            if request.form['category']:
                found_item.cat_id = request.form['category']
                found_item.last_update = datetime.now()
            try:
                session.add(found_item)
                session.commit()
                flash("Successful item edit", "info")
                return redirect(url_for('mainPage'))
            except Exception:
                session.rollback()
                flash("Failed item edit", "error")
                return redirect(url_for('mainPage'))

    if action == "edit":
        categories = session.query(Categories)\
                            .filter_by(user_id=login_session["user_id"])\
                            .order_by(Categories.name).all()
        return (render_template("edititem.html",
                                item=item,
                                categories=categories,
                                login_session=login_session))
    elif action == "delete":
        return (render_template("deleteitem.html",
                                item=item,
                                login_session=login_session))
    else:
        return (render_template("viewitem.html",
                                item=item,
                                login_session=login_session))
