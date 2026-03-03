from app.models.db import get_db_connection

def get_user_profile(user_id, role):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if role == 'rider':
                table = "riders"
                id_field = "riderID"
            elif role == 'driver':
                table = "drivers"
                id_field = "driverID"
            else:
                return {"error": "Invalid role"}, 400
            
            sql = f"SELECT email, phoneNumber, fullName, rating, totalRides, created_at FROM {table} WHERE {id_field} = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            
            if user:
                return user, 200
            return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        connection.close()
