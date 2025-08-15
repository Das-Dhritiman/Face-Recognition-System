import tkinter as tk
from tkinter import *
import os
import cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import pyttsx3

# Import project modules
import show_attendance
import takeImage
import trainImage
import automaticAttedance

# Set working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()

# Path configurations
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
trainimage_path = "TrainingImage"
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)

studentdetail_path = "./StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

# Main window setup
window = Tk()
window.title("Face Recognizer")
window.geometry("1280x720")
window.configure(background="#1c1c1c")

# Function to destroy error screen
def del_sc1():
    sc1.destroy()

# Error message function
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry("400x110")
    sc1.iconbitmap("AMS.ico")
    sc1.title("Warning!!")
    sc1.configure(background="#1c1c1c")
    sc1.resizable(0, 0)
    tk.Label(
        sc1,
        text="Enrollment & Name required!!!",
        fg="yellow",
        bg="#1c1c1c",
        font=("Verdana", 16, "bold"),
    ).pack()
    tk.Button(
        sc1,
        text="OK",
        command=del_sc1,
        fg="yellow",
        bg="#333333",
        width=9,
        height=1,
        activebackground="red",
        font=("Verdana", 16, "bold"),
    ).place(x=110, y=50)

def testVal(inStr, acttyp):
    if acttyp == "1":  # insert
        if not inStr.isdigit():
            return False
    return True

# Load logo image
try:
    logo = Image.open("UI_Image/0001.png")
    logo = logo.resize((50, 47), Image.LANCZOS)
    logo1 = ImageTk.PhotoImage(logo)
except FileNotFoundError:
    print("Logo image not found. Using placeholder.")
    logo = Image.new('RGB', (50, 47), color='gray')
    logo1 = ImageTk.PhotoImage(logo)

# Header section
header_frame = Frame(window, bg="#1c1c1c")
header_frame.pack(fill='x', pady=10)

# Logo label
ll = Label(header_frame, image=logo1, bg="#1c1c1c")
ll.pack(side='left', padx=20)

# Title label
titl = Label(
    header_frame, 
    text="EMPLOYEE ATTENDANCE DASHBOARD", 
    bg="#2c1db1", 
    fg="yellow", 
    font=("Verdana", 27, "bold")
)
titl.pack(side='left', expand=True)

# Welcome message
welcome_label = Label(
    window,
    text="Attendance System",
    bg="#2a8795",
    fg="yellow",
    bd=10,
    font=("Verdana", 35, "bold"),
)
welcome_label.pack(pady=20)

# Function to load button images
def load_button_image(image_name, size=(200, 200)):
    try:
        img = Image.open(f"UI_Image/{image_name}")
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except FileNotFoundError:
        print(f"Image UI_Image/{image_name} not found. Using placeholder.")
        img = Image.new('RGB', size, color='gray')
        return ImageTk.PhotoImage(img)

# Load button images
register_img = load_button_image("register.png")
attendance_img = load_button_image("attendance.png")
verify_img = load_button_image("verifyy.png")

# Create image labels
register_label = Label(window, image=register_img, bg="#1c1c1c")
register_label.image = register_img
register_label.place(x=100, y=270)

attendance_label = Label(window, image=attendance_img, bg="#1c1c1c")
attendance_label.image = attendance_img
attendance_label.place(x=980, y=270)

verify_label = Label(window, image=verify_img, bg="#1c1c1c")
verify_label.image = verify_img
verify_label.place(x=600, y=270)

# Take Image UI function
def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("Take Student Image..")
    ImageUI.geometry("780x480")
    ImageUI.configure(background="#1c1c1c")
    ImageUI.resizable(0, 0)
    
    titl = tk.Label(ImageUI, bg="#1c1c1c", relief=RIDGE, bd=10, font=("Verdana", 30, "bold"))
    titl.pack(fill=X)
    
    titl = tk.Label(
        ImageUI, text="Register Your Face", bg="#1c1c1c", fg="green", font=("Verdana", 30, "bold"),
    )
    titl.place(x=270, y=12)

    a = tk.Label(
        ImageUI,
        text="Enter the details",
        bg="#1c1c1c",
        fg="yellow",
        bd=10,
        font=("Verdana", 24, "bold"),
    )
    a.place(x=280, y=75)

    # Enrollment No
    lbl1 = tk.Label(
        ImageUI,
        text="Enrollment No",
        width=10,
        height=2,
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl1.place(x=120, y=130)
    txt1 = tk.Entry(
        ImageUI,
        width=17,
        bd=5,
        validate="key",
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 18, "bold"),
    )
    txt1.place(x=250, y=130)
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Name
    lbl2 = tk.Label(
        ImageUI,
        text="Name",
        width=10,
        height=2,
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl2.place(x=120, y=200)
    txt2 = tk.Entry(
        ImageUI,
        width=17,
        bd=5,
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 18, "bold"),
    )
    txt2.place(x=250, y=200)

    # Notification
    lbl3 = tk.Label(
        ImageUI,
        text="Notification",
        width=10,
        height=2,
        bg="#1c1c1c",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl3.place(x=120, y=270)

    message = tk.Label(
        ImageUI,
        text="",
        width=32,
        height=2,
        bd=5,
        bg="#333333",
        fg="yellow",
        relief=RIDGE,
        font=("Verdana", 14, "bold"),
    )
    message.place(x=250, y=270)

    def take_image():
        l1 = txt1.get()
        l2 = txt2.get()
        takeImage.TakeImage(
            l1,
            l2,
            haarcasecade_path,
            trainimage_path,
            message,
            err_screen,
            text_to_speech,
        )
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    # Take Image button
    takeImg = tk.Button(
        ImageUI,
        text="Take Image",
        command=take_image,
        bd=10,
        font=("Verdana", 18, "bold"),
        bg="#333333",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    takeImg.place(x=130, y=350)

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            message,
            text_to_speech,
        )

    # Train Image button
    trainImg = tk.Button(
        ImageUI,
        text="Train Image",
        command=train_image,
        bd=10,
        font=("Verdana", 18, "bold"),
        bg="#333333",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    trainImg.place(x=360, y=350)

# Main buttons
# [Previous imports and setup code remains the same...]

# Main buttons - Fixed to pass text_to_speech argument
register_btn = tk.Button(
    window,
    text="Register a new student",
    command=TakeImageUI,
    bd=10,
    font=("Verdana", 16),
    bg="black",
    fg="yellow",
    height=2,
    width=17,
)
register_btn.place(x=100, y=520)

# Fixed attendance button
attendance_btn = tk.Button(
    window,
    text="Take Attendance",
    command=lambda: automaticAttedance.subjectChoose(text_to_speech),
    bd=10,
    font=("Verdana", 16),
    bg="black",
    fg="yellow",
    height=2,
    width=17,
)
attendance_btn.place(x=600, y=520)

# Fixed view attendance button
view_btn = tk.Button(
    window,
    text="View Attendance",
    command=lambda: show_attendance.subjectchoose(text_to_speech),
    bd=10,
    font=("Verdana", 16),
    bg="black",
    fg="yellow",
    height=2,
    width=17,
)
view_btn.place(x=1000, y=520)

exit_btn = tk.Button(
    window,
    text="EXIT",
    bd=10,
    command=window.quit,
    font=("Verdana", 16),
    bg="black",
    fg="yellow",
    height=2,
    width=17,
)
exit_btn.place(x=600, y=660)

window.mainloop()