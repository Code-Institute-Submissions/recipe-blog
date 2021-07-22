import os
import time
from flask import (
    Flask, render_template, flash,
    request, redirect, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

recipes = mongo.db.recipes.find()


# function to retrieve file
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


# home page
@app.route("/")
def index():
    return render_template("index.html")


# sign up page
@app.route("/signup")
def signup():
    return render_template("signup.html")


# log in page
@app.route("/log-in")
def log_in():
    return render_template("login.html")


# blog page
@app.route("/blog")
def blog():
    return render_template('blog.html')


# create recipe page
@app.route("/createrecipe")
def create_recipe():
    return render_template(
        "createrecipe.html")


# recipes page
@app.route("/recipes")
def recipe():
    recipes = mongo.db.recipes.find()

    return render_template(
        "recipes.html",
        recipes=recipes)


@app.route("/recipes/<recipeName>")
def fullrecipe(recipeName):
    recipe = mongo.db.recipes.find_one({"recipeName": recipeName})

    return render_template(
                        "fullrecipe.html",
                        recipeName=recipeName,
                        recipe=recipe
                        )


# logs user out
@app.route("/logout")
def logout():
    session.pop("user")
    return render_template("index.html")


# profile page
@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    # grab the session users username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    user = mongo.db.users.find_one({"username": username})
    hasProfileImage = user['hasProfileImage']
    hasUploadedRecipe = user['hasUploadedRecipe']
    allRecipes = mongo.db.recipes.find()
    userRecipes = mongo.db.recipes.find({"author": username})
    hasPosted = user['hasPosted']

    if session["user"]:
        if hasProfileImage == "1":
            profileImage = user['profileImageName']
            if hasUploadedRecipe == "1":
                return render_template(
                    "profile.html",
                    username=username,
                    hasProfileImage=hasProfileImage,
                    profileImage=profileImage,
                    allRecipes=allRecipes,
                    userRecipes=userRecipes,
                    hasPosted=hasPosted,
                    hasUploadedRecipe=hasUploadedRecipe,
                    user=user)
            if hasUploadedRecipe == "0":
                return render_template(
                    "profile.html",
                    username=username,
                    hasProfileImage=hasProfileImage,
                    hasUploadedRecipe=hasUploadedRecipe,
                    hasPosted=hasPosted,
                    profileImage=profileImage,
                    user=user)
        else:
            if hasUploadedRecipe == "1":
                return render_template(
                    "profile.html",
                    username=username,
                    hasProfileImage=hasProfileImage,
                    allRecipes=allRecipes,
                    userRecipes=userRecipes,
                    hasPosted=hasPosted,
                    hasUploadedRecipe=hasUploadedRecipe,
                    user=user)
            if hasUploadedRecipe == "0":
                return render_template(
                    "profile.html",
                    username=username,
                    hasProfileImage=hasProfileImage,
                    hasPosted=hasPosted,
                    hasUploadedRecipe=hasUploadedRecipe,
                    user=user)

    flash("Please login to view your profile")
    return render_template("login.html", username=username, user=user)


# sign up function
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks if username exists in db
        is_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # if user exists flash message and return to login page
        if is_user:
            flash("Username already exists")
            return redirect(url_for("log_in"))

        else:
            profileImage = request.files['profilepic']
            # checks if profile image has been selected
            if profileImage:
                # generates secure filename
                securedImage = secure_filename(profileImage.filename)
                # saves file to mongodb
                mongo.save_file(securedImage, profileImage)

                # document to insert to users collection
                create_account = {
                    "profileImageName": securedImage,
                    "username": request.form.get("username").lower(),
                    "fname": request.form.get("fname").lower(),
                    "lname": request.form.get("lname").lower(),
                    "email": request.form.get("email").lower(),
                    "password": generate_password_hash(
                        request.form.get("password")),
                    "hasProfileImage": "1",
                    "hasUploadedRecipe": "0",
                    "hasPosted": "0"
                }

                # inserts new user info into users collection
                mongo.db.users.insert_one(create_account)

                newUser = mongo.db.users.find_one({
                    "username": request.form.get("username").lower()})
                hasProfilePic = newUser['hasProfileImage']
                # image variable to pass into profile page
                image = securedImage

                # creates user session cookie
                session["user"] = request.form.get("username").lower()
                # flashes message to new user
                flash("Registration Successful!")
                return redirect(url_for(
                    "profile",
                    username=session["user"],
                    image=image,
                    hasPosted="0",
                    hasProfilePic=hasProfilePic))
            # if no profile image has been selected
            else:
                # document to insert to users collection
                create_account = {
                    "username": request.form.get("username").lower(),
                    "fname": request.form.get("fname").lower(),
                    "lname": request.form.get("lname").lower(),
                    "email": request.form.get("email").lower(),
                    "password": generate_password_hash(
                        request.form.get("password")),
                    "hasProfileImage": "0",
                    "hasUploadedRecipe": "0",
                    "hasPosted": "0"}

                # inserts new user info into users collection
                mongo.db.users.insert_one(create_account)

                newUser = mongo.db.users.find_one({
                    "username": request.form.get(
                        "username").lower()})
                hasProfilePic = newUser['hasProfileImage']
                # creates user session cookie
                session["user"] = request.form.get("username").lower()
                # flashes message to new user
                flash("Registration Successful!")
                return redirect(url_for(
                    "profile",
                    username=session["user"],
                    hasPosted="0",
                    hasProfilePic=hasProfilePic))

    return render_template("signup.html")


# log in function
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        is_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if is_user:
            if check_password_hash(
                is_user["password"],
                    request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect username / password")
                return render_template("login")

    return render_template("login.html")


# edit profile picture
@app.route("/profile/<username>/edit_profile_picture", methods=["GET", "POST"])
def edit_profile_picture(username):
    user = mongo.db.users.find_one({"username": username})
    hasUploadedRecipe = user['hasUploadedRecipe']
    if request.method == "POST":
        if 'newProfilePic' not in request.files:
            flash("No file selected! Please select a file to upload.")
            return render_template("profile.html")

        if 'newProfilePic' in request.files:
            user = mongo.db.users.find_one({"username": username})
            hasProfileImage = str(user['hasProfileImage'])
            # pulls new profile pic from form
            new = request.files['newProfilePic']

            # if user has a profile image
            if hasProfileImage == "1":
                # finds old profile image
                oldProfileImage = user['profileImageName']
                # deletes old profile image from fs.files
                mongo.db.fs.files.delete_one({"filename": oldProfileImage})

                # finds record where profile image name
                # matches oldProfileImage variable
                old = mongo.db.users.find_one(
                    {"profileImageName": oldProfileImage})

                # generates secure filename
                securedImage = secure_filename(new.filename)
                # saves file to mongodb
                mongo.save_file(securedImage, new)
                # new image
                image = securedImage

                # updates image to new image
                update = {"$set": {"profileImageName": image}}

                mongo.db.users.update_one(old, update)
                # flashes message to user
                flash("Profile image successfully changed!")
                return render_template(
                    "profile.html",
                    profileImage=image,
                    user=user,
                    recipes=recipes,
                    hasProfileImage=hasProfileImage,
                    hasUploadedRecipe=hasUploadedRecipe)

            # if user doesn't have a profile pic
            if hasProfileImage == "0":
                # generates secure filename
                securedImage = secure_filename(new.filename)
                value = "1"
                # saves file to mongodb
                mongo.save_file(securedImage, new)
                # info to update
                update = {"$set": {
                    "profileImageName": securedImage,
                    "hasProfileImage": value}}
                # updates profile image name to new profile image name
                mongo.db.users.update_one(user, update)
                profileImage = securedImage
                # flashes message to user
                flash("Profile image successfully uploaded!")

                return render_template(
                    "profile.html",
                    profileImage=profileImage,
                    recipes=recipes,
                    hasProfileImage="1",
                    hasUploadedRecipe=hasUploadedRecipe,
                    user=user)
    return render_template("profile.html")


# deletes profile picture
@app.route("/profile/<username>/delete_profile_image", methods=["GET", "POST"])
def deleteProfileImage(username):
    # grabs users account
    user = mongo.db.users.find_one({"username": username})
    hasUploadedRecipe = user['hasUploadedRecipe']
    # finds profile image name
    profileImage = user['profileImageName']
    # finds profile image record
    file = mongo.db.fs.files.find_one({"filename": profileImage})
    # finds file_id
    file_id = file['_id']
    # deletes file from db
    mongo.db.fs.files.delete_one({"_id": file_id})

    value = "0"
    # changes to update
    update = {"$set": {
        "hasProfileImage": value,
        "profileImageName": " "}}

    # updates hasProfileImage in users collection
    mongo.db.users.update_one(user, update)
    return render_template(
        "profile.html",
        hasProfileImage="0",
        hasUploadedRecipe=hasUploadedRecipe,
        recipes=recipes,
        profileImage=profileImage,
        user=user)


# edits personal details
@app.route("/profile/<username>/edit_personal_details",
           methods=["GET", "POST"])
def editPersonalDetails(username):
    allRecipes = mongo.db.recipes.find()
    user = mongo.db.users.find_one({"username": username})
    hasProfileImage = user['hasProfileImage']
    hasUploadedRecipe = user['hasUploadedRecipe']

    changes = {"$set": {
        "username": request.form.get("username"),
        "email": request.form.get("email"),
        "fname": request.form.get("fname"),
        "lname": request.form.get("lname")}}

    mongo.db.users.update_one(user, changes)

    time.sleep(7)
    if hasProfileImage == "1":
        profileImage = user['profileImageName']
        return render_template(
            "profile.html",
            profileImage=profileImage,
            hasUploadedRecipe=hasUploadedRecipe,
            hasProfileImage=hasProfileImage,
            allRecipes=allRecipes,
            user=user)
    else:
        return render_template(
            "profile.html",
            hasUploadedRecipe=hasUploadedRecipe,
            hasProfileImage=hasProfileImage,
            allRecipes=allRecipes,
            user=user)

    return render_template(url_for('profile', username=username))


# create recipe form handling
@app.route("/addrecipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        # finds recipes from db
        recipeList = mongo.db.recipes.find()
        # finds username
        user = session['user']
        # finds users record
        userRecord = mongo.db.users.find_one({"username": user})
        # amend hasUploaded Recipe value on users record
        setHasUploadedRecipe = {"$set": {"hasUploadedRecipe": "1"}}

        if 'recipeImage' in request.files:
            recipeImage = request.files['recipeImage']
            securedImage = secure_filename(recipeImage.filename)
            mongo.save_file(securedImage, recipeImage)

            recipeDetails = {
                "recipeImageName": securedImage,
                "recipeName": request.form.get("recipeName"),
                "serves": request.form.get("serves"),
                "prepTime": request.form.get("prepTime"),
                "cookingTime": request.form.get("cookingTime"),
                "recipeDescription": request.form.get("recipeDescription"),
                "likes": 1,
                "author": user
            }

            mongo.db.users.update_one(userRecord, setHasUploadedRecipe)

            _id = mongo.db.recipes.insert_one(recipeDetails).inserted_id

            ingredients = {
                "recipeName": request.form.get("recipeName"),
                "recipeID": _id,
                "ingredient1": request.form.get("ingredient1"),
                "ingredient2": request.form.get("ingredient2"),
                "ingredient3": request.form.get("ingredient3"),
                "ingredient4": request.form.get("ingredient4"),
                "ingredient5": request.form.get("ingredient5"),
                "ingredient6": request.form.get("ingredient6"),
                "ingredient7": request.form.get("ingredient7"),
                "ingredient8": request.form.get("ingredient8"),
                "ingredient9": request.form.get("ingredient9"),
                "ingredient10": request.form.get("ingredient10")
            }

            mongo.db.ingredients.insert_one(ingredients)

            steps = {
                "recipeName": request.form.get("recipeName"),
                "recipeID": _id,
                "step1": request.form.get("step1"),
                "step2": request.form.get("step2"),
                "step3": request.form.get("step3"),
                "step4": request.form.get("step4"),
                "step5": request.form.get("step5"),
                "step6": request.form.get("step6"),
                "step7": request.form.get("step7"),
                "step8": request.form.get("step8"),
                "step9": request.form.get("step9"),
                "step10": request.form.get("step10")
            }

            mongo.db.steps.insert_one(steps)

    return render_template(
        "recipes.html",
        recipeList=recipeList,
        recipes=recipes)


@app.route("/search", methods=["GET", "POST"])
def search():
    option = request.form.get("select")
    if option == "recipes":
        # creates search index
        mongo.db.recipes.create_index(
            [
                ("recipeName", "text"),
                ("recipeDescription", "text"),
                ("author", "text")])

        # gets text input from search form
        query = request.form.get("search")

        # performs search
        search = ({"$text": {"$search": query}})
        # finds results
        results = mongo.db.recipes.find(search)

        return render_template(
            "searchedrecipes.html",
            results=results)

    else:
        mongo.db.users.create_index(
            [
                ("username", "text"),
                ("fname", "text"),
                ("lname", "text")])

        query = request.form.get("search")
        searchUser = ({"$text": {"$search": query}})

        results = mongo.db.users.find(searchUser)

        return render_template(
            "searcheduser.html",
            results=results)

    return url_for('index')


# Searches recipes
@app.route("/recipes/search_recipes", methods=["GET", "POST"])
def searchRecipes():
    # creates search index
    mongo.db.recipes.create_index(
        [
            ("recipeName", "text"),
            ("recipeDescription", "text"),
            ("author", "text")])

    # gets text input from search form
    query = request.form.get("search")
    # performs search
    search = ({"$text": {"$search": query}})
    # finds results
    results = mongo.db.recipes.find(search)

    return render_template(
        "searchedrecipes.html",
        results=results)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
