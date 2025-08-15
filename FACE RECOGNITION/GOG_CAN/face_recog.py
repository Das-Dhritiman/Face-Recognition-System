import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from PIL import Image, ImageTk
import os
import cv2
import csv
import numpy as np
import pandas as pd
import datetime
import attendance_system # <-- IMPORT THE NEW MODULE

# --- Custom Gradient Frame ---
class GradientFrame(tk.Canvas):
    """A canvas that draws a gradient background."""
    def __init__(self, parent, color1="#2C3E50", color2="#4CA1AF", **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        """Draw the gradient."""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr:04x}{ng:04x}{nb:04x}"
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

# --- Main Application Class ---
class PersonalIdentifierApp:
    """
    A Personal Face Recognition and Identification System built with Tkinter.
    This application allows registering individuals with their details (ID, Name, Age, Status)
    and then identifying them in real-time via a camera feed.
    """
    def __init__(self, window):
        """
        Initializes the main application window and its components.
        """
        self.window = window
        self.window.title("Face Recognition and Attendance System")
        self.window.geometry("1280x720")
        self.window.state('zoomed')
        
        # --- PATH CONFIGURATIONS ---
        self.haarcasecade_path = "haarcascade_frontalface_default.xml"
        self.trainimagelabel_path = "./TrainingData/trainer.yml"
        self.trainimage_path = "TrainingData/Images"
        self.persondetail_path = "./TrainingData/person_details.csv"
        self.attendance_path = "./TrainingData/attendance.csv"
        
        self.setup_directories_and_files()

        # --- UI STYLING ---
        self.style = ttk.Style(self.window)
        self.style.theme_use("clam")
        self.configure_styles()

        # --- MAIN LAYOUT ---
        self.create_main_widgets()

    def setup_directories_and_files(self):
        """Creates necessary directories and files for the application to function correctly."""
        os.makedirs(self.trainimage_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.trainimagelabel_path), exist_ok=True)
        
        if not os.path.exists(self.persondetail_path):
            with open(self.persondetail_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Age', 'Status'])

        # This check is now less relevant as we use a database, but good for legacy/fallback.
        if not os.path.exists(self.attendance_path):
            with open(self.attendance_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Date', 'Time', 'Latitude', 'Longitude'])
        
        if not os.path.exists(self.haarcasecade_path):
            self.download_haar_cascade()

    def download_haar_cascade(self):
        """Downloads the Haar Cascade XML file from OpenCV's repository if it's missing."""
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        try:
            import requests
            print("Downloading required face detection model...")
            response = requests.get(url)
            response.raise_for_status()
            with open(self.haarcasecade_path, 'wb') as f:
                f.write(response.content)
            print("Download complete.")
        except Exception as e:
            messagebox.showerror("Download Error", f"Could not download model file.\nPlease ensure you have an internet connection.\nError: {e}")
            self.window.quit()

    def configure_styles(self):
        """Configures the styles for various widgets for a modern and cohesive look."""
        # Colors
        self.primary_color = "#3498DB"
        self.dark_color = "#2C3E50"
        self.light_color = "#ECF0F1"
        self.card_color = "#34495E"

        self.style.configure("TFrame", background=self.dark_color) # Fallback
        self.style.configure("Header.TLabel", font=("Segoe UI", 32, "bold"), foreground=self.light_color, background=self.dark_color)
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 14), foreground=self.light_color, background=self.dark_color)
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), foreground="white", background=self.primary_color, padding=(15, 10), borderwidth=0)
        self.style.map("TButton", background=[('active', '#2980B9')])
        
        # Card styles
        self.style.configure("Card.TFrame", background=self.card_color, relief="raised", borderwidth=2, bordercolor=self.primary_color)
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.light_color, background=self.card_color)
        self.style.configure("CardDesc.TLabel", font=("Segoe UI", 11), foreground=self.light_color, background=self.card_color)
        
        # Recognition window styles
        self.style.configure("InfoPanel.TFrame", background=self.card_color)
        self.style.configure("ProfileHeader.TLabel", font=("Segoe UI", 20, "bold"), foreground=self.light_color, background=self.card_color)
        self.style.configure("InfoBold.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.primary_color, background=self.card_color)
        self.style.configure("Info.TLabel", font=("Segoe UI", 12), foreground=self.light_color, background=self.card_color)
        self.style.configure("Black.TLabel", background="black")


    def create_main_widgets(self):
        """Creates and lays out the primary widgets on the main application window."""
        # Use the GradientFrame as the main background
        main_frame = GradientFrame(self.window, color1=self.dark_color, color2="#1A252F")
        main_frame.pack(expand=True, fill="both")

        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(pady=(50, 50))
        
        header_frame.configure(style="TFrame")
        
        title = ttk.Label(header_frame, text="Face Recognition & Attendance", style="Header.TLabel")
        title.pack()
        
        subtitle = ttk.Label(header_frame, text="Real-time face recognition and attendance marking", style="Subheader.TLabel")
        subtitle.pack(pady=5)

        cards_frame = ttk.Frame(main_frame, style="TFrame")
        cards_frame.pack(expand=True)

        actions = [
            ("Register New Person", "Add a new person to the database with their details and facial data.", self.open_registration_window),
            ("Start Recognition", "Launch the camera to identify registered individuals and mark attendance.", self.open_recognition_window)
        ]

        for i, (title, desc, command) in enumerate(actions):
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=30)
            card.grid(row=0, column=i, padx=30, pady=20, sticky="ns")
            cards_frame.grid_columnconfigure(i, weight=1)

            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(pady=(0, 10))
            ttk.Label(card, text=desc, wraplength=250, justify="center", style="CardDesc.TLabel").pack(pady=(0, 30), expand=True)
            ttk.Button(card, text=f"Launch {title.split()[0]}", command=command, width=25).pack(pady=(10, 0))

        footer = ttk.Label(main_frame, text=f"© {datetime.datetime.now().year} Face Recognition System. All rights reserved.", style="Subheader.TLabel", font=("Segoe UI", 9))
        footer.pack(side="bottom", pady=10)

    def open_toplevel_window(self, title, geometry="600x550"):
        """Helper function to create a styled Toplevel window."""
        top_window = Toplevel(self.window)
        top_window.title(title)
        top_window.geometry(geometry)
        top_window.grab_set()

        main_frame = GradientFrame(top_window, color1=self.dark_color, color2="#1A252F")
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text=title, style="Header.TLabel", font=("Segoe UI", 22, "bold")).pack(pady=(30, 20))
        return main_frame

    def open_registration_window(self):
        """Opens a window for registering a new person with their details."""
        reg_frame = self.open_toplevel_window("Register New Person")

        form_frame = ttk.Frame(reg_frame, style="TFrame")
        form_frame.pack(pady=10)

        fields = {"ID": "A unique numeric ID", "Name": "Full Name", "Age": "Age", "Status": "e.g., Student, Employee"}
        self.entries = {}
        for i, (field, placeholder) in enumerate(fields.items()):
            ttk.Label(form_frame, text=f"{field}:", style="Subheader.TLabel").grid(row=i, column=0, sticky="w", pady=8, padx=5)
            entry = ttk.Entry(form_frame, font=("Segoe UI", 12), width=30)
            entry.grid(row=i, column=1, pady=8, padx=5)
            self.entries[field] = entry
        
        notification_label = ttk.Label(reg_frame, text="", font=("Segoe UI", 10, "italic"), style="Subheader.TLabel")
        notification_label.pack(pady=10)
        
        def update_notification(msg, is_error=False):
            notification_label.config(text=msg, foreground="red" if is_error else "#2ECC71")

        buttons_frame = ttk.Frame(reg_frame, style="TFrame")
        buttons_frame.pack(pady=20)

        ttk.Button(buttons_frame, text="Capture Images", command=lambda: self.capture_images_action(update_notification)).pack(side="left", padx=10)
        ttk.Button(buttons_frame, text="Train Model", command=lambda: self.train_model_action(update_notification)).pack(side="left", padx=10)

    def capture_images_action(self, notification_callback):
        #face captuirng initiation
        details = {field: entry.get() for field, entry in self.entries.items()}
        if not details['ID'].isdigit() or not details['Name'] or not details['Age'].isdigit() or not details['Status']:
            notification_callback("Please fill all fields correctly (ID and Age must be numbers).", is_error=True)
            return

        try:
            if os.path.exists(self.persondetail_path) and os.path.getsize(self.persondetail_path) > 0:
                df = pd.read_csv(self.persondetail_path)
                if int(details['ID']) in df['ID'].values:
                    notification_callback("This ID already exists. Please use a unique ID.", is_error=True)
                    return
        except Exception as e:
            notification_callback(f"Error reading details file: {e}", is_error=True)
            return

        self.run_face_capture(details, notification_callback)
    
    def run_face_capture(self, details, notification_callback):
        # face capute r image save korar jonno
        try:
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier(self.haarcasecade_path)
            path = os.path.join(self.trainimage_path, f"{details['ID']}_{details['Name']}")
            os.makedirs(path, exist_ok=True)
            
            sample_num = 0
            notification_callback("Look at the camera. Capturing 50 images...", is_error=False)
            
            while True:
                ret, img = cam.read()
                if not ret: break
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    sample_num += 1
                    cv2.imwrite(f"{path}/{details['Name']}_{details['ID']}_{sample_num}.jpg", gray[y:y+h, x:x+w])
                    cv2.putText(img, f"Images Captured: {sample_num}/50", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Capturing Images...", img)
                
                if cv2.waitKey(100) & 0xFF == ord('q') or sample_num >= 50: break
            
            cam.release()
            cv2.destroyAllWindows()

            with open(self.persondetail_path, "a", newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([details['ID'], details['Name'], details['Age'], details['Status']])
            
            notification_callback(f"Images saved for {details['Name']}. Please train the model.", is_error=False)
        except Exception as e:
            notification_callback(f"An error occurred: {e}", is_error=True)
            if 'cam' in locals() and cam.isOpened(): cam.release()
            cv2.destroyAllWindows()

    def train_model_action(self, notification_callback):
        """Trains the face recognizer model with the collected images."""
        notification_callback("Training model... This may take a moment.", is_error=False)
        self.window.update_idletasks()
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            faces, ids = self.get_images_and_labels(self.trainimage_path)
            
            if not faces:
                notification_callback("No images found to train. Please register a person first.", is_error=True)
                return

            recognizer.train(faces, np.array(ids))
            recognizer.save(self.trainimagelabel_path)
            notification_callback("Model trained successfully!", is_error=False)
        except Exception as e:
            notification_callback(f"Error during training: {e}", is_error=True)

    def get_images_and_labels(self, path):
        """Reads image files and extracts face data and corresponding IDs for training."""
        image_paths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        faces, ids = [], []

        for dir_path in image_paths:
            for file_name in os.listdir(dir_path):
                image_path = os.path.join(dir_path, file_name)
                try:
                    pil_image = Image.open(image_path).convert("L")
                    image_np = np.array(pil_image, "uint8")
                    person_id = int(os.path.basename(dir_path).split("_")[0])
                    faces.append(image_np)
                    ids.append(person_id)
                except Exception:
                    continue
        return faces, ids

    def open_recognition_window(self):
        """Opens the main real-time face recognition window."""
        if not os.path.exists(self.trainimagelabel_path):
            messagebox.showerror("Error", "Model not trained. Please register a person and train the model first.")
            return

        rec_window = Toplevel(self.window)
        rec_window.title("Live Recognition")
        rec_window.geometry("1200x700")
        rec_window.configure(bg=self.dark_color)

        main_frame = ttk.Frame(rec_window, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        video_label = ttk.Label(main_frame, style="Black.TLabel")
        video_label.pack(side="left", fill="both", expand=True, padx=(0, 20))

        info_panel = ttk.Frame(main_frame, style="InfoPanel.TFrame", width=350)
        info_panel.pack(side="right", fill="y")
        info_panel.pack_propagate(False)

        ttk.Label(info_panel, text="Profile Details", style="ProfileHeader.TLabel").pack(pady=20)
        
        profile_pic_label = ttk.Label(info_panel, style="InfoPanel.TFrame") # Match panel bg
        profile_pic_label.pack(pady=10)
        
        details_frame = ttk.Frame(info_panel, style="InfoPanel.TFrame")
        details_frame.pack(pady=20, padx=20, fill="x")
        
        info_labels = {}
        for i, field in enumerate(["ID", "Name", "Age", "Status"]):
            ttk.Label(details_frame, text=f"{field}:", style="InfoBold.TLabel").grid(row=i, column=0, sticky="w", pady=5)
            value_label = ttk.Label(details_frame, text="---", style="Info.TLabel")
            value_label.grid(row=i, column=1, sticky="w", padx=10)
            info_labels[field] = value_label
            
        attendance_button = ttk.Button(info_panel, text="Mark Attendance", state="disabled")
        attendance_button.pack(pady=20)

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(self.trainimagelabel_path)
        face_cascade = cv2.CascadeClassifier(self.haarcasecade_path)
        df = pd.read_csv(self.persondetail_path)
        
        cam = cv2.VideoCapture(0)

        def update_frame():
            ret, frame = cam.read()
            if not ret:
                rec_window.after(10, update_frame)
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            recognized_this_frame = False
            for (x, y, w, h) in faces:
                person_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

                if confidence < 75:
                    try:
                        person_details = df[df['ID'] == person_id].iloc[0]
                        display_text = f"{person_details['Name']} ({int(100 - confidence)}%)"
                        color = (0, 255, 0)
                        
                        if not recognized_this_frame:
                            info_labels["ID"].config(text=person_details['ID'])
                            info_labels["Name"].config(text=person_details['Name'])
                            info_labels["Age"].config(text=person_details['Age'])
                            info_labels["Status"].config(text=person_details['Status'])
                            
                            profile_img_arr = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
                            profile_img = Image.fromarray(profile_img_arr).resize((150, 150), Image.LANCZOS)
                            profile_photo = ImageTk.PhotoImage(image=profile_img)
                            profile_pic_label.config(image=profile_photo)
                            profile_pic_label.image = profile_photo
                            recognized_this_frame = True
                            
                            # --- FIXED LINE ---
                            # Convert the numpy.int64 to a standard Python int before passing it.
                            attendance_button.config(state="normal", command=lambda: attendance_system.mark_attendance(int(person_details['ID']), person_details['Name']))


                    except IndexError:
                        display_text = "Unknown ID"
                        color = (0, 255, 255)
                        attendance_button.config(state="disabled")
                else:
                    display_text = "Unknown"
                    color = (0, 0, 255)
                    attendance_button.config(state="disabled")
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, display_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

            if not recognized_this_frame:
                for label in info_labels.values(): label.config(text="---")
                profile_pic_label.config(image='')
                attendance_button.config(state="disabled")


            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = img_tk
            video_label.configure(image=img_tk)
            
            rec_window.after(10, update_frame)

        def on_close():
            cam.release()
            rec_window.destroy()

        rec_window.protocol("WM_DELETE_WINDOW", on_close)
        update_frame()


if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalIdentifierApp(root)
    root.mainloop()
