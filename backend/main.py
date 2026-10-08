from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# MYSQL CONFIGURATION
# =====================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Jeff@123",
    "database": "health_monitor"
}


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Health Monitor Backend is running"
    }


# =====================================================
# ANALYZE
# =====================================================

@app.get("/analyze")
def analyze():

    # Connect to MySQL
    db = mysql.connector.connect(**DB_CONFIG)

    cursor = db.cursor(dictionary=True)


    # -------------------------------------------------
    # Find latest session
    # -------------------------------------------------

    cursor.execute("""
        SELECT session_id
        FROM sensor_readings
        ORDER BY id DESC
        LIMIT 1
    """)

    latest_session = cursor.fetchone()


    if latest_session is None:

        cursor.close()
        db.close()

        return {
            "message": "No sensor data available"
        }


    session_id = latest_session["session_id"]


    # -------------------------------------------------
    # Get readings for that session
    # -------------------------------------------------

    cursor.execute("""
        SELECT heart_rate, spo2, timestamp
        FROM sensor_readings
        WHERE session_id = %s
        ORDER BY timestamp
    """, (session_id,))

    readings = cursor.fetchall()


    cursor.close()
    db.close()


    # -------------------------------------------------
    # Extract values
    # -------------------------------------------------

    heart_rates = [
        reading["heart_rate"]
        for reading in readings
    ]

    spo2_values = [
        reading["spo2"]
        for reading in readings
    ]


    # -------------------------------------------------
    # Basic calculations
    # -------------------------------------------------

    average_heart_rate = sum(heart_rates) / len(heart_rates)

    minimum_heart_rate = min(heart_rates)

    maximum_heart_rate = max(heart_rates)


    average_spo2 = sum(spo2_values) / len(spo2_values)

    minimum_spo2 = min(spo2_values)


    # -------------------------------------------------
    # Simple insight
    # -------------------------------------------------

    if maximum_heart_rate > 120:

        insight = "High heart-rate values detected."

    else:

        insight = "Heart-rate values remained within the basic threshold."


    # -------------------------------------------------
    # Return JSON
    # -------------------------------------------------

    return {

        "session_id": session_id,

        "reading_count": len(readings),

        "heart_rate": {
            "average": round(average_heart_rate, 2),
            "minimum": round(minimum_heart_rate, 2),
            "maximum": round(maximum_heart_rate, 2)
        },

        "spo2": {
            "average": round(average_spo2, 2),
            "minimum": round(minimum_spo2, 2)
        },

        "insight": insight
    }