import serial
import mysql.connector
import time


# =========================================================
# CONFIGURATION
# =========================================================

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200

SESSION_DURATION = 60  # seconds


# =========================================================
# CONNECT TO ARDUINO
# =========================================================

arduino = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=0.1
)


# Give Arduino a moment after opening serial connection
time.sleep(2)


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

    while True:

        # ---------------------------------------------
        # Check how much time has passed
        # ---------------------------------------------

        elapsed_time = time.monotonic() - start_time

        if elapsed_time >= SESSION_DURATION:
            break


        # ---------------------------------------------
        # Read data from Arduino
        # ---------------------------------------------

        line = arduino.readline().decode(
            errors="ignore"
        ).strip()


        # No data received
        if not line:
            continue


        # ---------------------------------------------
        # Expected Arduino format:
        #
        # 69.70,95
        # ---------------------------------------------

        try:

            heart_rate, spo2 = line.split(",")

            heart_rate = float(heart_rate)
            spo2 = float(spo2)


            # -----------------------------------------
            # Display reading
            # -----------------------------------------

            print(
                f"HR: {heart_rate:.2f} BPM | "
                f"SpO2: {spo2:.2f}%"
            )


            # -----------------------------------------
            # Insert into MySQL
            # -----------------------------------------

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


            # Save the row permanently
            db.commit()

            print("SAVED TO MYSQL")


            reading_count += 1


        except ValueError:

            print(
                "Invalid data received:",
                line
            )


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


    # ---------------------------------------------
    # Close Arduino connection
    # ---------------------------------------------

    if arduino.is_open:
        arduino.close()

    print("Arduino connection closed.")


    # ---------------------------------------------
    # Close MySQL connection
    # ---------------------------------------------

    cursor.close()
    db.close()

    print("MySQL connection closed.")


    print()
    print("Data has been saved to MySQL.")
    print("========================================")