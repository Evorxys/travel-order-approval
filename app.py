from flask import Flask, render_template, request, jsonify, session, url_for, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
import os.path

load_dotenv()

app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates')
app.secret_key = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

class Warriors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    section = db.Column(db.String(120), nullable=False)
    official_station = db.Column(db.String(120), nullable=False)

class Captain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    section = db.Column(db.String(120), nullable=False)
    official_station = db.Column(db.String(120), nullable=False)

class Overlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    section = db.Column(db.String(120), nullable=False)
    official_station = db.Column(db.String(120), nullable=False)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for(f"dashboard_{session['role']}"))
    return render_template('login.html')

@app.route('/dashboard/chief')
def dashboard_chief():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'chief':
        return redirect(url_for('login_page'))
    return render_template('home_chief.html')

@app.route('/dashboard/cenro')
def dashboard_cenro():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'cenro':
        return redirect(url_for('login_page'))
    return render_template('home_cenro.html')

@app.route('/dashboard/employee')
def dashboard_employee():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('login_page'))
    
    employee = Warriors.query.get(session['user_id'])
    return render_template('home_emp.html', employee=employee)

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'user_id' not in session or 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    return render_template('home_admin.html')

@app.route('/admin/add_employee')
def add_employee():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin_privilages/add_emp.html')

@app.route('/admin/employee_list')
def admin_employee_list():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    
    # Fetch all users from different tables with proper attributes
    warriors = Warriors.query.with_entities(
        Warriors.name, Warriors.username, Warriors.position,
        Warriors.section, Warriors.official_station
    ).all()
    captains = Captain.query.with_entities(
        Captain.name, Captain.username, Captain.position,
        Captain.section, Captain.official_station
    ).all()
    overlords = Overlord.query.with_entities(
        Overlord.name, Overlord.username, Overlord.position,
        Overlord.section, Overlord.official_station
    ).all()
    
    # Convert query results to dictionaries
    all_users = (
        [{'user': {
            'name': w.name,
            'username': w.username,
            'position': w.position,
            'section': w.section,
            'official_station': w.official_station
        }, 'role': 'Employee'} for w in warriors] +
        [{'user': {
            'name': c.name,
            'username': c.username,
            'position': c.position,
            'section': c.section,
            'official_station': c.official_station
        }, 'role': 'Chief'} for c in captains] +
        [{'user': {
            'name': o.name,
            'username': o.username,
            'position': o.position,
            'section': o.section,
            'official_station': o.official_station
        }, 'role': 'CENRO'} for o in overlords]
    )
    
    return render_template('admin_privilages/employee_list.html', users=all_users)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Check Admin credentials from .env
    if data['username'] == os.getenv('mandirigma_user') and data['password'] == os.getenv('mandirigma_password'):
        session['user_id'] = 'admin'
        session['role'] = 'admin'
        return jsonify({
            'message': 'Login successful',
            'redirect': url_for('dashboard_admin')
        }), 200
    
    # Check Warriors (employees)
    user = Warriors.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        session['user_id'] = user.id
        session['role'] = 'employee'
        return jsonify({
            'message': 'Login successful',
            'redirect': url_for('dashboard_employee')
        }), 200
    
    # Check Captain (chiefs)
    chief = Captain.query.filter_by(username=data['username']).first()
    if chief and chief.password == data['password']:
        session['user_id'] = chief.id
        session['role'] = 'chief'
        return jsonify({
            'message': 'Login successful',
            'redirect': url_for('dashboard_chief')
        }), 200
    
    # Check Overlord (cenro)
    cenro = Overlord.query.filter_by(username=data['username']).first()
    if cenro and cenro.password == data['password']:
        session['user_id'] = cenro.id
        session['role'] = 'cenro'
        return jsonify({
            'message': 'Login successful',
            'redirect': url_for('dashboard_cenro')
        }), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/create-travel')
def create_travel():
    if 'user_id' not in session or session['role'] != 'employee':
        return redirect(url_for('login_page'))
    employee = Warriors.query.get(session['user_id'])
    return render_template('create_travel.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)