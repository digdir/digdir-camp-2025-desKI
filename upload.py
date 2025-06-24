import tkinter as tk
from tkinter import filedialog
import PyPDF2
import json

# Function to convert PDF to text and append to vault.txt
def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        with open("vault.txt", "a", encoding="utf-8") as vault_file:
            vault_file.write(text + "\n")
        print(f" Innhold fra PDF lagt til vault.txt uten endringer.")

# Function to upload a text file and append to vault.txt
def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
        with open("vault.txt", "a", encoding="utf-8") as vault_file:
            vault_file.write(text + "\n")
        print(f" Innhold fra tekstfil lagt til vault.txt uten endringer.")

# Function to upload a JSON file and append to vault.txt
def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
        text = json.dumps(data, ensure_ascii=False, indent=2)  # formater som lesbar tekst
        with open("vault.txt", "a", encoding="utf-8") as vault_file:
            vault_file.write(text + "\n")
        print(f" Innhold fra JSON-fil lagt til vault.txt uten endringer.")

# Create the main window
root = tk.Tk()
root.title("Upload .pdf, .txt, or .json")

# Create a button to open the file dialog for PDF
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Create a button to open the file dialog for text file
txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
txt_button.pack(pady=10)

# Create a button to open the file dialog for JSON file
json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile)
json_button.pack(pady=10)

# Run the main event loop
root.mainloop()