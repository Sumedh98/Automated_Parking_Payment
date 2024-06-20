import os
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import easyocr




# Configure application
app = Flask(__name__)

db = SQL("sqlite:///parking.db")
dt = datetime.datetime.now()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def detect_num_plate():
    harcascade = "model/haarcascade_russian_plate_number.xml"
    count =0

    cv2.waitKey(500)
    cap = cv2.VideoCapture(0)
    
    cap.set(3, 640) # width
    cap.set(4, 480) #height
    
    min_area = 500
    flag=1
    
    # while True:
    while flag:
        success, img = cap.read()
        plate_cascade = cv2.CascadeClassifier(harcascade)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)
        for (x,y,w,h) in plates:
            area = w * h
            if area > min_area:
                flag=0
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(img, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
                img_roi = img[y: y+h, x:x+w]
    
                
                reader = easyocr.Reader(['en'])
                result = reader.readtext(img_roi)
                # cv2.rectangle(img, (0,200), (640,300), (0,255,0), cv2.FILLED)
                cv2.imwrite("static/scaned_img_" + str(count) + ".jpg", img)
                count += 1

                texts = [text for (_, text, _) in result]
                return(texts)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "GET":
        num_plate = detect_num_plate()
        num_plate = num_plate[0].replace(" ","")
        num_plate = num_plate.upper()
        try:
            db.execute("INSERT INTO parking (veh_num, day, month, year, hour, min) VALUES(?,?,?,?,?,?)", num_plate, dt.day, dt.month, dt.year, dt.hour,dt.minute)
        except Exception:
            return render_template("checkin.html", error="cant checkin twice")
        
        return render_template("checkedin.html", num_plate=num_plate)
        # return redirect("/")
        # return render_template("checkin.html",error="")
    else:
        veh_num = request.form.get("number")
        veh_num = veh_num.replace(" ","")
        veh_num = veh_num.upper()
        try:
            db.execute("INSERT INTO parking (veh_num, day, month, year, hour, min) VALUES(?,?,?,?,?,?)", num_plate, dt.day, dt.month, dt.year, dt.hour,dt.minute)
        except Exception:
            return render_template("checkin.html", error="cant checkin twice")

        return redirect("/")


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        num_plate = detect_num_plate()
        num_plate = num_plate[0].replace(" ","")
        num_plate = num_plate.upper()
        ret_hour = db.execute("SELECT hour FROM parking WHERE veh_num=?", num_plate)
        ret_min = db.execute("SELECT min FROM parking WHERE veh_num=?", num_plate)

        if not ret_hour:
            return render_template("checkout.html", error="Vehicle not checked-in")

        ci_hour = ret_hour[0]["hour"]
        ci_minute = ret_min[0]["min"]

        hours = dt.hour - ci_hour
        minutes = dt.minute - ci_minute

        minutes += hours*60

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

