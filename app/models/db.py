from app import mysql

# ─── USER MODEL ────────────────────────────────────────────────────────────────

def get_user_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return user

def create_user(username, hashed_password, role='user'):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_password, role))
    mysql.connection.commit()
    cur.close()

def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    return users

def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s AND role != 'admin'", (user_id,))
    mysql.connection.commit()
    cur.close()

# ─── SLOT MODEL ────────────────────────────────────────────────────────────────

def get_all_slots():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM slots ORDER BY id")
    slots = cur.fetchall()
    cur.close()
    return slots

def get_available_slot():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM slots WHERE status = 'available' ORDER BY id LIMIT 1")
    slot = cur.fetchone()
    cur.close()
    return slot['id'] if slot else None

def set_slot_status(slot_id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE slots SET status = %s WHERE id = %s", (status, slot_id))
    mysql.connection.commit()
    cur.close()

def get_slot_counts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT status, COUNT(*) as count FROM slots GROUP BY status")
    rows = cur.fetchall()
    cur.close()
    counts = {'available': 0, 'occupied': 0}
    for r in rows:
        counts[r['status']] = r['count']
    return counts

# ─── VEHICLE MODEL ─────────────────────────────────────────────────────────────

def add_vehicle(vehicle_number, owner_name, user_id, slot_number):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO vehicles (vehicle_number, owner_name, user_id, slot_number, status, entry_time)
        VALUES (%s, %s, %s, %s, 'parked', NOW())
    """, (vehicle_number.upper(), owner_name, user_id, slot_number))
    mysql.connection.commit()
    vid = cur.lastrowid
    cur.close()
    return vid

def get_vehicle_by_number(vehicle_number):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vehicles WHERE vehicle_number = %s AND status = 'parked'",
                (vehicle_number.upper(),))
    v = cur.fetchone()
    cur.close()
    return v

def get_vehicle_by_id(vehicle_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT v.*, u.username FROM vehicles v JOIN users u ON v.user_id = u.id WHERE v.id = %s",
                (vehicle_id,))
    v = cur.fetchone()
    cur.close()
    return v

def exit_vehicle(vehicle_id, fee):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE vehicles SET exit_time = NOW(), fee = %s, status = 'exited'
        WHERE id = %s
    """, (fee, vehicle_id))
    mysql.connection.commit()
    cur.close()

def delete_vehicle(vehicle_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT slot_number, status FROM vehicles WHERE id = %s", (vehicle_id,))
    v = cur.fetchone()
    if v and v['status'] == 'parked' and v['slot_number']:
        set_slot_status(v['slot_number'], 'available')
    cur.execute("DELETE FROM vehicles WHERE id = %s", (vehicle_id,))
    mysql.connection.commit()
    cur.close()

def get_all_vehicles(search=None, sort='entry_time', order='desc'):
    allowed_sort = ['vehicle_number', 'owner_name', 'entry_time', 'exit_time', 'fee', 'status', 'slot_number']
    allowed_order = ['asc', 'desc']
    sort = sort if sort in allowed_sort else 'entry_time'
    order = order if order in allowed_order else 'desc'
    cur = mysql.connection.cursor()
    if search:
        like = f"%{search}%"
        cur.execute(f"""
            SELECT v.*, u.username FROM vehicles v JOIN users u ON v.user_id = u.id
            WHERE v.vehicle_number LIKE %s OR v.owner_name LIKE %s OR u.username LIKE %s
            ORDER BY v.{sort} {order}
        """, (like, like, like))
    else:
        cur.execute(f"""
            SELECT v.*, u.username FROM vehicles v JOIN users u ON v.user_id = u.id
            ORDER BY v.{sort} {order}
        """)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_user_vehicles(user_id, search=None, sort='entry_time', order='desc'):
    allowed_sort = ['vehicle_number', 'owner_name', 'entry_time', 'exit_time', 'fee', 'status', 'slot_number']
    allowed_order = ['asc', 'desc']
    sort = sort if sort in allowed_sort else 'entry_time'
    order = order if order in allowed_order else 'desc'
    cur = mysql.connection.cursor()
    if search:
        like = f"%{search}%"
        cur.execute(f"""
            SELECT * FROM vehicles
            WHERE user_id = %s AND (vehicle_number LIKE %s OR owner_name LIKE %s)
            ORDER BY {sort} {order}
        """, (user_id, like, like))
    else:
        cur.execute(f"SELECT * FROM vehicles WHERE user_id = %s ORDER BY {sort} {order}", (user_id,))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_currently_parked():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT v.*, u.username FROM vehicles v JOIN users u ON v.user_id = u.id
        WHERE v.status = 'parked' ORDER BY v.entry_time DESC
    """)
    rows = cur.fetchall()
    cur.close()
    return rows

# ─── REVENUE MODEL ─────────────────────────────────────────────────────────────

def get_total_revenue():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COALESCE(SUM(fee), 0) as total FROM vehicles WHERE status = 'exited'")
    row = cur.fetchone()
    cur.close()
    return float(row['total'])

def get_daily_revenue(days=30):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE(exit_time) as day, COALESCE(SUM(fee), 0) as revenue
        FROM vehicles WHERE status = 'exited' AND exit_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(exit_time) ORDER BY day ASC
    """, (days,))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_monthly_revenue(months=12):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(exit_time, '%%Y-%%m') as month, COALESCE(SUM(fee), 0) as revenue
        FROM vehicles WHERE status = 'exited' AND exit_time >= DATE_SUB(NOW(), INTERVAL %s MONTH)
        GROUP BY DATE_FORMAT(exit_time, '%%Y-%%m') ORDER BY month ASC
    """, (months,))
    rows = cur.fetchall()
    cur.close()
    return rows
