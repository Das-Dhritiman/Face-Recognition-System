import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Frame, Label, Button, Entry, RIDGE, X
from PIL import Image, ImageTk
import os
import cv2
import csv
import numpy as np
import pandas as pd
import datetime
import time
import pyttsx3
from glob import glob

# --- Main Application Class ---
class AttendanceApp:
    def __init__(self, window):
        """
        Initialize the main application window and its components.
        """
        self.window = window
        self.window.title("Face Recognition Attendance System")
        self.window.geometry("1280x720")
        self.window.configure(bg="#f0f0f0")
        self.window.resizable(True, True)

        # --- PATH CONFIGURATIONS ---
        # It's good practice to have these paths clearly defined.
        self.haarcasecade_path = "haarcascade_frontalface_default.xml"
        self.trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
        self.trainimage_path = "TrainingImage"
        self.studentdetail_path = "./StudentDetails/studentdetails.csv"
        self.attendance_path = "Attendance"
        
        # Create necessary directories if they don't exist
        for path in [self.trainimage_path, "TrainingImageLabel", "StudentDetails", self.attendance_path]:
            if not os.path.exists(path):
                os.makedirs(path)
        
        # Create student details CSV if it doesn't exist
        if not os.path.exists(self.studentdetail_path):
            with open(self.studentdetail_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Enrollment', 'Name'])


        # --- VOICE ENGINE SETUP ---
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        try:
            # Attempt to use a more natural voice (index 1 is often female on Windows)
            self.engine.setProperty('voice', voices[1].id)
        except IndexError:
            print("Default voice will be used.") # Fallback to default
        self.engine.setProperty('rate', 160) # Adjusted for clarity

        # --- UI STYLING ---
        self.style = ttk.Style(self.window)
        self.style.theme_use("clam")

        self.style.configure("TLabel", background="#f0f0f0", foreground="#333", font=("Segoe UI", 12))
        self.style.configure("Header.TLabel", font=("Segoe UI", 28, "bold"), foreground="#00529B")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 16, "italic"), foreground="#555")
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), foreground="white", background="#0078D7", padding=(10, 5))
        self.style.map("TButton", background=[('active', '#005A9E')])
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Card.TFrame", background="white", relief="raised", borderwidth=1)

        # --- MAIN LAYOUT ---
        self.create_main_widgets()
        self.text_to_speech("Welcome to the attendance system.")

    def text_to_speech(self, text):
        """
        Converts text to speech using the configured engine.
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text_to_speech: {e}")

    def create_main_widgets(self):
        """
        Creates and lays out the widgets on the main application window.
        """
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill="both")

        # --- Header ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(10, 40))
        
        try:
            logo_img = Image.open("UI_Image/logo.png").resize((60, 60), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=self.logo_photo, background="#f0f0f0")
            logo_label.pack(side="left", padx=(0, 20))
        except FileNotFoundError:
            print("Logo image not found.")

        title_label = ttk.Label(header_frame, text="Face Recognition Attendance", style="Header.TLabel")
        title_label.pack(side="left")

        # --- Action Buttons in Cards ---
        cards_frame = ttk.Frame(main_frame)
        cards_frame.pack(expand=True)

        actions = [
            ("Register New Student", self.open_registration_window, "UI_Image/register.png"),
            ("Take Attendance", self.open_attendance_subject_choice, "UI_Image/attendance.png"),
            ("View Attendance Report", self.open_view_attendance_choice, "UI_Image/verifyy.png")
        ]

        for i, (text, command, img_path) in enumerate(actions):
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=20)
            card.grid(row=0, column=i, padx=20, pady=20, sticky="ns")
            
            try:
                img = Image.open(img_path).resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(card, image=photo, background="white")
                img_label.image = photo
                img_label.pack(pady=(0, 15))
            except FileNotFoundError:
                # Placeholder if image not found
                img_label = ttk.Label(card, text=text.split()[0], font=("Segoe UI", 20, "bold"), background="white")
                img_label.pack(pady=(60, 75))


            button = ttk.Button(card, text=text, command=command, width=25)
            button.pack()

        # --- Exit Button ---
        exit_button = ttk.Button(main_frame, text="Exit Application", command=self.window.quit, width=20)
        exit_button.pack(pady=(40, 10))
        
    def open_registration_window(self):
        """
        Opens a new Toplevel window for student registration.
        """
        reg_window = Toplevel(self.window)
        reg_window.title("Register New Student")
        reg_window.geometry("600x500")
        reg_window.configure(bg="#f0f0f0")

        main_frame = ttk.Frame(reg_window, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Student Registration", style="Header.TLabel").pack(pady=(0, 20))

        # --- Form Fields ---
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Enrollment No:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        enroll_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        enroll_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Student Name:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        name_entry = ttk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=5)

        # --- Notification Area ---
        notification_label = ttk.Label(main_frame, text="", font=("Segoe UI", 10, "italic"), foreground="green")
        notification_label.pack(pady=(10, 10))
        
        def update_notification(msg, is_error=False):
            notification_label.config(text=msg, foreground="red" if is_error else "green")
            self.text_to_speech(msg)

        # --- Action Buttons ---
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)

        take_image_button = ttk.Button(
            buttons_frame, 
            text="Take Images", 
            command=lambda: self.take_image_action(
                enroll_entry.get(), 
                name_entry.get(), 
                update_notification
            )
        )
        take_image_button.pack(side="left", padx=10)

        train_image_button = ttk.Button(
            buttons_frame, 
            text="Train Model",
            command=lambda: self.train_image_action(update_notification)
        )
        train_image_button.pack(side="left", padx=10)

    def take_image_action(self, enrollment, name, notification_callback):
        """
        Logic to capture and save images for a new student.
        """
        if not enrollment or not name:
            notification_callback("Enrollment and Name are required.", is_error=True)
            return

        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                notification_callback("Could not open camera.", is_error=True)
                return

            detector = cv2.CascadeClassifier(self.haarcasecade_path)
            directory = f"{enrollment}_{name}"
            path = os.path.join(self.trainimage_path, directory)
            
            if os.path.exists(path):
                notification_callback("This student's data already exists.", is_error=True)
                return
            os.makedirs(path)

            sample_num = 0
            notification_callback("Look at the camera. Capturing images...")
            
            while True:
                ret, img = cam.read()
                if not ret:
                    break
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    sample_num += 1
                    cv2.imwrite(
                        f"{path}/{name}_{enrollment}_{sample_num}.jpg",
                        gray[y:y+h, x:x+w]
                    )
                    cv2.imshow("Capturing Images...", img)
                
                if cv2.waitKey(100) & 0xFF == ord('q') or sample_num >= 50:
                    break
            
            cam.release()
            cv2.destroyAllWindows()

            # Save student details to CSV
            with open(self.studentdetail_path, "a+", newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([enrollment, name])
            
            notification_callback(f"Images saved for {name}. Please train the model.")
        except Exception as e:
            notification_callback(f"An error occurred: {e}", is_error=True)
            if 'cam' in locals() and cam.isOpened():
                cam.release()
            cv2.destroyAllWindows()

    def train_image_action(self, notification_callback):
        """
        Trains the face recognizer model with the collected images.
        """
        notification_callback("Training model... Please wait.")
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            detector = cv2.CascadeClassifier(self.haarcasecade_path)
            
            faces, ids = self.get_images_and_labels(self.trainimage_path)
            if not faces:
                notification_callback("No images to train. Please register students first.", is_error=True)
                return

            recognizer.train(faces, np.array(ids))
            recognizer.save(self.trainimagelabel_path)
            notification_callback("Model trained successfully!")
        except Exception as e:
            notification_callback(f"Error during training: {e}", is_error=True)

    def get_images_and_labels(self, path):
        """
        Gets face images and their corresponding IDs from the training folder.
        """
        image_paths = []
        for dir_name in os.listdir(path):
            dir_path = os.path.join(path, dir_name)
            if os.path.isdir(dir_path):
                for file_name in os.listdir(dir_path):
                    image_paths.append(os.path.join(dir_path, file_name))

        faces = []
        ids = []
        for image_path in image_paths:
            try:
                pil_image = Image.open(image_path).convert("L")  # Convert to grayscale
                image_np = np.array(pil_image, "uint8")
                # Extract ID from filename: enrollment_name_id.jpg
                file_id = int(os.path.split(image_path)[-1].split("_")[1])
                faces.append(image_np)
                ids.append(file_id)
            except Exception as e:
                print(f"Skipping corrupted file {image_path}: {e}")
        return faces, ids

    def open_attendance_subject_choice(self):
        """
        Opens a window to enter the subject name for taking attendance.
        """
        self.create_subject_choice_window("Take Attendance", self.take_attendance_action)

    def open_view_attendance_choice(self):
        """
        Opens a window to enter the subject name for viewing attendance.
        """
        self.create_subject_choice_window("View Attendance Report", self.view_attendance_action)

    def create_subject_choice_window(self, title, command):
        """
        Generic window for entering a subject name.
        """
        sub_window = Toplevel(self.window)
        sub_window.title(f"{title} - Subject")
        sub_window.geometry("500x250")
        sub_window.configure(bg="#f0f0f0")

        main_frame = ttk.Frame(sub_window, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Enter Subject Name", style="Subheader.TLabel").pack(pady=(0, 20))

        subject_entry = ttk.Entry(main_frame, font=("Segoe UI", 12), width=30)
        subject_entry.pack(pady=10)

        action_button = ttk.Button(
            main_frame,
            text=title,
            command=lambda: command(subject_entry.get(), sub_window)
        )
        action_button.pack(pady=20)

    def take_attendance_action(self, subject, parent_window):
        """
        Logic for recognizing faces and marking attendance.
        """
        if not subject:
            messagebox.showerror("Error", "Please enter a subject name.", parent=parent_window)
            return
        
        parent_window.destroy()
        self.text_to_speech(f"Starting attendance for {subject}. Look at the camera.")

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            if not os.path.exists(self.trainimagelabel_path):
                messagebox.showerror("Error", "Model not found. Please train the model first.")
                return
            recognizer.read(self.trainimagelabel_path)
            
            face_cascade = cv2.CascadeClassifier(self.haarcasecade_path)
            df = pd.read_csv(self.studentdetail_path)
            
            cam = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            attendance = pd.DataFrame(columns=["Enrollment", "Name"])
            
            # Capture for 20 seconds
            start_time = time.time()
            end_time = start_time + 20

            while time.time() < end_time:
                ret, im = cam.read()
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    face_id, conf = recognizer.predict(gray[y:y+h, x:x+w])

                    if conf < 70:  # Confidence threshold
                        student_name = df.loc[df["Enrollment"] == face_id]["Name"].values[0]
                        display_text = f"{student_name} ({face_id})"
                        
                        # Add to attendance if not already present
                        if face_id not in attendance["Enrollment"].values:
                            new_entry = pd.DataFrame([{"Enrollment": face_id, "Name": student_name}])
                            attendance = pd.concat([attendance, new_entry], ignore_index=True)
                            self.text_to_speech(f"Hello {student_name}")

                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(im, display_text, (x, y - 10), font, 0.75, (0, 255, 0), 2)
                    else:
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(im, "Unknown", (x, y - 10), font, 0.75, (0, 0, 255), 2)
                
                cv2.imshow(f"Attendance for {subject}", im)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cam.release()
            cv2.destroyAllWindows()
            
            if not attendance.empty:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timestamp = datetime.datetime.fromtimestamp(ts).strftime("%H-%M-%S")
                
                subject_path = os.path.join(self.attendance_path, subject)
                if not os.path.exists(subject_path):
                    os.makedirs(subject_path)
                
                file_name = f"{subject}_{date}_{timestamp}.csv"
                file_path = os.path.join(subject_path, file_name)
                
                attendance.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Attendance for {subject} saved successfully!")
            else:
                messagebox.showinfo("Info", "No faces were recognized.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            if 'cam' in locals() and cam.isOpened():
                cam.release()
            cv2.destroyAllWindows()

    def view_attendance_action(self, subject, parent_window):
        """
        Calculates and displays the attendance report for a subject.
        """
        if not subject:
            messagebox.showerror("Error", "Please enter a subject name.", parent=parent_window)
            return

        subject_path = os.path.join(self.attendance_path, subject)
        if not os.path.exists(subject_path):
            messagebox.showerror("Error", f"No attendance records found for {subject}.", parent=parent_window)
            return

        parent_window.destroy()

        try:
            all_files = glob(os.path.join(subject_path, f"{subject}*.csv"))
            if not all_files:
                messagebox.showinfo("Info", f"No attendance sheets found for {subject}.")
                return

            # Read all student details
            all_students_df = pd.read_csv(self.studentdetail_path)
            
            # Create a master dataframe with all dates as columns
            date_columns = sorted(list(set([os.path.basename(f).split('_')[1] for f in all_files])))
            master_df = all_students_df.copy()
            for date in date_columns:
                master_df[date] = 0 # Initialize with 'Absent'

            # Populate the master dataframe
            for file in all_files:
                date = os.path.basename(file).split('_')[1]
                attendance_df = pd.read_csv(file)
                for index, row in attendance_df.iterrows():
                    master_df.loc[master_df['Enrollment'] == row['Enrollment'], date] = 1 # Mark as 'Present'

            # Calculate total attendance percentage
            date_cols = master_df.columns[2:]
            if len(date_cols) > 0:
                master_df['Total_Classes'] = len(date_cols)
                master_df['Classes_Attended'] = master_df[date_cols].sum(axis=1)
                master_df['Attendance_%'] = round((master_df['Classes_Attended'] / master_df['Total_Classes']) * 100, 2)
            else:
                master_df['Attendance_%'] = 0

            self.display_report_window(subject, master_df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def display_report_window(self, subject, df):
        """
        Displays the attendance data in a new Toplevel window with a Treeview.
        """
        report_window = Toplevel(self.window)
        report_window.title(f"Attendance Report for {subject}")
        report_window.geometry("900x600")
        report_window.configure(bg="#f0f0f0")

        frame = ttk.Frame(report_window, padding=10)
        frame.pack(expand=True, fill="both")

        tree = ttk.Treeview(frame)
        tree.pack(expand=True, fill="both")

        # Define columns
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        # Define headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        # Add data to the treeview
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        hsb.pack(side='bottom', fill='x')
        tree.configure(xscrollcommand=hsb.set)


# --- Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()


# import tkinter as tk
# from tkinter import ttk, messagebox,Toplevel
# from PIL import Image, ImageTk
# import os
# import cv2
# import csv
# import numpy as np
# import pandas as pd
# import datetime
# import attendance_system

# class GradientFrame(tk.Canvas):
    
#     def __init__(self, parent, color1="#2C3E50", color2="#4CA1AF", **kwargs):
#         tk.Canvas.__init__(self, parent, **kwargs)
#         self._color1 = color1
#         self._color2 = color2
#         self.bind("<Configure>", self._draw_gradient)

#     def _draw_gradient(self, event=None):
        
#         self.delete("gradient")
#         width = self.winfo_width()
#         height = self.winfo_height()
#         limit = height
#         (r1, g1, b1) = self.winfo_rgb(self._color1)
#         (r2, g2, b2) = self.winfo_rgb(self._color2)
#         r_ratio = float(r2 - r1) / limit
#         g_ratio = float(g2 - g1) / limit
#         b_ratio = float(b2 - b1) / limit

#         for i in range(limit):
#             nr = int(r1 + (r_ratio * i))
#             ng = int(g1 + (g_ratio * i))
#             nb = int(b1 + (b_ratio * i))
#             color = f"#{nr:04x}{ng:04x}{nb:04x}"
#             self.create_line(0, i, width, i, tags=("gradient",), fill=color)
#         self.lower("gradient")

# # Main Application Class
# class PersonalIdentifierApp:
    
#     def __init__(self, window):
        
#         # Initializes the main application window and its components.
#         self.window = window
#         self.window.title("Face Recognition System")
#         self.window.geometry("1280x720")
#         self.window.state('zoomed')
        
#         # --- PATH CONFIGURATIONS ---
#         self.haarcasecade_path = "haarcascade_frontalface_default.xml"
#         self.trainimagelabel_path = "./TrainingData/trainer.yml"
#         self.trainimage_path = "TrainingData/Images"
#         self.persondetail_path = "./TrainingData/person_details.csv"
        
#         self.setup_directories_and_files()

#         # --- UI STYLING ---
#         self.style = ttk.Style(self.window)
#         self.style.theme_use("clam")
#         self.configure_styles()

#         # --- MAIN LAYOUT ---
#         self.create_main_widgets()

#     def setup_directories_and_files(self):
#         """Creates necessary directories and files for the application to function correctly."""
#         os.makedirs(self.trainimage_path, exist_ok=True)
#         os.makedirs(os.path.dirname(self.trainimagelabel_path), exist_ok=True)
        
#         if not os.path.exists(self.persondetail_path):
#             with open(self.persondetail_path, 'w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(['ID', 'Name', 'Age', 'Status'])
        
#         if not os.path.exists(self.haarcasecade_path):
#             self.download_haar_cascade()

#     def download_haar_cascade(self):
#         """Downloads the Haar Cascade XML file from OpenCV's repository if it's missing."""
#         url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
#         try:
#             import requests
#             print("Downloading required face detection model...")
#             response = requests.get(url)
#             response.raise_for_status()
#             with open(self.haarcasecade_path, 'wb') as f:
#                 f.write(response.content)
#             print("Download complete.")
#         except Exception as e:
#             messagebox.showerror("Download Error", f"Could not download model file.\nPlease ensure you have an internet connection.\nError: {e}")
#             self.window.quit()

#     def configure_styles(self):
#         """Configures the styles for various widgets for a modern and cohesive look."""
#         # Colors
#         self.primary_color = "#3498DB"
#         self.dark_color = "#2C3E50"
#         self.light_color = "#ECF0F1"
#         self.card_color = "#34495E"

#         self.style.configure("TFrame", background=self.dark_color) # Fallback
#         self.style.configure("Header.TLabel", font=("Segoe UI", 32, "bold"), foreground=self.light_color, background=self.dark_color)
#         self.style.configure("Subheader.TLabel", font=("Segoe UI", 14), foreground=self.light_color, background=self.dark_color)
#         self.style.configure("TButton", font=("Segoe UI", 12, "bold"), foreground="white", background=self.primary_color, padding=(15, 10), borderwidth=0)
#         self.style.map("TButton", background=[('active', '#2980B9')])
        
#         # Card styles
#         self.style.configure("Card.TFrame", background=self.card_color, relief="raised", borderwidth=2, bordercolor=self.primary_color)
#         self.style.configure("CardTitle.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.light_color, background=self.card_color)
#         self.style.configure("CardDesc.TLabel", font=("Segoe UI", 11), foreground=self.light_color, background=self.card_color)
        
#         # Recognition window styles
#         self.style.configure("InfoPanel.TFrame", background=self.card_color)
#         self.style.configure("ProfileHeader.TLabel", font=("Segoe UI", 20, "bold"), foreground=self.light_color, background=self.card_color)
#         self.style.configure("InfoBold.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.primary_color, background=self.card_color)
#         self.style.configure("Info.TLabel", font=("Segoe UI", 12), foreground=self.light_color, background=self.card_color)
#         self.style.configure("Black.TLabel", background="black")


#     def create_main_widgets(self):
#         """Creates and lays out the primary widgets on the main application window."""
#         # Use the GradientFrame as the main background
#         main_frame = GradientFrame(self.window, color1=self.dark_color, color2="#1A252F")
#         main_frame.pack(expand=True, fill="both")

#         header_frame = ttk.Frame(main_frame, style="TFrame")
#         header_frame.pack(pady=(50, 50))
        
#         # To make labels transparent on the gradient, they must be tk.Label, not ttk.Label
#         # Or their style must have a matching background. We will make their parent frame transparent.
#         header_frame.configure(style="TFrame")
        
#         title = ttk.Label(header_frame, text="Face Recognition System", style="Header.TLabel")
#         title.pack()
        
#         subtitle = ttk.Label(header_frame, text="Real-time face recognition and profile display", style="Subheader.TLabel")
#         subtitle.pack(pady=5)

#         cards_frame = ttk.Frame(main_frame, style="TFrame")
#         cards_frame.pack(expand=True)

#         actions = [
#             ("Register New Person", "Add a new person to the database with their details and facial data.", self.open_registration_window),
#             ("Start Recognition", "Launch the camera to identify registered individuals in real-time.", self.open_recognition_window)
#         ]

#         for i, (title, desc, command) in enumerate(actions):
#             card = ttk.Frame(cards_frame, style="Card.TFrame", padding=30)
#             card.grid(row=0, column=i, padx=30, pady=20, sticky="ns")
#             cards_frame.grid_columnconfigure(i, weight=1)

#             ttk.Label(card, text=title, style="CardTitle.TLabel").pack(pady=(0, 10))
#             ttk.Label(card, text=desc, wraplength=250, justify="center", style="CardDesc.TLabel").pack(pady=(0, 30), expand=True)
#             ttk.Button(card, text=f"Launch {title.split()[0]}", command=command, width=25).pack(pady=(10, 0))

#         footer = ttk.Label(main_frame, text=f"© {datetime.datetime.now().year} Face Recognition System. All rights reserved.", style="Subheader.TLabel", font=("Segoe UI", 9))
#         footer.pack(side="bottom", pady=10)

#     def open_toplevel_window(self, title, geometry="600x550"):
#         """Helper function to create a styled Toplevel window."""
#         top_window = Toplevel(self.window)
#         top_window.title(title)
#         top_window.geometry(geometry)
#         top_window.grab_set()

#         main_frame = GradientFrame(top_window, color1=self.dark_color, color2="#1A252F")
#         main_frame.pack(expand=True, fill="both")
        
#         ttk.Label(main_frame, text=title, style="Header.TLabel", font=("Segoe UI", 22, "bold")).pack(pady=(30, 20))
#         return main_frame

#     def open_registration_window(self):
#         """Opens a window for registering a new person with their details."""
#         reg_frame = self.open_toplevel_window("Register New Person")

#         form_frame = ttk.Frame(reg_frame, style="TFrame")
#         form_frame.pack(pady=10)

#         fields = {"ID": "A unique numeric ID", "Name": "Full Name", "Age": "Age", "Status": "e.g., Student, Employee"}
#         self.entries = {}
#         for i, (field, placeholder) in enumerate(fields.items()):
#             ttk.Label(form_frame, text=f"{field}:", style="Subheader.TLabel").grid(row=i, column=0, sticky="w", pady=8, padx=5)
#             entry = ttk.Entry(form_frame, font=("Segoe UI", 12), width=30)
#             entry.grid(row=i, column=1, pady=8, padx=5)
#             self.entries[field] = entry
        
#         notification_label = ttk.Label(reg_frame, text="", font=("Segoe UI", 10, "italic"), style="Subheader.TLabel")
#         notification_label.pack(pady=10)
        
#         def update_notification(msg, is_error=False):
#             notification_label.config(text=msg, foreground="red" if is_error else "#2ECC71")

#         buttons_frame = ttk.Frame(reg_frame, style="TFrame")
#         buttons_frame.pack(pady=20)

#         ttk.Button(buttons_frame, text="Capture Images", command=lambda: self.capture_images_action(update_notification)).pack(side="left", padx=10)
#         ttk.Button(buttons_frame, text="Train Model", command=lambda: self.train_model_action(update_notification)).pack(side="left", padx=10)

#     def capture_images_action(self, notification_callback):
#         """Validates input and initiates the face capture process."""
#         details = {field: entry.get() for field, entry in self.entries.items()}
#         if not details['ID'].isdigit() or not details['Name'] or not details['Age'].isdigit() or not details['Status']:
#             notification_callback("Please fill all fields correctly (ID and Age must be numbers).", is_error=True)
#             return

#         try:
#             if os.path.exists(self.persondetail_path) and os.path.getsize(self.persondetail_path) > 0:
#                 df = pd.read_csv(self.persondetail_path)
#                 if int(details['ID']) in df['ID'].values:
#                     notification_callback("This ID already exists. Please use a unique ID.", is_error=True)
#                     return
#         except Exception as e:
#             notification_callback(f"Error reading details file: {e}", is_error=True)
#             return

#         self.run_face_capture(details, notification_callback)
    
#     def run_face_capture(self, details, notification_callback):
#         """Handles the camera operations for capturing and saving face images."""
#         try:
#             cam = cv2.VideoCapture(0)
#             detector = cv2.CascadeClassifier(self.haarcasecade_path)
#             path = os.path.join(self.trainimage_path, f"{details['ID']}_{details['Name']}")
#             os.makedirs(path, exist_ok=True)
            
#             sample_num = 0
#             notification_callback("Look at the camera. Capturing 50 images...", is_error=False)
            
#             while True:
#                 ret, img = cam.read()
#                 if not ret: break
#                 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                 faces = detector.detectMultiScale(gray, 1.3, 5)
                
#                 for (x, y, w, h) in faces:
#                     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     sample_num += 1
#                     cv2.imwrite(f"{path}/{details['Name']}_{details['ID']}_{sample_num}.jpg", gray[y:y+h, x:x+w])
#                     cv2.putText(img, f"Images Captured: {sample_num}/50", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#                     cv2.imshow("Capturing Images...", img)
                
#                 if cv2.waitKey(100) & 0xFF == ord('q') or sample_num >= 50: break
            
#             cam.release()
#             cv2.destroyAllWindows()

#             with open(self.persondetail_path, "a", newline='') as csvFile:
#                 writer = csv.writer(csvFile)
#                 writer.writerow([details['ID'], details['Name'], details['Age'], details['Status']])
            
#             notification_callback(f"Images saved for {details['Name']}. Please train the model.", is_error=False)
#         except Exception as e:
#             notification_callback(f"An error occurred: {e}", is_error=True)
#             if 'cam' in locals() and cam.isOpened(): cam.release()
#             cv2.destroyAllWindows()

#     def train_model_action(self, notification_callback):
#         """Trains the face recognizer model with the collected images."""
#         notification_callback("Training model... This may take a moment.", is_error=False)
#         self.window.update_idletasks()
#         try:
#             recognizer = cv2.face.LBPHFaceRecognizer_create()
#             faces, ids = self.get_images_and_labels(self.trainimage_path)
            
#             if not faces:
#                 notification_callback("No images found to train. Please register a person first.", is_error=True)
#                 return

#             recognizer.train(faces, np.array(ids))
#             recognizer.save(self.trainimagelabel_path)
#             notification_callback("Model trained successfully!", is_error=False)
#         except Exception as e:
#             notification_callback(f"Error during training: {e}", is_error=True)

#     def get_images_and_labels(self, path):
#         """Reads image files and extracts face data and corresponding IDs for training."""
#         image_paths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
#         faces, ids = [], []

#         for dir_path in image_paths:
#             for file_name in os.listdir(dir_path):
#                 image_path = os.path.join(dir_path, file_name)
#                 try:
#                     pil_image = Image.open(image_path).convert("L")
#                     image_np = np.array(pil_image, "uint8")
#                     person_id = int(os.path.basename(dir_path).split("_")[0])
#                     faces.append(image_np)
#                     ids.append(person_id)
#                 except Exception:
#                     continue
#         return faces, ids

#     def open_recognition_window(self):
#         """Opens the main real-time face recognition window."""
#         if not os.path.exists(self.trainimagelabel_path):
#             messagebox.showerror("Error", "Model not trained. Please register a person and train the model first.")
#             return

#         rec_window = Toplevel(self.window)
#         rec_window.title("Live Recognition")
#         rec_window.geometry("1200x700")
#         rec_window.configure(bg=self.dark_color)

#         main_frame = ttk.Frame(rec_window, style="TFrame")
#         main_frame.pack(fill="both", expand=True, padx=20, pady=20)

#         video_label = ttk.Label(main_frame, style="Black.TLabel")
#         video_label.pack(side="left", fill="both", expand=True, padx=(0, 20))

#         info_panel = ttk.Frame(main_frame, style="InfoPanel.TFrame", width=350)
#         info_panel.pack(side="right", fill="y")
#         info_panel.pack_propagate(False)

#         ttk.Label(info_panel, text="Profile Details", style="ProfileHeader.TLabel").pack(pady=20)
        
#         profile_pic_label = ttk.Label(info_panel, style="InfoPanel.TFrame") # Match panel bg
#         profile_pic_label.pack(pady=10)
        
#         details_frame = ttk.Frame(info_panel, style="InfoPanel.TFrame")
#         details_frame.pack(pady=20, padx=20, fill="x")
        
#         info_labels = {}
#         for i, field in enumerate(["ID", "Name", "Age", "Status"]):
#             ttk.Label(details_frame, text=f"{field}:", style="InfoBold.TLabel").grid(row=i, column=0, sticky="w", pady=5)
#             value_label = ttk.Label(details_frame, text="---", style="Info.TLabel")
#             value_label.grid(row=i, column=1, sticky="w", padx=10)
#             info_labels[field] = value_label

#         recognizer = cv2.face.LBPHFaceRecognizer_create()
#         recognizer.read(self.trainimagelabel_path)
#         face_cascade = cv2.CascadeClassifier(self.haarcasecade_path)
#         df = pd.read_csv(self.persondetail_path)
        
#         cam = cv2.VideoCapture(0)

#         def update_frame():
#             ret, frame = cam.read()
#             if not ret:
#                 rec_window.after(10, update_frame)
#                 return

#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#             recognized_this_frame = False
#             for (x, y, w, h) in faces:
#                 person_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

#                 if confidence < 75:
#                     try:
#                         person_details = df[df['ID'] == person_id].iloc[0]
#                         display_text = f"{person_details['Name']} ({int(100 - confidence)}%)"
#                         color = (0, 255, 0)
                        
#                         if not recognized_this_frame:
#                             info_labels["ID"].config(text=person_details['ID'])
#                             info_labels["Name"].config(text=person_details['Name'])
#                             info_labels["Age"].config(text=person_details['Age'])
#                             info_labels["Status"].config(text=person_details['Status'])
                            
#                             profile_img_arr = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
#                             profile_img = Image.fromarray(profile_img_arr).resize((150, 150), Image.LANCZOS)
#                             profile_photo = ImageTk.PhotoImage(image=profile_img)
#                             profile_pic_label.config(image=profile_photo)
#                             profile_pic_label.image = profile_photo
#                             recognized_this_frame = True

#                     except IndexError:
#                         display_text = "Unknown ID"
#                         color = (0, 255, 255)
#                 else:
#                     display_text = "Unknown"
#                     color = (0, 0, 255)
                
#                 cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
#                 cv2.putText(frame, display_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

#             if not recognized_this_frame:
#                 for label in info_labels.values(): label.config(text="---")
#                 profile_pic_label.config(image='')

#             img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = Image.fromarray(img)
#             img_tk = ImageTk.PhotoImage(image=img)
#             video_label.imgtk = img_tk
#             video_label.configure(image=img_tk)
            
#             rec_window.after(10, update_frame)

#         def on_close():
#             cam.release()
#             rec_window.destroy()

#         rec_window.protocol("WM_DELETE_WINDOW", on_close)
#         update_frame()


# # --- Application Entry Point ---
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = PersonalIdentifierApp(root)
#     root.mainloop()
