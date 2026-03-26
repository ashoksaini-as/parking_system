from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.db import get_user_by_username, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard') if session.get('role') == 'admin' else url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('All fields required.', 'error')
            return render_template('auth/login.html')
        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin.dashboard') if user['role'] == 'admin' else url_for('user.dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()
        if not username or not password or not confirm:
            flash('All fields required.', 'error')
            return render_template('auth/register.html')
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('auth/register.html')
        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        if get_user_by_username(username):
            flash('Username already taken.', 'error')
            return render_template('auth/register.html')
        create_user(username, generate_password_hash(password))
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
