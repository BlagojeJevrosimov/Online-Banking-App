from audioop import add
from logging import debug
from flask import Flask, render_template, jsonify , request, flash, redirect, url_for
import flask_login 
from flaskext.mysql import MySQL
from flask_login import login_user, login_required, logout_user, current_user, LoginManager


import database_op
from model.user import User,UserSchema
from model.transaction import Transaction

from config import db, ma

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin1999drs'
app.config['MYSQL_DATABASE_DB'] = 'finance'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


app.config['SECRET_KEY'] = 'bsadaasgsdfwefwefwe asdada' #secretKey za cookies itd

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:admin1999drs@localhost/finance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ma.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')#stavimo url endpointa 
def start():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST']) #znaci na ruti / i /home nam otvara home.html
@login_required
def home(): #kad odemo na url / sta god da je u home() ce raditi

    #db.drop_all()
    #db.create_all()
    #database_op.insert_credit_card('4222 4212 4787 4998','Milojko Milic',154,5876)
   # database_op.update_credit_card_amount('4222 4212 4787 4998', 2000)

    #database_op.insert_transaction('djokssso@example.com', 2555, 'micko', 'expense')
   # database_op.insert_transaction('djoksso@example.com', 25575, 'mickos', 'income')

    #database_op.insert_user_amount('djoksssoss@example.com',255)
    #database_op.update_amount('djoksssoss@example.com',6500)

    credit = database_op.get_credit_card('4222 4212 4787 4998')

    #transactions = database_op.get_transactions()
    transactions = database_op.filter_transaction_receiver('mickos')
    amount = database_op.get_amount('djoksssoss@example.com')

    #database_op.register_user('examples@gmail.com','bozidar','kilibarda','55874','258746985','srb','mmm','rd')
    #database_op.validate_user('examples@gmail.com')
    #user = database_op.check_if_user_exists('examples@gmail.com')
    #amount = 0

    return render_template('home.html', user = current_user, transactions=transactions, amount=credit.amount_dinar)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        country = request.form.get('country')
        city = request.form.get('city')
        address = request.form.get('address')
        phoneNumber = request.form.get('phoneNumber')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = database_op.check_if_user_exists(email)
        if user:
            flash('Email already exists.', category='error')
        elif len(firstName) < 2:
            flash('First name required.', category='error')
        elif len(lastName) < 2:
            flash('Last name required.', category='error')
        elif len(country) < 2:
            flash('Country required.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif ~email.__contains__('@'):
            flash('Email must contain "@" characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(address) < 2:
            flash('Address required.', category='error')
        elif len(city) < 2:
            flash('City required.', category='error')
        elif len(phoneNumber) < 2:
            flash('Phone number required.', category='error')
        else:
            database_op.register_user(email=email, firstName=firstName,lastName=lastName, password=password1,phone = phoneNumber,country=country,city=city,address= address)
            login_user(User(email=email, firstName=firstName,lastName=lastName, password=password1,phone = phoneNumber,country=country,city=city,address= address), remember=True)
            return redirect(url_for('home'))

    return render_template('register.html',user = current_user)

@app.route('/login', methods=['GET', 'POST'] )
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = database_op.check_if_user_exists(email)
        if user:
            if user.passw == password:
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html",user = current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/bank-transaction',methods=['GET', 'POST'])
@login_required
def deposit((sad)
    if request.method == 'POST':
        cardnumber = request.form.get('card_number')
        expdate =  request.form.get('expiration')
        cvc_code = request.form.get('cvc')
        amount = request.form.get('amount')
        credit_card = database_op.get_credit_card(cardnumber,cvc_code)


        if credit_card:
            expire_base = credit_card.expiration.strftime('%Y-%m')
            expire_form = expdate[0:7]
            if expdate == '':
                flash('Expiration date is not checked', category='error')
            elif expire_form != expire_base:
                flash('Incorrect expiration date, try again', category='error')
            else:
                x = threading.Thread(target=bank_transaction_validation,args=(credit_card.amount_dinar,amount,current_user.email,cardnumber,app))
                x.start()
                return redirect(url_for('home'))
        else:
            flash('Incorrect card number or cvc code, try again', category='error')
    return render_template('deposit.html',user=current_user)

@app.route('/transfer')
def transfer():
    return render_template('transfer.html')



if __name__ == '__main__':
    app.run(debug=True) 
