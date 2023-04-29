from flask import Flask, render_template, request, flash, redirect, url_for
import pymysql
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proj4'

# create a connection to the MySQL database
conn = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)


# define a user class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        cursor = conn.cursor()
        sql = "SELECT * FROM admins WHERE Account_name = %s"
        val = (user_id,)
        cursor.execute(sql, val)
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return None

        return User(id=user[0])


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# home page
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# officer page
@app.route('/officers')
@login_required
def officers():
    # get all the data from the officers table
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM officers")
    data = cursor.fetchall()
    cursor.close()

    # search function
    search_query = request.args.get('search')
    if search_query:
        cursor = conn.cursor()
        cursor.callproc('search_police', (search_query,))
        data = cursor.fetchall()
        cursor.close()

    return render_template('officers.html', data=data)

@app.route('/delete_officer/<int:officer_id>', methods=['POST'])
@login_required
def delete_officer(officer_id):
    success = delete_officer_from_database(officer_id)
    if not success:
        flash("Cannot delete officer due to constraint violation.", "error")
    return redirect(url_for('officers'))

def delete_officer_from_database(officer_id):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM officers WHERE Officer_ID = %s"
        val = (officer_id,)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.IntegrityError:
        return False

@app.route('/update_officer', methods=['POST'])
@login_required
def update_officer():
    officer_id = request.form.get('officer_id')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    precinct = request.form.get('precinct')
    badge_number = request.form.get('badge_number')
    phone_number = request.form.get('phone_number')
    status = request.form.get('status')

    success = update_officer_in_database(officer_id, last_name, first_name, precinct, badge_number, phone_number, status)
    if not success:
        flash("Error updating officer data.", "error")
    else:
        flash("Officer data updated successfully.", "success")
    return redirect(url_for('officers'))

def update_officer_in_database(officer_id, last_name, first_name, precinct, badge_number, phone_number, status):
    try:
        cursor = conn.cursor()
        sql = """UPDATE officers SET 
                 last_Name = %s, 
                 first_Name = %s, 
                 precinct = %s, 
                 badge = %s, 
                 phone = %s, 
                 status = %s 
                 WHERE Officer_ID = %s"""
        val = (last_name, first_name, precinct, badge_number, phone_number, status, officer_id)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False
    
@app.route('/insert_officer', methods=['POST'])
@login_required
def insert_officer():
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    precinct = request.form.get('precinct')
    badge_number = request.form.get('badge_number')
    phone_number = request.form.get('phone_number')
    status = request.form.get('status')

    success = insert_officer_into_database(last_name, first_name, precinct, badge_number, phone_number, status)
    if not success:
        flash("Error adding new officer.", "error")
    else:
        flash("New officer added successfully.", "success")
    return redirect(url_for('officers'))

def insert_officer_into_database(last_name, first_name, precinct, badge_number, phone_number, status):
    try:
        cursor = conn.cursor()
        # get the max Officer_ID in the table
        cursor.execute("SELECT MAX(Officer_ID) FROM officers")
        max_officer_id = cursor.fetchone()[0]
        # increment the max Officer_ID to generate the new Officer_ID
        officer_id = max_officer_id + 1 if max_officer_id else 1
        sql = """INSERT INTO officers (Officer_ID, last_Name, first_Name, precinct, badge, phone, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (officer_id, last_name, first_name, precinct, badge_number, phone_number, status)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False


# criminal page
@app.route('/criminals')
@login_required
def criminals():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criminals")
    data = cursor.fetchall()
    cursor.close()

    search_query = request.args.get('search')
    if search_query:
        cursor = conn.cursor()
        cursor.callproc('search_criminal', (search_query,))
        data = cursor.fetchall()
        cursor.close()

    return render_template('criminals.html', data=data)

@app.route('/delete_criminal/<int:criminal_id>', methods=['POST'])
@login_required
def delete_criminal(criminal_id):
    success = delete_criminal_from_database(criminal_id)
    if not success:
        flash("Cannot delete criminal due to constraint violation.", "error")
    return redirect(url_for('criminals'))

def delete_criminal_from_database(criminal_id):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM criminals WHERE criminal_id = %s"
        val = (criminal_id,)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.IntegrityError:
        return False

@app.route('/update_criminal', methods=['POST'])
@login_required
def update_criminal():
    criminal_id = request.form.get('criminal_id')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip = request.form.get('zip')
    phone = request.form.get('phone')
    V_status = request.form.get('V_status')
    p_status = request.form.get('p_status')

    success = update_criminal_in_database(criminal_id, last_name, first_name, street, city, state, zip, phone, V_status, p_status)
    if not success:
        flash("Error updating criminal data.", "error")
    else:
        flash("Criminal data updated successfully.", "success")
    return redirect(url_for('criminals'))

def update_criminal_in_database(criminal_id, last_name, first_name, street, city, state, zip, phone, V_status, p_status):
    try:
        cursor = conn.cursor()
        sql = """UPDATE criminals SET 
                 last_name = %s, 
                 first_name = %s, 
                 street = %s, 
                 city = %s, 
                 state = %s, 
                 zip_code = %s, 
                 phone = %s, 
                 V_status = %s, 
                 p_status = %s 
                 WHERE criminal_id = %s"""
        val = (last_name, first_name, street, city, state, zip, phone, V_status, p_status, criminal_id)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False
    
@app.route('/insert_criminal', methods=['POST'])
@login_required
def insert_criminal():
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip = request.form.get('zip')
    phone = request.form.get('phone')
    V_status = request.form.get('V_status')
    p_status = request.form.get('p_status')

    success = insert_criminal_into_database(last_name, first_name, street, city, state, zip, phone, V_status, p_status)
    if not success:
        flash("Error adding new criminal.", "error")
    else:
        flash("New criminal added successfully.", "success")
    return redirect(url_for('criminals'))

def insert_criminal_into_database(last_name, first_name, street, city, state, zip, phone, V_status, p_status):
    try:
        cursor = conn.cursor()
        # get the max criminal_id in the table
        cursor.execute("SELECT MAX(criminal_id) FROM criminals")
        max_criminal_id = cursor.fetchone()[0]
        # increment the max criminal_id to generate the new criminal_id
        criminal_id = max_criminal_id + 1 if max_criminal_id else 1
        sql = """INSERT INTO criminals (criminal_id, last_name, first_name, street, city, state, zip_code, phone, V_status, p_status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (criminal_id, last_name, first_name, street, city, state, zip, phone, V_status, p_status)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False


# crimes page
@app.route('/crimes')
@login_required
def crimes():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crimes")
    data = cursor.fetchall()
    cursor.close()

    search_query = request.args.get('search')
    if search_query:
        cursor = conn.cursor()
        cursor.callproc('search_crime', (search_query,))
        data = cursor.fetchall()
        cursor.close()

    return render_template('crimes.html', data=data)

# crime page
@app.route('/delete_crime/<int:crime_id>', methods=['POST'])
@login_required
def delete_crime(crime_id):
    success = delete_crime_from_database(crime_id)
    if not success:
        flash("Cannot delete crime due to constraint violation.", "error")
    return redirect(url_for('crimes'))

def delete_crime_from_database(crime_id):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM crimes WHERE crime_id = %s"
        val = (crime_id,)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.IntegrityError:
        return False

@app.route('/update_crime', methods=['POST'])
@login_required
def update_crime():
    crime_id = request.form.get('crime_id')
    criminal_id = request.form.get('criminal_id')
    classification = request.form.get('classification')
    date_charged = request.form.get('date_charged')
    status = request.form.get('status')
    hearing_date = request.form.get('hearing_date')
    appeal_cut_date = request.form.get('appeal_cut_date')

    success = update_crime_in_database(crime_id, criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date)
    if not success:
        flash("Error updating crime data.", "error")
    else:
        flash("Crime data updated successfully.", "success")
    return redirect(url_for('crimes'))

def update_crime_in_database(crime_id, criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date):
    try:
        cursor = conn.cursor()
        sql = """UPDATE crimes SET 
                 criminal_id = %s, 
                 classification = %s, 
                 date_charged = %s, 
                 status = %s, 
                 hearing_date = %s, 
                 appeal_cut_date = %s
                 WHERE crime_id = %s"""
        val = (criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date, crime_id)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False
    
@app.route('/insert_crime', methods=['POST'])
@login_required
def insert_crime():
    criminal_id = request.form.get('criminal_id')
    classification = request.form.get('classification')
    date_charged = request.form.get('date_charged')
    status = request.form.get('status')
    hearing_date = request.form.get('hearing_date')
    appeal_cut_date = request.form.get('appeal_cut_date')

    success = insert_crime_into_database(criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date)
    if not success:
        flash("Error adding new crime.", "error")
    else:
        flash("New crime added successfully.", "success")
    return redirect(url_for('crimes'))

def insert_crime_into_database(criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date):
    try:
        cursor = conn.cursor()
        # get the max crime_id in the table
        cursor.execute("SELECT MAX(crime_id) FROM crimes")
        max_crime_id = cursor.fetchone()[0]
        # increment the max crime_id to generate the new crime_id
        crime_id = max_crime_id + 1 if max_crime_id else 1
        sql = """INSERT INTO crimes (crime_id, criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (crime_id, criminal_id, classification, date_charged, status, hearing_date, appeal_cut_date)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False


# aliases page
@app.route('/aliases')
@login_required
def aliases():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Aliases")
    data = cursor.fetchall()
    cursor.close()
    return render_template('aliases.html', data=data)

@app.route('/delete_alias/<int:alias_id>', methods=['POST'])
@login_required
def delete_alias(alias_id):
    success = delete_alias_from_database(alias_id)
    if not success:
        flash("Cannot delete alias due to constraint violation.", "error")
    return redirect(url_for('aliases'))

def delete_alias_from_database(alias_id):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Aliases WHERE alias_id = %s"
        val = (alias_id,)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.IntegrityError:
        return False

@app.route('/update_alias', methods=['POST'])
@login_required
def update_alias():
    alias_id = request.form.get('alias_id')
    criminal_id = request.form.get('criminal_id')
    alias = request.form.get('alias')

    success = update_alias_in_database(alias_id, criminal_id, alias)
    if not success:
        flash("Error updating alias data.", "error")
    else:
        flash("Alias data updated successfully.", "success")
    return redirect(url_for('aliases'))

def update_alias_in_database(alias_id, criminal_id, alias):
    try:
        cursor = conn.cursor()
        sql = """UPDATE Aliases SET 
                 criminal_id = %s, 
                 alias = %s
                 WHERE alias_id = %s"""
        val = (criminal_id, alias, alias_id)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False

@app.route('/insert_alias', methods=['POST'])
@login_required
def insert_alias():
    criminal_id = request.form.get('criminal_id')
    alias = request.form.get('alias')

    success = insert_alias_into_database(criminal_id, alias)
    if not success:
        flash("Error adding new alias.", "error")
    else:
        flash("New alias added successfully.", "success")
    return redirect(url_for('aliases'))

def insert_alias_into_database(criminal_id, alias):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(alias_id) FROM Aliases")
        max_alias_id = cursor.fetchone()[0]
        alias_id = max_alias_id + 1 if max_alias_id else 1
        sql = """INSERT INTO Aliases (alias_id, criminal_id, alias)
                 VALUES (%s, %s, %s)"""
        val = (alias_id, criminal_id, alias)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except pymysql.err.InternalError:
        return False

# police sign up page
@app.route('/p_signup', methods=['GET', 'POST'])
@login_required
def p_signup():
    if request.method == 'POST':
        account_name = request.form['account_name']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # check if the account name already exists in any of the tables
        cursor = conn.cursor()
        sql = "SELECT Account_name FROM police_users WHERE Account_name = %s UNION SELECT Account_name FROM admins WHERE Account_name = %s UNION SELECT Account_name FROM open_accounts WHERE Account_name = %s"
        val = (account_name, account_name, account_name)
        cursor.execute(sql, val)
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Account name already exists.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 2:
            flash('Password must be at least 2 characters.', category='error')
        else:
            # Insert the form data into the database
            cursor = conn.cursor()
            sql = "INSERT INTO police_users (Account_name, Password) VALUES (%s, %s)"
            val = (account_name, password1)
            cursor.execute(sql, val)
            conn.commit()

            flash('Account created successfully! Please log in.', category='success')
            return redirect(url_for('home'))

    return render_template('policesignup.html')

# signup page
@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        account_name = request.form['account_name']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # check if the account name already exists in any of the tables
        cursor = conn.cursor()
        sql = "SELECT Account_name FROM police_users WHERE Account_name = %s UNION SELECT Account_name FROM admins WHERE Account_name = %s UNION SELECT Account_name FROM open_accounts WHERE Account_name = %s"
        val = (account_name, account_name, account_name)
        cursor.execute(sql, val)
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Account name already exists.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 2:
            flash('Password must be at least 2 characters.', category='error')
        else:
            # Insert the form data into the database
            cursor = conn.cursor()
            sql = "INSERT INTO open_accounts (Account_name, Password) VALUES (%s, %s)"
            val = (account_name, password1)
            cursor.execute(sql, val)
            conn.commit()

            flash('Account created successfully! Please log in.', category='success')
            return redirect(url_for('login'))

    return render_template('signup.html')

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_name = request.form['account_name']
        password = request.form['password']

        cursor = conn.cursor()

        # Check police_users table
        sql = "SELECT * FROM police_users WHERE Account_name = %s AND Password = %s"
        val = (account_name, password)
        cursor.execute(sql, val)
        user = cursor.fetchone()

        # Check admins table if no user found in police_users
        if not user:
            sql = "SELECT * FROM admins WHERE Account_name = %s AND Password = %s"
            val = (account_name, password)
            cursor.execute(sql, val)
            user = cursor.fetchone()

        # Check open_accounts table if no user found in admins
        if not user:
            sql = "SELECT * FROM open_accounts WHERE Account_name = %s AND Password = %s"
            val = (account_name, password)
            cursor.execute(sql, val)
            user = cursor.fetchone()

        cursor.close()

        if user:
            user = User(id=user[0])
            login_user(user)
            flash('Login successful!', category='success')
            return redirect(url_for('home'))
        else:
            flash('Invalid account name or password', category='error')

    return render_template('login.html')


# logout page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

