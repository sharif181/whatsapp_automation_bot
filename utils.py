from tkinter import filedialog

import pandas as pd


def handle_csv_upload():
    global data
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[
            ("CSV and Excel files", "*.csv;*.xlsx"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx")
        ]
    )
    
    if file_path:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, dtype=str)
        elif file_path.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path, dtype=str)
        return df

# Function to handle attachment upload
def handle_attachment_upload():
    file_types = [
        ("All supported files", "*.pdf;*.csv;*.xlsx;*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.txt;*.doc;*.docx;*.ppt;*.pptx;"),
        ("PDF files", "*.pdf"),
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx"),
        ("JPEG files", "*.jpg;*.jpeg"),
        ("PNG files", "*.png"),
        ("GIF files", "*.gif"),
        ("BMP files", "*.bmp"),
        ("Text files", "*.txt"),
        ("Word documents", "*.doc;*.docx"),
        ("PowerPoint files", "*.ppt;*.pptx")
    ]
    
    file_paths = filedialog.askopenfilenames(title="Select files", filetypes=file_types)
    
    if file_paths:
        return file_paths