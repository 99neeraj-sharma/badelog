from flask import Flask,url_for,render_template,request,  redirect,url_for, flash,abort
from flask_login import LoginManager , login_required , UserMixin , login_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer, SignatureExpired

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return None

class User(UserMixin):
    def __init__(self , first , last , email , password , id , active=False):
        self.id = id
        self.first = first
        self.last = last
        self.email = email
        self.password = password
        self.active = active

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.email , key='secret_key')

class UsersRepository:

    def __init__(self):
        self.users = dict()
        self.users_id_dict = dict()
        self.identifier = 0
    
    def save_user(self, user):
        self.users_id_dict.setdefault(user.id, user)
        self.users.setdefault(user.email, user)

    def get_email(self, email):
        return self.users.get(email)    
    
    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)
    
    def next_index(self):
        self.identifier +=1
        return self.identifier

users_repository = UsersRepository()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'neera99j@gmail.com'           #use your gmail ID
app.config['MAIL_PASSWORD'] = '145518110gmail'	#Use Password of gmail ID
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)

@app.route("/", methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        registeredUser = users_repository.get_email(email)
        if registeredUser != None and registeredUser.password == password and registeredUser.active == True:
            print('Logged in..')
            login_user(registeredUser)
            return "successfull login"
        else:
            return abort(401)
    else:
        return render_template("home.html")

string = "b17100@students.iitmandi.ac.in"   #default webmail 
@app.route("/signup",methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        firstName = userDetails['firstName']
        lastName = userDetails['lastName']
        email = userDetails['email']
        global string
        string = email
        password = userDetails['password']
        new_user = User(firstName , lastName , email , password , users_repository.next_index())
        users_repository.save_user(new_user)
        return redirect(url_for('verification_page'))

    return render_template("signup.html")

token=""
random_URL = URLSafeSerializer('secret_key')
@app.route("/verification_page")
def verification_page():
    global random_URL
    random_URL = URLSafeSerializer('secret_key')
    global token
    token = random_URL.dumps(string, salt='email-confirm')
    #Put email ID of sender in <sender>
    msg = Message('Email confirmation', sender = 'neera99j@gmail.com', recipients = [string])
    msg.body = "Activate your account by clicking the link: "
    domain = "http://localhost:5000/confirm_email/"
    msg.body += domain
    msg.body += token
    mail.send(msg)
    return "Please see your email for verification"

@app.route('/confirm_email/<token_recv>')
def confirm_email(token_recv):
    try:
        email = random_URL.loads(token_recv, salt='email-confirm')
    except SignatureExpired:
        return '<h2>The token is expired!</h2>'
    registeredUser = users_repository.get_email(email)
    #set registered user to be active means user's account is verified.
    registeredUser.active = True
    return '<h2>The token works!</h2>'

@app.route("/alumniLogin")
def alumniLogin():
    return render_template("alumniLogin.html")

@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")

@app.route("/studentLogin")
def studentLogin():
    return render_template("studentLogin.html")

@app.route("/contact")
def contacts():
    return render_template("contact.html")
    
if __name__ == "__main__":
    app.run(debug=True)
