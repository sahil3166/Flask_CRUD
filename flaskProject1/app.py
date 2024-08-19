from flask import Flask, flash, render_template, request, redirect, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root316@localhost/sahil1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a1b2c3d4e5f67890abcdef1234567890'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)

    def __init__(self, name, age):
        self.name = name
        self.age = age


with app.app_context():
    db.create_all()


def validate_name(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            name = request.form.get('name')
            if name is None or not name.isalpha():
                flash('Name must contain only alphabets', 'error')
                return render_template('create.html')
        return func(*args, **kwargs)

    return decorated_function


def validate_age(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            age = request.form.get('age')
            if age is None or not age.isdigit() or int(age) <= 0:
                flash('Age must be a positive integer', 'error')
                return render_template('create.html')
        return func(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['GET', 'POST'])
@validate_name
@validate_age
def create():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']

        new_user = User(name=name, age=age)
        db.session.add(new_user)
        db.session.commit()
    return render_template('create.html')


@app.route('/view')
def view():
    all_users = User.query.all()
    return render_template('view.html', users=all_users)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('view'))
    return 'User not found', 404


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@validate_name
@validate_age
def update_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.age = request.form['age']

        db.session.commit()
        return redirect(url_for('view'))
    return render_template('update.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
