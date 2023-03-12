from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os, sqlite3

app = Flask(__name__,
            template_folder='template',
            static_folder='static'
            )

# -----------------------------------------
# -------------- AUTENTIKASI --------------
# -----------------------------------------

bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret190323'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html', form=form)

# -----------------------------------------
# ------------- CRUD APLIKASI -------------
# -----------------------------------------

app.config['DB_smartphone'] = os.getcwd() + '/smartphone.db'
conn = cursor = None

def open():
    global conn, cursor
    conn = sqlite3.connect(app.config['DB_smartphone'])
    cursor = conn.cursor()

def close():
    global conn, cursor
    cursor.close()
    conn.close()

@app.route("/index", methods=['GET', 'POST'])
def home():
    open()
    conn.row_factory=sqlite3.Row
    cursor.execute('SELECT nama_produk, harga_produk, rating_produk, id_produk, stock_produk, produk_terjual, lokasi_penjual, kategori  FROM smartphone limit 60')
    data = cursor.fetchall()
    close()
    return render_template('index.html', data=data)

@app.route("/tambah", methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama_produk     = request.form['nama_produk']
        harga_produk    = request.form['harga_produk']
        rating_produk   = request.form['rating_produk']
        id_produk       = request.form['id_produk']
        stock_produk    = request.form['stock_produk']
        produk_terjual  = request.form['produk_terjual']
        lokasi_penjual  = request.form['lokasi_penjual']
        kategori        = request.form['kategori']
        open()
        cursor.execute ('INSERT INTO smartphone(nama_produk, harga_produk, rating_produk, id_produk, stock_produk, produk_terjual, lokasi_penjual, kategori) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (nama_produk, harga_produk, rating_produk, id_produk, stock_produk, produk_terjual, lokasi_penjual, kategori))
        conn.commit()
        close()
        return redirect(url_for('home'))
    else:
        return render_template('tambah.html')

@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    open()
    conn.row_factory=sqlite3.Row
    cursor.execute('SELECT * FROM smartphone WHERE id=?', (id, ))
    data = cursor.fetchone()
    if request.method == 'POST':
        id              = request.form['id']
        nama_produk     = request.form['nama_produk']
        harga_produk    = request.form['harga_produk']
        rating_produk   = request.form['rating_produk']
        id_produk       = request.form['id_produk']
        stock_produk    = request.form['stock_produk']
        produk_terjual  = request.form['produk_terjual']
        lokasi_penjual  = request.form['lokasi_penjual']
        kategori        = request.form['kategori']
        cursor.execute('UPDATE smartphone SET nama_produk=?, harga_produk=?, rating_produk=?, id_produk=?, stock_produk=?, produk_terjual=?, lokasi_penjual=?, kategori=? WHERE id=?', (nama_produk, harga_produk, rating_produk, id_produk, stock_produk, produk_terjual, lokasi_penjual, kategori, id))
        conn.commit()
        close()
        return redirect(url_for('home'))
    else:
        return render_template('edit.html', data=data)

@app.route("/delete/<id>", methods=['GET', 'POST'])
def delete(id):
    open()
    cursor.execute('DELETE FROM smartphone WHERE id=?', (id, ))
    conn.commit()
    close()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5005)