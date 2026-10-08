import serial
import mysql.connector
import time
import re


# =========================================================
# CONFIGURATION
# =========================================================

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200

SESSION_DURATION = 60


# =========================================================
# CONNECT TO ARDUINO
# =========================================================

arduino = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=0.1
)

time.sleep(2)

arduino.reset_input_buffer()


# =========================================================
# CONNECT TO MYSQL
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="health_monitor"
)

cursor = db.cursor()


# =========================================================
# CREATE SESSION
# =========================================================

session_id = int(time.time())

print()
print("========================================")
print("   HEART RATE MONITORING STARTED")
print("========================================")
print("Session ID:", session_id)
print("Monitoring for 60 seconds...")
print()


# =========================================================
# START TIMER
# =========================================================

start_time = time.monotonic()

reading_count = 0


# =========================================================
# COLLECT DATA
# =========================================================

try:

    while time.monotonic() - start_time < SESSION_DURATION:

        line = arduino.readline().decode(
            errors="ignore"
        ).strip()


        if not line:
            continue


        # -------------------------------------------------
        # Ignore Beat! messages
        # -------------------------------------------------

        if line == "Beat!":
            continue


        # -------------------------------------------------
        # Extract:
        #
        # Heart rate:66.75bpm / SpO2:96%
        #
        # HR   = 66.75
        # SpO2 = 96
        # -------------------------------------------------

        match = re.search(
            r"Heart rate:([\d.]+)bpm\s*/\s*SpO2:([\d.]+)%",
            line
        )


        if not match:

            print("Invalid data received:", line)

            continue


        heart_rate = float(match.group(1))
        spo2 = float(match.group(2))


        # =================================================
        # DISPLAY
        # =================================================

        print(
            f"HR: {heart_rate:.2f} BPM | "
            f"SpO2: {spo2:.2f}%"
        )


        # =================================================
        # SAVE TO MYSQL
        # =================================================

        query = """
            INSERT INTO sensor_readings
            (session_id, heart_rate, spo2)
            VALUES (%s, %s, %s)
        """


        cursor.execute(
            query,
            (
                session_id,
                heart_rate,
                spo2
            )
        )


        db.commit()

        reading_count += 1

        print("SAVED TO MYSQL")


# =========================================================
# FINISH
# =========================================================

finally:

    print()
    print("========================================")
    print("      60 SECONDS COMPLETED")
    print("========================================")

    print("Session ID:", session_id)
    print("Total readings:", reading_count)

    print()
    print("Stopping monitoring...")


    if arduino.is_open:
        arduino.close()

    print("Arduino connection closed.")


    cursor.close()
    db.close()

    print("MySQL connection closed.")


    print()
    print("Data has been saved to MySQL.")
    print("========================================")