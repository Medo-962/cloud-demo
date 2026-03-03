import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.db import get_db_connection
from pymysql.err import IntegrityError
from datetime import datetime, timedelta

def register_user(role, data):
    # role is 'rider' or 'driver'
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            email = data.get('email')
            phone = data.get('phoneNumber')
            password = data.get('password')
            full_name = data.get('fullName')
            
            if not all([email, phone, password, full_name]):
                return {"error": "Missing required fields"}, 400

            hashed_password = generate_password_hash(password)
            
            if role == 'rider':
                sql = """
                    INSERT INTO riders (email, phoneNumber, passwordHash, fullName)
                    VALUES (%s, %s, %s, %s)
                """
            elif role == 'driver':
                sql = """
                    INSERT INTO drivers (email, phoneNumber, passwordHash, fullName)
                    VALUES (%s, %s, %s, %s)
                """
            else:
                return {"error": "Invalid role"}, 400

            try:
                cursor.execute(sql, (email, phone, hashed_password, full_name))
                user_id = cursor.lastrowid
                return {"message": f"{role.capitalize()} registered successfully", "id": user_id}, 201
            except IntegrityError:
                return {"error": "Email or phone number already exists"}, 409
    finally:
        connection.close()


def authenticate_user(role, email, password):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if role == 'rider':
                sql = "SELECT riderID as id, passwordHash, fullName FROM riders WHERE email = %s"
            elif role == 'driver':
                sql = "SELECT driverID as id, passwordHash, fullName FROM drivers WHERE email = %s"
            else:
                return {"error": "Invalid role"}, 400

            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['passwordHash'], password):
                # Update last login
                update_sql = f"UPDATE {role}s SET lastLogin = NOW() WHERE {'riderID' if role == 'rider' else 'driverID'} = %s"
                cursor.execute(update_sql, (user['id'],))
                return {"id": user['id'], "fullName": user['fullName'], "role": role}, 200
            else:
                return {"error": "Invalid credentials"}, 401
    finally:
        connection.close()
