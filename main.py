import csv
import os
import random
import string
import time
from tkinter import *
from tkinter import ttk

import pandas as pd
import pyautogui
import pygetwindow as gw
import pyperclip
from selenium.webdriver.common.keys import Keys

from crawler import Crawler
from utils import handle_attachment_upload, handle_csv_upload

# Global variables to store data
uploaded_file_paths = []
csv_data = None
message_text = ""
bot = None


def generate_random_name(length=5):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

def handle_attachment():
    global uploaded_file_paths
    uploaded_file_paths = handle_attachment_upload()
    if uploaded_file_paths:
        file_names = "\n".join([f.split("/")[-1] for f in uploaded_file_paths])
        uploaded_files_label.config(text=f"Uploaded files:\n{file_names}")
    check_button_state()

def upload_and_display_csv():
    global csv_data
    csv_data = handle_csv_upload()
    if csv_data is not None:
        display_dataframe(csv_data)
    check_button_state()

# Function to display the DataFrame in the Treeview
def display_dataframe(df):
    # Clear any existing data in the Treeview
    for widget in dataviewer.winfo_children():
        widget.destroy()

    # Create Treeview widget
    tree = ttk.Treeview(dataviewer)
    tree.grid(row=0, column=0, sticky='nsew')

    # Define columns
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    # Set up column headings
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    # Add data to the Treeview
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Enable vertical scrollbar
    vsb = ttk.Scrollbar(dataviewer, orient="vertical", command=tree.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    tree.configure(yscrollcommand=vsb.set)

    # Store a reference to the treeview for later use
    dataviewer.tree = tree

# Function to check if the table view and message box have data
def check_button_state():
    table_has_data = hasattr(dataviewer, 'tree') and len(dataviewer.tree.get_children()) > 0
    message_not_empty = message_input.get("1.0", "end-1c").strip() != ""
    if table_has_data and message_not_empty:
        action_button.config(state=NORMAL)
    else:
        action_button.config(state=DISABLED)

# Function to be called when the button is clicked
def on_action_button_click():
    global message_text
    message_text = message_input.get("1.0", "end-1c").strip()
    show_second_screen()

def show_second_screen():
    # Destroy all widgets from the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Create new content for the second screen
    second_screen_frame = Frame(root, bg="#f0f0f0")
    second_screen_frame.pack(fill="both", expand=True)

    Label(second_screen_frame, text="Welcome to the WhatsApp bot", font=("Arial", 24), bg="#f0f0f0").pack(pady=50)

    Button(second_screen_frame, text="Initialize the bot", bg="#007acc", fg="white", relief="flat", font=("Arial", 12), command=initialize_and_start).pack(pady=20)
    
    Button(second_screen_frame, text="Start sending messages", bg="#007acc", fg="white", relief="flat", font=("Arial", 12), command=start_sending_message).pack(pady=20)
    
    Button(second_screen_frame, text="Go Back", command=show_first_screen, bg="#007acc", fg="white", relief="flat", font=("Arial", 12)).pack(pady=20)


def display_dataframe_on_second_screen(df, frame):
    tree = ttk.Treeview(frame)
    tree.grid(row=0, column=0, sticky='nsew')

    # Define columns
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    # Set up column headings
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    # Add data to the Treeview
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Enable vertical scrollbar
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    tree.configure(yscrollcommand=vsb.set)

def initialize_and_start():
    global bot
    bot = Crawler("https://web.whatsapp.com/")
    bot.initialize_whatsapp()
    time.sleep(10)
    # Add your logic here to initialize the bot and start sending messages


def write_to_excel(file_path, row):
    fieldnames = ['name', 'number', 'status', 'comment']
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing Excel file into a DataFrame
        df = pd.read_excel(file_path, dtype=str)
    else:
        # Create a new DataFrame if the file does not exist
        df = pd.DataFrame(columns=fieldnames)
    
    # Create a new DataFrame with the row to be appended
    new_df = pd.DataFrame([row])
    
    # Append the new row to the existing DataFrame
    df = pd.concat([df, new_df], ignore_index=True)
    
    # Write the updated DataFrame back to the Excel file
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)


def send_message(XPATH, message_text):
    message_box = bot.crawler.find_element_by_xpath(XPATH)
    if message_box:
        message_box.click()
        # print(f"typing {message_text}")
        pyperclip.copy(message_text)
        pyautogui.hotkey('ctrl', 'v')
        message_box.send_keys(Keys.RETURN)
        time.sleep(2)


def start_sending_message():
    global csv_data
    global bot
    global message_text
    global uploaded_file_paths

    # Minimize the Tkinter window
    root.iconify()

    time.sleep(3)
    # Attempt to focus on the browser window
    try:
        browser_window = gw.getWindowsWithTitle("WhatsApp")[0]  # Assuming the title has "WhatsApp"
        if browser_window:
            browser_window.activate()
            browser_window.maximize()
    except Exception as e:
        print(f"Could not focus on the browser window: {e}")

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    csv_file_name = f"whatsapp_bot_status_{generate_random_name()}"
    csv_file_path = os.path.join(desktop_path, csv_file_name)
    csv_file_path = f"{csv_file_path}.xlsx"
    
    for index, row in csv_data.iterrows():
        if (index+1) % 10 == 0:
            time.sleep(3)
        
        name = row["name"]
        number = row["number"]
        
        try:
            XPATH = '//div[@aria-placeholder="Type a message"]'
            ATTACH_XPATH = '//div[@aria-label="Attach"]'
            NEW_CONT_XPATH = '//div[@aria-label="New chat"]'
            SER_PH_CONT_XPATH = "//p[contains(@class, 'selectable-text') and contains(@class, 'copyable-text')]"
            SEND_XPATH = '//div[@aria-label="Send"]'
            FILE_INPUT_XPATH = '//span[text()="Document"]'


            new_cont_btn = bot.crawler.find_element_by_xpath(NEW_CONT_XPATH)
            if new_cont_btn:
                new_cont_btn.click()
                time.sleep(3)
                bot.crawler.driver.switch_to.window(bot.crawler.driver.current_window_handle)
                try:
                    time.sleep(3)
                    ser_ph_cont_box = bot.crawler.find_element_by_xpath(SER_PH_CONT_XPATH)
                    if ser_ph_cont_box.is_enabled():
                        ser_ph_cont_box.click()
                        time.sleep(3)
                        pyperclip.copy(f"+88{number}")
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(3)
                        pyautogui.press("enter")
                        time.sleep(2)
                    else:
                        raise Exception("text box not found")
                except Exception as e:
                    bot.crawler.go_to_page(f'https://web.whatsapp.com/send?phone={number}', True, XPATH)
                    time.sleep(3)

            else:
                bot.crawler.go_to_page(f'https://web.whatsapp.com/send?phone={number}', True, XPATH)
                time.sleep(3)
            
            if uploaded_file_paths:
                attachment_box = bot.crawler.find_element_by_xpath(ATTACH_XPATH)
                attachment_box.click()
                time.sleep(2)
                file_input = bot.crawler.find_element_by_xpath(FILE_INPUT_XPATH)
                file_input.click()
                time.sleep(1)

                files_name = []
                for file_path in uploaded_file_paths:
                    file_path = file_path.replace("/", "\\")
                    file_path = f'"{file_path}"'
                    files_name.append(file_path)

                final_file_paths = " ".join(files_name)
                pyperclip.copy(final_file_paths)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(2)
                pyautogui.press('enter')
                send_btn = bot.crawler.find_element_by_xpath(SEND_XPATH)
                if send_btn:
                    if len(files_name) == 1:
                        time.sleep(1)
                        pyperclip.copy(message_text)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(1)
                        send_btn.click()
                        time.sleep(2)
                    else:
                        time.sleep(1)
                        send_btn.click()
                        time.sleep(3)
                        send_message(XPATH, message_text)
            else:
                time.sleep(2)
                send_message(XPATH, message_text)
            row = {
                "name": name,
                "number": str(number),
                "status": "Success",
                "comment": ""
            }
            write_to_excel(csv_file_path, row)
    
        except Exception as e:
            row = {
                "name": name,
                "number": str(number),
                "status": "Failed",
                "comment": f"{e}"
            }
            write_to_excel(csv_file_path, row)


def show_first_screen():
    # Destroy all widgets from the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Recreate the first screen
    create_first_screen()

def create_first_screen():
    # left box
    left_frame = Frame(root, width=400, height=500, bg="#ffffff", relief=SOLID, bd=1)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Create frame within left_frame
    global dataviewer
    dataviewer = Frame(left_frame, width=400, height=480, bg="#ffffff")
    dataviewer.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
    dataviewer.grid_rowconfigure(0, weight=1)
    dataviewer.grid_columnconfigure(0, weight=1)

    # Create label above the dataviewer
    Button(left_frame, text="+ Upload CSV", command=upload_and_display_csv, bg="#007acc", fg="white", relief="flat").grid(row=1, column=0, padx=5, pady=10)

    # middle box
    middle_frame = Frame(root, width=400, height=400, bg="#ffffff", relief=SOLID, bd=1)
    middle_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Add message input box
    global message_input
    message_label = Label(middle_frame, text="Enter your message:", bg="#ffffff", font=("Arial", 12))
    message_label.pack(pady=5)

    message_input = Text(middle_frame, height=15, width=50, font=("Arial", 10), wrap=WORD, bd=1, relief=SOLID)
    message_input.pack(pady=5, padx=10)

    # Trigger button state check when message input changes
    message_input.bind("<KeyRelease>", lambda event: check_button_state())

    # right box
    right_frame = Frame(root, width=400, height=400, bg="#ffffff", relief=SOLID, bd=1)
    right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Add attachment upload button
    global uploaded_files_label
    attachment_button = Button(right_frame, text="Upload Attachments", command=handle_attachment, bg="#007acc", fg="white", relief="flat")
    attachment_button.pack(pady=10)

    # Label to display uploaded file names
    uploaded_files_label = Label(right_frame, text="", justify=LEFT, bg="#ffffff", font=("Arial", 10))
    uploaded_files_label.pack(pady=10)

    # bottom box
    button_frame = Frame(root, bg="#f0f0f0")
    button_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

    global action_button
    # Add action button to the bottom box, initially disabled
    action_button = Button(button_frame, text="Start Sending Message", state=DISABLED, command=on_action_button_click, bg="#007acc", fg="white", relief="flat", font=("Arial", 12))
    action_button.pack(pady=20)

    # Allow the frames to resize properly
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

root = Tk()
root.title("WhatsApp bot")
root.config(bg="#f0f0f0")  # Light gray background for a modern look

# Apply a consistent style
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))

# Start with the first screen
create_first_screen()

root.mainloop()
