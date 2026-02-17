# Mashup Generator

Live App:
https://mashup-generator-4fgx.onrender.com/

---

## Project Overview

This is a Flask-based web application that:

• downloads songs from YouTube  
• extracts audio clips  
• creates a mashup  
• sends the mashup via email  

---

## Technologies Used

Python  
Flask  
yt-dlp  
MoviePy  
SMTP Email  

---

## How It Works

1. User enters singer name and options  
2. Songs are downloaded automatically  
3. Clips are extracted and merged  
4. Mashup is created  
5. File is sent to user via email  

---

## Run Locally

Install dependencies:

pip install -r requirements.txt

Run:

python app.py

Open browser:

http://127.0.0.1:5000
# Mashup Generator

A Flask web application that:

• downloads songs from YouTube  
• extracts audio  
• cuts the first X seconds  
• merges clips into a mashup  
• sends the mashup via email  

## Technologies
Python, Flask, yt-dlp, MoviePy, Pydub

## Run

python app.py

