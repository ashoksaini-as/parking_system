from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from functools import wraps
from app.models.db import *
from app.services.parking import calculate_fee, generate_receipt_pdf
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    slot_counts = get_slot_counts()
    total_rev = get_total_revenue()
    parked = get_currently_parked()
    daily = get_daily_revenue(30)
    monthly = get_monthly_revenue(12)
    return render_template('admin/dashboard.html',
        slot_counts=slot_counts,
        total_revenue=total_rev,
        parked_vehicles=parked,
        daily_revenue=daily,
        monthly_revenue=monthly,
        total_slots=50
    )

@admin_bp.route('/entry', methods=['GET', 'POST'])
@admin_required
def vehicle_entry():
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        owner_name = request.form.get('owner_name', '').strip()
        user_id = request.form.get('user_id') or session['user_id']
        if not vehicle_number or not owner_name:
            flash('Vehicle number and owner name are required.', 'error')
            return redirect(url_for('admin.vehicle_entry'))
        if get_vehicle_by_number(vehicle_number):
            flash(f'Vehicle {vehicle_number} is already parked.', 'error')
            return redirect(url_for('admin.vehicle_entry'))
        slot = get_available_slot()
        if not slot:
            flash('No slots available!', 'error')
            return redirect(url_for('admin.vehicle_entry'))
        add_vehicle(vehicle_number, owner_name, user_id, slot)
        set_slot_status(slot, 'occupied')
        flash(f'Vehicle {vehicle_number} parked at slot #{slot}.', 'success')
        return redirect(url_for('admin.dashboard'))
    users = get_all_users()
    return render_template('admin/entry.html', users=users)

@admin_bp.route('/exit/<int:vehicle_id>', methods=['GET', 'POST'])
@admin_required
def vehicle_exit(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    fee, hours = calculate_fee(vehicle['entry_time'])
    if request.method == 'POST':
        exit_vehicle(vehicle_id, fee)
        if vehicle['slot_number']:
            set_slot_status(vehicle['slot_number'], 'available')
        vehicle = get_vehicle_by_id(vehicle_id)
        receipt = generate_receipt_pdf(vehicle)
        flash(f'Exit processed. Fee: ₹{fee:.2f}. Receipt ready.', 'success')
        return redirect(url_for('admin.download_receipt', filename=receipt))
    return render_template('admin/exit.html', vehicle=vehicle, fee=fee, hours=hours)

@admin_bp.route('/receipt/<filename>')
@admin_required
def download_receipt(filename):
    receipts_dir = os.path.join(os.getcwd(), 'app', 'static', 'receipts')
    return send_from_directory(receipts_dir, filename, as_attachment=True)

@admin_bp.route('/slots')
@admin_required
def slots():
    all_slots = get_all_slots()
    return render_template('admin/slots.html', slots=all_slots)

@admin_bp.route('/history')
@admin_required
def history():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'entry_time')
    order = request.args.get('order', 'desc')
    vehicles = get_all_vehicles(search=search, sort=sort, order=order)
    return render_template('admin/history.html', vehicles=vehicles, search=search, sort=sort, order=order)

@admin_bp.route('/users')
@admin_required
def users():
    all_users = get_all_users()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    delete_user(user_id)
    flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/vehicles/delete/<int:vehicle_id>', methods=['POST'])
@admin_required
def delete_vehicle_route(vehicle_id):
    delete_vehicle(vehicle_id)
    flash('Vehicle record deleted.', 'success')
    return redirect(url_for('admin.history'))

@admin_bp.route('/receipt/generate/<int:vehicle_id>')
@admin_required
def generate_receipt(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle['status'] != 'exited':
        flash('Receipt only available for exited vehicles.', 'error')
        return redirect(url_for('admin.history'))
    receipt = generate_receipt_pdf(vehicle)
    return redirect(url_for('admin.download_receipt', filename=receipt))

@admin_bp.route('/api/revenue')
@admin_required
def api_revenue():
    daily = get_daily_revenue(30)
    monthly = get_monthly_revenue(12)
    return jsonify({
        'daily': [{'day': str(r['day']), 'revenue': float(r['revenue'])} for r in daily],
        'monthly': [{'month': r['month'], 'revenue': float(r['revenue'])} for r in monthly]
    })
