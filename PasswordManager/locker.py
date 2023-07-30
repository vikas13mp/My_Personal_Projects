import tkinter as tk
from hashlib import sha256
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import os

# GUI
root = tk.Tk()
root.title("App Login")

# Set the window size
root.geometry("800x600")

# Load and display the background image
bg_image = Image.open("1.jpg")  
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


label = tk.Label(root, text="Enter Password", font=("Helvetica", 24, "bold"))
label.pack(pady=100)

user_database = {
    "user1": None,  
    "user2": None,  
}

# File to store the password set status and hashed password
password_status_file = "password_status.txt"
password_hash_file = "password_hash.txt"

def encrypt_password(password):
    return sha256(password.encode()).hexdigest()

def set_password(username, password):
    user_database[username] = encrypt_password(password)

def change_password(username, old_password, new_password):
    encrypted_old_password = encrypt_password(old_password)
    if user_database.get(username) == encrypted_old_password:
        user_database[username] = encrypt_password(new_password)
        return True
    return False

def login(username, password):
    encrypted_password = encrypt_password(password)
    return user_database.get(username) == encrypted_password

def save_password_status_to_file(status):
    with open(password_status_file, "w") as file:
        file.write(str(status))

def read_password_status_from_file():
    if os.path.exists(password_status_file):
        with open(password_status_file, "r") as file:
            return bool(file.read().strip())
    return False

def save_password_hash_to_file(password_hash):
    with open(password_hash_file, "w") as file:
        file.write(password_hash)

def read_password_hash_from_file():
    if os.path.exists(password_hash_file):
        with open(password_hash_file, "r") as file:
            return file.read().strip()
    return None


stored_hash = read_password_hash_from_file()
if stored_hash is not None:
    user_database["user1"] = stored_hash

def show_message(message):
    info_label.config(text=message)

def on_login_click():
    password = entry_password.get()

    if login("user1", password): 
        show_message("Login successful!")
        # Add code to open the main application window here
    else:
        show_message("Invalid password")

def on_change_password_click():
    def confirm_change_password():
        old_password = entry_old_password.get()
        new_password = entry_new_password.get()

        if change_password("user1", old_password, new_password):
            show_message("Password changed successfully!")
            change_password_window.destroy()
        else:
            show_message("Invalid password")

    change_password_window = tk.Toplevel(root)
    change_password_window.title("Change Password")

    label_old_password = tk.Label(change_password_window, text="Old Password:")
    label_old_password.pack()
    entry_old_password = tk.Entry(change_password_window, show="*")
    entry_old_password.pack()

    label_new_password = tk.Label(change_password_window, text="New Password:")
    label_new_password.pack()
    entry_new_password = tk.Entry(change_password_window, show="*")
    entry_new_password.pack()

    button_change_password = tk.Button(change_password_window, text="Change Password", command=confirm_change_password, padx=10, pady=5)
    button_change_password.pack()

def on_set_password_click():
    if not read_password_status_from_file():
        def confirm_set_password():
            new_password = entry_new_password.get()

            set_password("user1", new_password)
            show_message("Password set successfully!")
            save_password_status_to_file(True)  

            
            hashed_password = encrypt_password(new_password)
            save_password_hash_to_file(hashed_password)
            user_database["user1"] = hashed_password

            button_set_password.config(state=tk.DISABLED)  
            set_password_window.destroy()

        set_password_window = tk.Toplevel(root)
        set_password_window.title("Set Password")

        label_new_password = tk.Label(set_password_window, text="New Password:")
        label_new_password.pack()
        entry_new_password = tk.Entry(set_password_window, show="*")
        entry_new_password.pack()

        button_set_password = tk.Button(set_password_window, text="Set Password", command=confirm_set_password, padx=10, pady=5)
        button_set_password.pack()
    else:
        show_message("Password already set!")



label_password = tk.Label(root, text="Enter Password:")
label_password.pack()

entry_password = tk.Entry(root, show="*")
entry_password.pack()

button_login = tk.Button(root, text="Login", command=on_login_click, padx=15, pady=7)
button_login.pack()

button_change_password = tk.Button(root, text="Change Password", command=on_change_password_click, padx=15, pady=7)
button_change_password.pack()

button_set_password = tk.Button(root, text="Set Password", command=on_set_password_click, padx=15, pady=7)
button_set_password.pack()

info_label = tk.Label(root, text="", fg="blue",padx=15, pady=7)
info_label.pack()


if read_password_status_from_file():
    button_set_password.config(state=tk.DISABLED)

root.mainloop()