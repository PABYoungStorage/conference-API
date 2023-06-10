from flask import Blueprint, current_app, jsonify,request
from .lib.mailservice import MailSender
from werkzeug.security import generate_password_hash, check_password_hash
import random
from bson import ObjectId

# Create blueprint for authentication routes
auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

@auth_routes.post('/signin')
def signin():
    # Implement signin logic here
    return jsonify({"message":"signin","method":request.method})

@auth_routes.post('/signup')
def signup():
    data = request.get_json()
    email = data.get('email')
    db = current_app.config['MONGO']
    if not email:
        return {"message":"Enter Email First","status":False}

    if db.user.find_one({'email': email}):
        return {"message":"Email already exists","status": False}
    else:
        otp = random.randint(100000, 999999)
        otp_insert = db.userauth.insert_one({'otp': otp})
        send_email(email,otp)
        return jsonify({'message': 'OTP Sent To Your Email',"status": True}), 201

@auth_routes.route("/email_verify")
def email_verify():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')
    db = current_app.config['MONGO']
    if not otp or not email:
        return {"message":"Enter All Fields","status":False}
    
    if db.userauth.find_one({'email': email ,'otp': otp}):
        db.userauth.update_one({'email': email,'otp': otp},{ "$unset": { "otp": "" } })
        return {"message":"OTP Verified Successfully","status": True}
    else:
        return {"message":"Enter Correct OTP"}
    
@auth_routes.post("/details")
def details():
    db = current_app.config['MONGO']
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_pwd = data.get('confirm_pwd')

    if not username or not email or not password or not confirm_pwd:
        return {"message":"Please Enter All Fields","status":False}

    if db.user.find_one({'username': username}):
        return {"message":"Username Or Email Already Exists","status": False}
    elif db.user.find_one({'email':email}) and password == confirm_pwd:
        hash_pwd = generate_password_hash(password) 
        db.user.update_one({'email': email},{ "$set": {"username": username,"password": hash_pwd}})
        return {"message":"Details Successfully Inserted","status":True}
    


@auth_routes.route('/signout')
def signout():
    # Implement signout logic here
    return jsonify({"message":"signout"})



# Create blueprint for main routes
main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    # Access the MongoDB instance using the Flask app's context
    db = current_app.config['MONGO']

    # Access a collection and perform operations
    collection = db.users
    data = collection.find_one()
    print(data)
    return jsonify({"message":"root"})

@main_routes.route('/send_email')
def send_email(email,otp):
    # Access the Mail instance using the Flask app's context
    mail = current_app.config['MAIL']
    to = f"{email}"
    body = f"{otp}"
    message = "OTP Testing"

    MailSender(mail,to,body,message)
   

    return jsonify({"message":"Email sent"})
