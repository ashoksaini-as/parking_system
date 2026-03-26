from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from app.models.db import *
from app.services.parking import calculate_fee, generate_receipt_pdf
import os

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    vehicles = get_user_vehicles(user_id)
    parked = [v for v in vehicles if v['status'] == 'parked']
    exited = [v for v in vehicles if v['status'] == 'exited']
    total_spent = sum(float(v['fee']) for v in exited)
    slot_counts = get_slot_counts()
    return render_template('user/dashboard.html',
        parked=parked,
        exited=exited,
        total_spent=total_spent,
        slot_counts=slot_counts,
        total_slots=50
    )

@user_bp.route('/entry', methods=['GET', 'POST'])
@login_required
def vehicle_entry():
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        owner_name = request.form.get('owner_name', '').strip()
        user_id = session['user_id']
        if not vehicle_number or not owner_name:
            flash('All fields required.', 'error')
            return redirect(url_for('user.vehicle_entry'))
        if get_vehicle_by_number(vehicle_number):
            flash(f'{vehicle_number} is already parked.', 'error')
            return redirect(url_for('user.vehicle_entry'))
        slot = get_available_slot()
        if not slot:
            flash('No parking slots available!', 'error')
            return redirect(url_for('user.vehicle_entry'))
        add_vehicle(vehicle_number, owner_name, user_id, slot)
        set_slot_status(slot, 'occupied')
        flash(f'Vehicle parked at slot #{slot}!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('user/entry.html')

@user_bp.route('/history')
@login_required
def history():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'entry_time')
    order = request.args.get('order', 'desc')
    vehicles = get_user_vehicles(session['user_id'], search=search, sort=sort, order=order)
    return render_template('user/history.html', vehicles=vehicles, search=search, sort=sort, order=order)

@user_bp.route('/receipt/<int:vehicle_id>')
@login_required
def get_receipt(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle['user_id'] != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('user.history'))
    if vehicle['status'] != 'exited':
        flash('Receipt only available after exit.', 'error')
        return redirect(url_for('user.history'))
    receipt = generate_receipt_pdf(vehicle)
    receipts_dir = os.path.join(os.getcwd(), 'app', 'static', 'receipts')
    return send_from_directory(receipts_dir, receipt, as_attachment=True)
