import pymysql
pymysql.install_as_MySQLdb()

import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
mysql = MySQL()

def create_app():
    app = Flask(_name_, template_folder='app/templates', static_folder='app/static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        url = urlparse(database_url)

        app.config['MYSQL_HOST'] = url.hostname
        app.config['MYSQL_USER'] = url.username
        app.config['MYSQL_PASSWORD'] = url.password
        app.config['MYSQL_DB'] = url.path[1:]
        app.config['MYSQL_PORT'] = url.port or 3306
    else:
        app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
        app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
        app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
        app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'parking_db')
        app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    return app


app = create_app()   # required for gunicorn