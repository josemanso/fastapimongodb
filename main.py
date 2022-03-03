from typing import Optional

from fastapi import  FastAPI
import connection
from bson import ObjectId
from json import dumps
from schematics.models import Model
from schematics.types import StringType, EmailType

class User(Model):
    user_id = ObjectId()
    email = EmailType(required=True)
    name = StringType(required = True)
    password = StringType(required=True)

# An instance of clas User
newuser = User()

# function to create and assing values to the instance of class User create
def create_user(email, username, password):
    newuser.user_id = ObjectId()
    newuser.email = email
    newuser.name = username
    newuser.password = password
    return dict(newuser)

# A method to check if the email parameter exists from
# user database before validation of details
def email_exists(email):
    user_exist = True
    # counts the number of times the email exits,
    # if it equals 0 it means the email doesn't exist in the database
    if connection.db.users.find({'email': email}).count() == 0:
        user_exist = False
        return user_exist
# Reads user detail from database and ready for validation
def check_login_creds(email, password):
    if not email_exists(email):
        activeuser = connection.db.user.find({'email': email})
        for actuser in activeuser:
            acturser = dict(actuser)
            # Converted the user ObjectId to string so this can be stored into a session(how login works)
            acturser['_id'] = str(actuser['_id'])
            return actuser

app = FastAPI()

# Our root endpoint
@app.get("/")
def index():
    return {"message": "Hello World" }

#Signup endpoint with the POST method
@app.post("/signup/émail}/{username}/{password}")
def signup(email, username: str, password: str):
    user_exists = False
    data = create_user(email, username, password)

    # Covert data to dict so it can be easily inserted to MongoDB
    dict(data)

    # Checks if an email exists from the collection of user
    if connection.db.user.find({'email' : data['email']}).count() > 0:
        user_exists = True
        print("User Exists")
        return {"message": "User Exists"}
    # If the email doesn't exist, create the user
    elif user_exists == False:
        connection.db.user.insser_one(data)
        return {"message":"User Created", "email": data['email'], "name":data['name'],
                "pass": data['password']}

# Login endpoint
@app.get("/login/{email}/{password}")
def login(email, password):
    def log_user_in(creds):
        if creds['email'] == email and creds['password'] == password:
            return{"message": creds['name'] + ' successfully logged in '}
        else:
            return {"message": "Invalid credentials!!"}
        # Read email from database to validate if user exists and check if password matches
        logger = check_login_creds(email.password)
        if bool(logger) != True:
            if logger == None:
                logger = "Invalid Email"
                return{"message":logger}
            else:
                status = log_user_in(logger)
                return{"Info":status}


