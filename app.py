""" 
Author: Sumedh Nadiger
Date: 20/6/2024

Project for CS50x 2024 Final project
"""

# Import all essential library
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import easyocr
import re
import time



# Configure application
app = Flask(__name__)

# Configure database
db = SQL("sqlite:///parking.db")

# Configure date and time
dt = datetime.datetime.now()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Function to detect number plate and return the detected text as form of list
# Adapted detection algorithm from https://github.com/entbappy/Car-Number-Plates-Detection
def detect_num_plate():
    harcascade = "model/haarcascade_russian_plate_number.xml"
    count =0

    # Define the timeout duration
    timeout = 10  # seconds

    # Minimum accepted area
    min_area = 500
    flag=1

    # Record the start time
    start_time = time.time()

    # Keep trying to capture until succefull license plate capture
    while flag:

        # Check the elapsed time. If greater than 10 sec then exit without detection
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print("Timeout reached, exiting loop.")
            break

        # Wait before capture
        cv2.waitKey(500)
        # Capture frame
        cap = cv2.VideoCapture(0)

        cap.set(3, 640) # width
        cap.set(4, 480) #height
        
        success, img = cap.read()

        # Pre-Porcess the image
        plate_cascade = cv2.CascadeClassifier(harcascade)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

        # For all the plates detected, check area
        for (x,y,w,h) in plates:
            area = w * h

            # Check if detected rectangle is greater than the min area defined
            if area > min_area:
                #Area detected so turn flag to 0. No more detecting required
                flag=0

                # Draw rectangle around detection
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(img, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                # Crop the image to only detected area
                img_roi = img[y: y+h, x:x+w]
    
                # Extract text from image using easyOCR
                reader = easyocr.Reader(['en'])
                result = reader.readtext(img_roi)

                # Write the detection into an image to display
                cv2.imwrite("static/scaned_img_" + str(count) + ".jpg", img)
                count += 1

                # Return the detected texts
                texts = [text for (_, text, _) in result]
                return(texts)


# Default route
@app.route("/")
def index():
    return render_template("index.html") #Render default index.html

# Check-In route
@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "GET":

        # Detect number plate
        num_plate = detect_num_plate()


        # Pre-Process the number plate to remove unwanted inputs
        try:
            num_plate = num_plate[0].replace(" ","")
        except Exception:
            return render_template("checkin.html", error="Detection Fail. Add manually")
        
        num_plate = num_plate.upper()
        num_plate = re.sub(r'[^A-Za-z0-9 ]+', '', num_plate)

        # Insert into database. If exception, its because the car is already in parking lot. Throw error
        try:
            db.execute("INSERT INTO parking (veh_num, day, month, year, hour, min) VALUES(?,?,?,?,?,?)", num_plate, dt.day, dt.month, dt.year, dt.hour,dt.minute)
        except Exception:
            return render_template("checkin.html", error="cant checkin twice")
        
        # Show the detected number plate 
        return render_template("checkedin.html", num_plate=num_plate)
    else:
        veh_num = request.form.get("number")
        veh_num = veh_num.replace(" ","")
        veh_num = veh_num.upper()
        try:
            db.execute("INSERT INTO parking (veh_num, day, month, year, hour, min) VALUES(?,?,?,?,?,?)", veh_num, dt.day, dt.month, dt.year, dt.hour,dt.minute)
        except Exception:
            return render_template("checkin.html", error="cant checkin twice")

        return render_template("checkedin.html", num_plate=veh_num)

# CheckOut Route
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        # Detect number plate
        num_plate = detect_num_plate()

        # Pre-Process the number plate to remove unwanted inputs
        try:
            num_plate = num_plate[0].replace(" ","")
        except Exception:
            return render_template("checkout.html", error="Detection Fail. Add manually")
        
        num_plate = num_plate.upper()
        ret_hour = db.execute("SELECT hour FROM parking WHERE veh_num=?", num_plate)
        ret_min = db.execute("SELECT min FROM parking WHERE veh_num=?", num_plate)

        # Empty return means there is no such car checked-in. Allow to checkout manually
        if not ret_hour:
            return render_template("checkout.html", error="Vehicle not checked-in. Enter manually to check")
        
        # Calculate time spent in parking lot
        ci_hour = ret_hour[0]["hour"]
        ci_minute = ret_min[0]["min"]
        hours = dt.hour - ci_hour
        minutes = dt.minute - ci_minute
        minutes += hours*60

        # Delete from database
        try:
            db.execute("DELETE FROM parking WHERE veh_num=?", num_plate)
        except Exception:
            return render_template("checkout.html", error="Vehicle not checked-in")
        
        return render_template("payment.html", min=minutes)
        # return render_template("checkout.html",error="")
    else:
        veh_num = request.form.get("number")
        veh_num = veh_num.replace(" ","")
        veh_num = veh_num.upper()
        ret_hour = db.execute("SELECT hour FROM parking WHERE veh_num=?", veh_num)
        ret_min = db.execute("SELECT min FROM parking WHERE veh_num=?", veh_num)
        ret_date = db.execute("SELECT day FROM parking WHERE veh_num=?", veh_num)
        ret_month = db.execute("SELECT month FROM parking WHERE veh_num=?", veh_num)

        if not ret_hour:
            return render_template("checkout.html", error="Vehicle not checked-in")


        ci_hour = ret_hour[0]["hour"]
        ci_minute = ret_min[0]["min"]

        hours = dt.hour - ci_hour
        minutes = dt.minute - ci_minute

        minutes += hours*60

        try:
            db.execute("DELETE FROM parking WHERE veh_num=?", veh_num)
        except Exception:
            return render_template("checkout.html", error="Vehicle not checked-in")

        return render_template("payment.html", min=minutes)

