from flask import Flask,url_for,render_template,request,  redirect,url_for, flash,abort
from flask_login import LoginManager , login_required , UserMixin , login_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer, SignatureExpired
from flask_mysqldb import MySQL

app = Flask(__name__)

# Uncomment this if database is on your system
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ALUMNI'

# Uncomment this database is on server
# app.config['MYSQL_HOST'] = 'remotemysql.com'
# app.config['MYSQL_USER'] = 'qmrpgUAerV'
# app.config['MYSQL_PASSWORD'] = 'GS5zKM8g2w'
# app.config['MYSQL_DB'] = 'qmrpgUAerV'

# object of MySql
mysql = MySQL(app)

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
app.config['MAIL_PASSWORD'] = 'Neeraj@mysql'	#Use Password of gmail ID
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)



flag = 1
def globally_change():
    global  flag 
    flag = 1
    
@app.route("/", methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        registeredUser = users_repository.get_email(email)
        if registeredUser != None and registeredUser.password == password and registeredUser.active == True:
            globally_change()
            # print("value of flasg is :;",flag)
            print('Logged in..')
            login_user(registeredUser)
            return redirect(url_for('login_page'))
        else:
            return abort(401)
             # pyautogui.alert('Please signup first!', "alert")  # always returns "OK"
            # return render_template("home.html")
    else:
        return render_template("home.html")

@app.route("/login_page")
def login_page():
    print("flag is ",flag)
    if flag == 1:
        return render_template("login.html")
    else:
        return "Please Login first"

string = "b17100@students.iitmandi.ac.in"   #default webmail 
@app.route("/signup",methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        global first_db
        global last_db
        global email_
        global password_db
        userDetails = request.form
        firstName = userDetails['firstName']
        first_db = firstName
        lastName = userDetails['lastName']
        last_db = lastName
        email = userDetails['email']
        email_ = email
        print(email_)
        global string
        string = email
        password = userDetails['password'] 
        password_db = password
        new_user = User(firstName , lastName , email , password , users_repository.next_index())
        users_repository.save_user(new_user)
        return redirect(url_for('verification_page'))

    return render_template("signup.html")

@app.route("/forgot",methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        # Fetch form data
        global email
        email = request.form['email']
        global string
        string = email
        registeredUser = users_repository.get_email(email)
        print(registeredUser)
        if registeredUser is None:
            return render_template("not_registered_user.html")
        else:
            return redirect(url_for('forgotemail'))
        # new_user = User(firstName , lastName , email , password , users_repository.next_index())
        # users_repository.save_user(new_user)
    return render_template("forgot_email.html")

@app.route("/forgotemail")
def forgotemail():  
    global random_URL
    random_URL = URLSafeSerializer('secret_key')
    global token
    token = random_URL.dumps(string, salt='email-confirm')
    #Put email ID of sender in <sender>
    msg = Message('Email confirmation', sender = 'neera99j@gmail.com', recipients = [string])
    msg.body = "Reset your password by clicking the link: "
    domain = "http://localhost:5000/reset/"
    msg.body += domain
    msg.body += token
    mail.send(msg)
    return "Please see your email for password reset"
    
new_password=""
@app.route('/reset/<token_recv>',methods=['GET', 'POST'])
def password_change(token_recv):
    try:
        email = random_URL.loads(token_recv, salt='email-confirm')
        cur = mysql.connection.cursor()
        print("email is ",email)
        if request.method == 'POST':
            global new_password
            new_password = request.form['password1']
            # cur.execute("Delete from Login")
            cur.execute("Update Login SET password=(%s) Where Email=(%s)",(new_password, email))
            mysql.connection.commit()
            cur.close()
        registeredUser = users_repository.get_email(email)
    except SignatureExpired :
        return '<h2>The token is expired!</h2>'
    print(new_password)
    registeredUser = users_repository.get_email(email)
    registeredUser.password = new_password
    #set registered user to be active means user's account is verified.
    registeredUser.active = True
    return render_template("new_password.html")

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
        cur = mysql.connection.cursor()
        print("email is ",email_)
        cur.execute("Delete from Login")
        cur.execute("INSERT INTO Login(Email, FirstName,LastName,password) VALUES(%s,%s, %s,%s)",(email_,first_db,last_db,password_db))
        mysql.connection.commit()
        cur.close()
    except SignatureExpired :
        return '<h2>The token is expired!</h2>'
    registeredUser = users_repository.get_email(email)
    #set registered user to be active means user's account is verified.
    registeredUser.active = True
    return '<h2>Your Email is verified!</h2>'

alumni_no = 'b15100'

list1 = ""
@app.route('/profile/<enroll_no>')
def profile_page(enroll_no):
    global alumni_no
    alumni_no = enroll_no
    return render_template('profile.html')

final_result=""
@app.route("/login_page/alumni", methods=['GET', 'POST'])
def alumniLogin():
    if request.method == 'POST':
        # # Fetch form data
        # global first_db
        # global last_db
        # global email_
        # global password_db
        passout_year = request.form['passout_year']
        degree = request.form['degree']
        branch = request.form['branch']
        current_state = request.form['current_state']
        company_name = request.form['company_name']
        location = request.form['location']
        position = request.form['position']
        field_of_work = request.form['field_of_work']
        company = request.form['company']
        position_in_opportunities = request.form['position_in_opportunities']
        field = request.form['field']
        alumni_filter = request.form
        print(alumni_filter)
        print("alumni filter")
        print(alumni_filter['degree'])
        cur = mysql.connection.cursor()
        query1 = ("SELECT EnrollmentNumber from Alumni A Where A.PassoutYear={} AND A.Degree='{}' AND A.CurrentState='{}' AND A.Branch='{}' ").format(passout_year, degree,current_state, branch)
        query2 = ("SELECT EnrollmentNumber from Worked_In W Where W.CompanyName='{}' AND W.Location='{}' AND W.Position='{}' AND W.Field_of_work='{}' ").format(company_name, location, position, field_of_work)
        query3 = ("SELECT EnrollmentNumber from Opportunities_for_hiring O Where O.Company='{}' AND O.Position='{}' AND O.Field='{}'").format(company, position_in_opportunities, field)
        query1 = query1.replace("=All","!=''")
        query1 = query1.replace("='All'","!=''")
        query2 = query2.replace("=All","!=''")
        query2 = query2.replace("='All'","!=''")
        query3 = query3.replace("=All","!=''")
        query3 = query3.replace("='All'","!=''")
        print(query1)
        print(query2)
        print(query3)
        cur.execute(query1)
        result1 = cur.fetchall()
        cur.execute(query2)
        result2 = cur.fetchall()
        cur.execute(query3)
        result3 = cur.fetchall()
        print(result1)
        print(result2)
        print(result3)
        global final_result
        final_result = (set(result1).intersection(result2))
        final_result = (set(final_result).intersection(result3))
        print(final_result)
        # list1 = cur.execute(("SELECT EnrollmentNumber from Alumni A Where A.PassoutYear={} AND A.Degree='{}' AND A.CurrentState='Job' AND A.Branch='CSE' ").format(alumni_filter['passout_year'], alumni_filter['degree']))
        # print(list1)
        # list = cur.execute(("SELECT EnrollmentNumber from Alumni A Where A.PassoutYear={} AND A.Degree={} AND A.CurrentState=Job AND A.Branch=CSE ").format(alumni_filter['passout_year'], alumni_filter['degree'],alumni_filter['current_state'],alumni_filter['branch']))

        mysql.connection.commit()
        cur.close()
        # firstName = userDetails['firstName']
        # first_db = firstName
        # lastName = userDetails['lastName']
        # last_db = lastName
        # email = userDetails['email']
        # email_ = email
        print("alumni filter")
        # print(email_)
        # global string
        # string = email
        # password = userDetails['password'] 
        # password_db = password
        # new_user = User(firstName , lastName , email , password , users_repository.next_index())
        # users_repository.save_user(new_user)
        # return redirect(url_for('verification_page'))
    if flag == 1:
        return render_template("alumni.html", filter=final_result)
    else:
        return "Please Login first"
    
students = ""
@app.route("/login_page/students",methods=['GET','POST'])
def adminLogin():
    global students
    beauty_students=[]
    if request.method == 'POST':
        Btech = request.form
        Btech_year = request.form['Btech_year']    
        branch = Btech['branch']
        room_no = Btech['room_no']
        hostels = Btech['hostels']

        print(branch,room_no,hostels)
        cur = mysql.connection.cursor()
        query = "select * from student S where S.Branch='{}' AND S.Hostels='{}' AND S.Room_no='{}' ".format(branch,hostels,room_no)
        query1 = query.replace("='All'","!=''")
        cur.execute(query1)
       
        students = cur.fetchall()
        print(students)
        students = list(students)

        for temp in students:
            beauty_students.append(temp)
        
    if flag == 1:
        return render_template("students.html",students=students)
    else:
        return "Please Login first" 

@app.route("/login_page/faculty")
def studentLogin():
    if flag == 1 :
        return render_template("faculty.html")
    else:
        return "Please Login first"

@app.context_processor
def context_processor():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Alumni Where EnrollmentNumber=%s",[alumni_no])
    alumni_basic_information = cur.fetchall()
    cur.execute("SELECT * FROM Contact_Details Where EnrollmentNumber=%s",[alumni_no])
    contact_deatils = cur.fetchall()
    cur.execute("SELECT * FROM Worked_In Where EnrollmentNumber=%s",[alumni_no])
    Worked_In = cur.fetchall()
    cur.execute("SELECT * FROM Higher_Studies Where EnrollmentNumber=%s",[alumni_no])
    Higher_Studies = cur.fetchall()
    cur.execute("SELECT * FROM Semester_Exchange Where EnrollmentNumber=%s",[alumni_no])
    sem_exchange = cur.fetchall()
    cur.execute("SELECT * FROM Contributed_To Where EnrollmentNumber=%s",[alumni_no])
    contribution = cur.fetchall()
    cur.close()
    return dict(students = students,username=string, alumni=alumni_basic_information, contact=contact_deatils, work=Worked_In, study=Higher_Studies, sem_exchange=sem_exchange, contribution=contribution)
    
if __name__ == "__main__":
    app.run(debug=True)
