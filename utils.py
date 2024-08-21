from tkinter import filedialog

import pandas as pd


def handle_csv_upload():
    global data
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path, dtype=str)
        return df

# Function to handle attachment upload
def handle_attachment_upload():
    file_types = [("PDF files", "*.pdf"), ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")]
    file_paths = filedialog.askopenfilenames(title="Select files", filetypes=file_types)
    if file_paths:
        return file_paths 