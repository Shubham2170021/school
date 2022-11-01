from flask import Flask,render_template,request,url_for,redirect,session
from dbcom import UseDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_login import LoginManager
app=Flask(__name__)
app.secret_key="super secret key"
app.config['dbconfig']={'host':'127.0.0.1',
                       'user':'root',
		               'password':'root',
		               'database':'user'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='root', server='127.0.0.1', database='user')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    id=User.query.filter_by(id=user_id).first()
    return id
##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/register")
def register():
    return render_template("register.html ")
@app.route("/signup",methods=['POST'])
def signup():
    Name=request.form.get('name')
    Email=request.form['email']
    Password=request.form['password']
    print(Email)
    hash_and_salted_password = generate_password_hash(Password, method='pbkdf2:sha256', salt_length=8)
    new_user = User(
        email=Email,
        name=Name,
        password=hash_and_salted_password,
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return render_template("show.html",title=Name)
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        Email=(request.form.get('email')).strip()
        Password=request.form['password']
        user = User.query.filter_by(email=Email).first()
        if check_password_hash(user.password,Password):
            login_user(user)
            return render_template("show.html",title=user.name)
    return render_template("index.html")
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route("/addstudent")
@login_required
def add_student():
    return render_template("addstudent.html")
@app.route("/viewstudent",methods=['POST'])
@login_required
def do_add_student():
    Roll_no=request.form['rno']
    First_name=request.form['fname']
    Last_name=request.form['lname']
    DOB=request.form['dob']
    with UseDataBase(app.config['dbconfig']) as cursor:
        _sql="""insert into students
            (Roll_no,First_name,Last_name,DOB)
            values
            (%s,%s,%s,%s)"""
        cursor.execute(_sql,(Roll_no,First_name,Last_name,DOB,))
    return render_template("showsubmitdata.html",
                           rno=Roll_no,
                           fname=First_name,
                           lname=Last_name,
                           dob=DOB)
@app.route("/viewallstudent")
@login_required
def view_all_student():
    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL="""select Roll_no,First_name,Last_name,DOB from students"""
        cursor.execute(_SQL)
        contents=cursor.fetchall()
    titles=('Roll_no','First_name','Last_name','DOB')
    return render_template("marks.html",
                         the_row_titles=titles,
                         the_data=contents,
                         title='Student data')
@app.route("/searchrollno")
@login_required
def search_roll_no():
    return render_template("searchrollno.html")
@app.route("/viewrollno",methods=['POST'])
@login_required
def view_roll_no():
    Roll_no=request.form['rno']
    with UseDataBase(app.config['dbconfig']) as cursor:
        _sql=f"""SELECT Roll_no,First_name,Last_name,DOB FROM students WHERE Roll_no=%s"""
        cursor.execute(_sql,(Roll_no,))
        contents=cursor.fetchall()
    titles=('Roll_no','First_name','Last_name','DOB')
    return render_template("marks.html",
                           the_row_titles=titles,
                           the_data=contents,
                           title='Student data')
@app.route("/entermarks")
@login_required
def enter_marks():
    return render_template("openmarks.html")
@app.route("/submitmarks",methods=['POST'])
@login_required
def marks_search():
    Roll_no=request.form['rno']
    Exam_code=request.form['ecode']
    Paper_code=request.form['pcode']
    Total_marks=request.form['tmarks']
    Obtain_marks=request.form['omarks']
    with UseDataBase(app.config['dbconfig']) as cursor:
        _sql="""insert into marks
            (Roll_no,Exam_code,Paper_code,Total_marks,Obtain_marks)
            values
            (%s,%s,%s,%s,%s)"""
        cursor.execute(_sql,(Roll_no,Exam_code,Paper_code,Total_marks,Obtain_marks))
    return render_template("viewmarks.html",
                           rno=Roll_no,
                           ecode=Exam_code,
                           pcode=Paper_code,
                           tmarks=Total_marks,
                           omarks=Obtain_marks)
@app.route("/viewmarks")
@login_required
def view_the_marks():
    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL="""select Roll_no,Exam_code,Paper_code,Total_marks,Obtain_marks from marks"""
        cursor.execute(_SQL)
        contents=cursor.fetchall()
    obtain_marks=[]
    total_marks=[]
    for item in range(len(contents)):
        data=contents[item]
        obtain_marks.append(int(data[4]))
        total_marks.append(int(data[3]))
    obtain=sum(obtain_marks)
    total=sum(total_marks)
    percentage=round((obtain/total)*100,2)
    titles=('Roll_no','Exam_code','Paper_code','Total_marks','Obtain_marks')
    return render_template("marks.html",
                         the_row_titles=titles,the_data=contents,exam_title="Total",
                         percentage=percentage,obtain_marks=obtain,total_marks=total)
@app.route("/exammarks")
@login_required
def exammarks():
    return render_template("exammarks.html")
@app.route("/marks",methods=['POST'])
@login_required
def marks():
    Roll_no=request.form['rno']
    Exam_code=request.form['ecode']
    with UseDataBase(app.config['dbconfig']) as cursor:
        _sql=f"""SELECT Roll_no,Exam_code,Paper_code,Total_marks,Obtain_marks FROM marks WHERE Roll_no=%s and Exam_code=%s"""
        cursor.execute(_sql,(Roll_no,Exam_code,))
        contents=cursor.fetchall()
    titles=('Roll_no','Exam_code','Paper_code','Total_marks','Obtain_marks')
    obtain_marks=[]
    total_marks=[]
    for item in range(len(contents)):
        data=contents[item]
        obtain_marks.append(int(data[4]))
        total_marks.append(int(data[3]))
    paper_code=int(data[2])
    obtain=sum(obtain_marks)
    total=sum(total_marks)
    percentage=round((obtain/total)*100,2)
    if paper_code==1:
        return render_template('marks.html',the_row_titles=titles,
                         the_data=contents,exam_title=" pre university test",
                         percentage=percentage,obtain_marks=obtain,total_marks=total)
    elif paper_code==2:
        return render_template('marks.html',the_row_titles=titles,
                         the_data=contents,exam_title="university test",
                         percentage=percentage,obtain_marks=obtain,total_marks=total)
    elif paper_code==2:
        return render_template('marks.html',the_row_titles=titles,
                         the_data=contents,exam_title=" pre university exam",
                         percentage=percentage,obtain_marks=obtain,total_marks=total)
    else:
        return render_template('marks.html',the_row_titles=titles,
                         the_data=contents,exam_title=" university exam",
                         percentage=percentage,obtain_marks=obtain,total_marks=total)
app.run(debug=True)