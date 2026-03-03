from app.models.db import get_db_connection
from app.services.map_service import calculate_distance_time

def estimate_price(origin, destination):
    distance_km, duration_min = calculate_distance_time(origin, destination)
    
    if distance_km is None or duration_min is None:
        return {"error": "Could not calculate distance and duration. Please check the addresses."}, 400
        
    # User's pricing formula: base = 1, km = 0.18, min = 0.11
    base_fare = 1.0
    price_km = distance_km * 0.18
    price_min = duration_min * 0.11
    
    estimated_price = base_fare + price_km + price_min
    
    return {
        "distanceKM": round(distance_km, 2),
        "durationMin": round(duration_min, 2),
        "estimatedPrice": round(estimated_price, 2)
    }, 200

def create_ride_request(rider_id, data):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            pickup_address = data.get('pickupAddress')
            dropoff_address = data.get('dropoffAddress')
            pickup_lat = data.get('pickupLat')
            pickup_lng = data.get('pickupLng')
            dropoff_lat = data.get('dropoffLat')
            dropoff_lng = data.get('dropoffLng')
            
            # Recalculate directly to avoid manipulation from client
            origin = f"{pickup_lat},{pickup_lng}"
            destination = f"{dropoff_lat},{dropoff_lng}"
            
            pricing_data, status_code = estimate_price(origin, destination)
            
            if status_code != 200:
                return pricing_data, status_code

            distance_km = pricing_data['distanceKM']
            estimated_price = pricing_data['estimatedPrice']
            
            sql = """
                INSERT INTO rides (
                    riderID, pickupAddress, dropoffAddress, 
                    pickupLat, pickupLng, dropoffLat, dropoffLng, 
                    distanceKM, estimatedPrice, rideStatus, paymentMethod
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'requested', %s)
            """
            
            payment_method = data.get('paymentMethod', 'cash')
            
            cursor.execute(sql, (
                rider_id, pickup_address, dropoff_address,
                pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
                distance_km, estimated_price, payment_method
            ))
            
            ride_id = cursor.lastrowid
            
            return {
                "message": "Ride requested successfully",
                "rideID": ride_id,
                "distanceKM": distance_km,
                "estimatedPrice": estimated_price,
                "status": "requested"
            }, 201
    finally:
        connection.close()

def update_ride_status(ride_id, driver_id, status):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if status == 'accepted':
                sql = "UPDATE rides SET rideStatus = %s, driverID = %s, accepted_at = NOW() WHERE rideID = %s And rideStatus = 'requested'"
                affected = cursor.execute(sql, (status, driver_id, ride_id))
            elif status == 'in_progress':
                sql = "UPDATE rides SET rideStatus = %s, started_at = NOW() WHERE rideID = %s AND driverID = %s"
                affected = cursor.execute(sql, (status, ride_id, driver_id))
            elif status == 'completed':
                 sql = "UPDATE rides SET rideStatus = %s, completed_at = NOW() WHERE rideID = %s AND driverID = %s"
                 affected = cursor.execute(sql, (status, ride_id, driver_id))
            else:
                 return {"error": "Invalid status update"} , 400
                 
            if affected == 0:
                 return {"error": "Ride not found or status cannot be updated"}, 400
                 
            return {"message": f"Ride {status}"}, 200
    finally:
         connection.close()

def get_recent_rides(user_id, role):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if role == 'rider':
                sql = """
                    SELECT rideID, pickupAddress, dropoffAddress, distanceKM, estimatedPrice, 
                           rideStatus, requested_at, completed_at
                    FROM rides
                    WHERE riderID = %s
                    ORDER BY requested_at DESC LIMIT 10
                """
            elif role == 'driver':
                sql = """
                    SELECT rideID, pickupAddress, dropoffAddress, distanceKM, estimatedPrice, 
                           rideStatus, requested_at, completed_at
                    FROM rides
                    WHERE driverID = %s
                    ORDER BY requested_at DESC LIMIT 10
                """
            else:
                 return {"error": "Invalid role"} , 400
                 
            cursor.execute(sql, (user_id,))
            rides = cursor.fetchall()
            return rides, 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        connection.close()
