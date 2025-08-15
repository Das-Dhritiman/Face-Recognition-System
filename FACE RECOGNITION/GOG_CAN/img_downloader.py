import os
import csv
import requests
import tkinter as tk
from tkinter import filedialog, messagebox

def download_images_from_csv():
    """
    Reads a CSV file containing image URLs, downloads them, and saves them
    into a structured folder required by the Face Recognition System.
    """
    # --- Configuration ---
    # These should match the details you registered in the main application.
    PERSON_ID = id_entry.get()
    PERSON_NAME = name_entry.get()
    CSV_FILE_PATH = csv_path_entry.get()

    # Basic validation
    if not PERSON_ID.isdigit() or not PERSON_NAME or not CSV_FILE_PATH:
        messagebox.showerror("Error", "Please fill all fields. ID must be a number.")
        return

    # The base path where the main application stores its training images.
    BASE_IMAGE_FOLDER = "TrainingData/Images"
    
    # Create the specific folder for the person (e.g., "TrainingData/Images/1_Jeff Bezos")
    target_folder = os.path.join(BASE_IMAGE_FOLDER, f"{PERSON_ID}_{PERSON_NAME}")
    
    try:
        os.makedirs(target_folder, exist_ok=True)
        print(f"Directory '{target_folder}' is ready.")
    except OSError as e:
        messagebox.showerror("Error", f"Could not create directory: {e}")
        return

    # --- Read CSV and Download ---
    try:
        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            image_count = 0
            
            print(f"\nStarting download for {PERSON_NAME} (ID: {PERSON_ID})...")
            
            for row in reader:
                image_url = row.get('image_url')
                if not image_url:
                    print(f"Skipping row with no 'image_url': {row}")
                    continue

                try:
                    # Send a request to download the image
                    response = requests.get(image_url, stream=True, timeout=10)
                    response.raise_for_status()  # Raise an exception for bad status codes

                    # Create a unique filename for each image
                    image_count += 1
                    file_extension = os.path.splitext(image_url)[1]
                    if not file_extension: # Default to .jpg if no extension found
                        file_extension = ".jpg"
                    
                    file_name = f"image_{image_count}{file_extension}"
                    file_path = os.path.join(target_folder, file_name)

                    # Save the image to the target folder
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"  ({image_count}) Successfully downloaded and saved: {file_name}")

                except requests.exceptions.RequestException as e:
                    print(f"  - Failed to download {image_url}. Error: {e}")
            
            if image_count > 0:
                messagebox.showinfo("Success", f"Download complete! {image_count} images were saved to:\n{target_folder}")
            else:
                messagebox.showwarning("Warning", "Process finished, but no images were downloaded. Check your CSV file and URLs.")

    except FileNotFoundError:
        messagebox.showerror("Error", f"The file '{CSV_FILE_PATH}' was not found.")
    except Exception as e:
        messagebox.showerror("An Unexpected Error Occurred", f"An error occurred: {e}")

# --- GUI Setup ---
def create_gui():
    """Creates a simple Tkinter GUI for the downloader script."""
    root = tk.Tk()
    root.title("Image Downloader for Face Recognition")
    root.geometry("500x250")

    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(frame, text="Person ID:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
    global id_entry
    id_entry = tk.Entry(frame, width=40)
    id_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Person Name:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
    global name_entry
    name_entry = tk.Entry(frame, width=40)
    name_entry.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="CSV File Path:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
    global csv_path_entry
    csv_path_entry = tk.Entry(frame, width=40)
    csv_path_entry.grid(row=2, column=1, pady=5)
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            csv_path_entry.delete(0, tk.END)
            csv_path_entry.insert(0, filename)

    browse_button = tk.Button(frame, text="Browse...", command=browse_file)
    browse_button.grid(row=2, column=2, padx=5)

    download_button = tk.Button(frame, text="Download Images", command=download_images_from_csv)
    download_button.grid(row=3, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    # Ensure you have the 'requests' library installed.
    # You can install it by running: pip install requests
    create_gui()
