# Automated Parking Management System
## CS50x 2024 Final Project

## Author: Sumedh Nadiger
## Date: 20th June 2024
## Video Demo: https://youtu.be/c7-6Kougrnc


## Project Overview:
Parking lots are essential part of society's funtioning. Checking in and checking a out of one in many places is still a manual task and requires physical presense of a person to get in and to pay the amount while getting out. 
This project aims to remove that by using Computer Vision technology to detect number plate while entering and exiting the parking space and automatically calculate the price according to the time spent in the parking lot. 

## Feature
* **Licence plate detection:** Utilizes a Haar cascade classifier and EasyOCR to detect and recognize vehicle number plates from camera footage.
* **Web App:** Uses flask with HTML and CSS with BootStap to create webapp
* **Database Management:** SQLITE3 is used to manage database to insert and delete vehicle entries

## Technologies Used
* **Python:** Programming language
* **SQLITE3:** Database management
* **Flask:** Web Application
* **OpenCV:** image recognistion and classification
* **EasyOCR:** Image to text conversion

## Project Design:
app.py is uses flask with HTML and CSS to create webapp which has 2 functionalities. Check-In and Check-Out. 

### Check IN 
Check In functionality uses CV2 library to initialise camera of device running and captures the frame. Then Haar cascade classifier is used to detect the coodinates of the rectangle of license plate. This is then fed to EasyOCR to convert to string data. 
As a pre-processing, all text that is not A-Z, a-z, 1-9 is rejected from the detection. There is also timeout functionality added for detection incase the detection is not completed in 10 sec. 
If multiple detections are seen, then again the data is rejected and manual entry option is provided to the user stating the failure of detection. 

If Detection fail:
Inputs are taken in the html form. 

The data is stored in sqlite database including the date and time information for the vehicle

After this, the image with detection is highlighted and the deteceted licence number is shown by rendering template checkedin.html

### Checkout 
Checkout feature similarly uses CV2 lib to detect and OCR to convert the licence plate info to text. This is then checked if the database if the vehicle exists. If it does not then error message is shown and manual input option is provided to the user. 
If found then time data is taken from the input and hours are converted to minutes and price is calcuated at 1 rupee per minute basis. 
This is then used to render the template of payment.html that shows the price. 

Pay button does not do anything at the moment. Future development is planned to integrate PayTM UPI functionality to integrate payment gateway for people to scan QR code and pay though UPI.

### Future Enhancement
* Add PayTM gateway for payment
* Enhance detection algorithm
* Implement history html that shows all the in out data + how many vehicles are in parking lot


