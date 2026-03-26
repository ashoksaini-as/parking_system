"""
Run this once after creating the DB to ensure admin password is correctly hashed.
Usage: python init_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash

hashed = generate_password_hash('1234')
print("Admin password hash:")
print(hashed)
print()
print("Run this SQL to set it:")
print(f"UPDATE users SET password = '{hashed}' WHERE username = 'admin';")
print()
print("Or insert fresh admin:")
print(f"INSERT INTO users (username, password, role) VALUES ('admin', '{hashed}', 'admin') ON DUPLICATE KEY UPDATE password = '{hashed}';")
