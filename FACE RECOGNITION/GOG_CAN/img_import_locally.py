import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def import_local_images():
    """
    Copies images from a user-selected local folder into the structured
    directory required by the Face Recognition System.
    """
    # --- Get User Input ---
    person_id = id_entry.get()
    person_name = name_entry.get()
    source_folder = folder_path_entry.get()

    # --- Input Validation ---
    if not person_id.isdigit() or not person_name or not source_folder:
        messagebox.showerror("Error", "Please fill all fields. ID must be a number and a source folder must be selected.")
        return

    if not os.path.isdir(source_folder):
        messagebox.showerror("Error", "The selected source path is not a valid folder.")
        return

    # --- Define Paths and Create Folders ---
    base_image_folder = "TrainingData/Images"
    target_folder = os.path.join(base_image_folder, f"{person_id}_{person_name}")
    
    try:
        os.makedirs(target_folder, exist_ok=True)
        print(f"Directory '{target_folder}' is ready.")
    except OSError as e:
        messagebox.showerror("Error", f"Could not create directory: {e}")
        return

    # --- Copy Image Files ---
    supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    image_count = 0
    
    print(f"\nStarting import for {person_name} (ID: {person_id})...")
    
    for filename in os.listdir(source_folder):
        # Check if the file is an image
        if filename.lower().endswith(supported_extensions):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(target_folder, filename)
            
            try:
                # Copy the file
                shutil.copy2(source_path, destination_path)
                image_count += 1
                print(f"  ({image_count}) Successfully copied: {filename}")
            except Exception as e:
                print(f"  - Failed to copy {filename}. Error: {e}")

    # --- Final Feedback ---
    if image_count > 0:
        messagebox.showinfo("Success", f"Import complete! {image_count} images were copied to:\n{target_folder}")
    else:
        messagebox.showwarning("Warning", "Process finished, but no supported image files were found in the selected folder.")

# --- GUI Setup ---
def create_gui():
    """Creates a simple Tkinter GUI for the local image importer."""
    root = tk.Tk()
    root.title("Local Image Importer")
    root.geometry("500x250")

    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack(expand=True, fill=tk.BOTH)

    # --- Widgets ---
    tk.Label(frame, text="Person ID:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
    global id_entry
    id_entry = tk.Entry(frame, width=40)
    id_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Person Name:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
    global name_entry
    name_entry = tk.Entry(frame, width=40)
    name_entry.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Image Folder:", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
    global folder_path_entry
    folder_path_entry = tk.Entry(frame, width=40)
    folder_path_entry.grid(row=2, column=1, pady=5)
    
    def browse_folder():
        # Ask the user to select a directory
        directory = filedialog.askdirectory(title="Select the folder containing images")
        if directory:
            folder_path_entry.delete(0, tk.END)
            folder_path_entry.insert(0, directory)

    # Use ttk for a more modern button look if available
    try:
        browse_button = ttk.Button(frame, text="Browse...", command=browse_folder)
        import_button = ttk.Button(frame, text="Import Images", command=import_local_images)
    except NameError: # Fallback for environments without ttk
        browse_button = tk.Button(frame, text="Browse...", command=browse_folder)
        import_button = tk.Button(frame, text="Import Images", command=import_local_images)

    browse_button.grid(row=2, column=2, padx=5)
    import_button.grid(row=3, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
