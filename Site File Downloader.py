import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from urllib.parse import urljoin, urlparse
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, StringVar, Listbox, MULTIPLE, END, messagebox
import threading

class SiteFileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Site File Downloader")

        Label(root, text="Enter URL:").grid(row=0, column=0)
        self.url_entry = Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(root, text="Select Download Folder:").grid(row=1, column=0)
        self.folder_path = Entry(root, width=50)
        self.folder_path.grid(row=1, column=1, padx=10, pady=10)
        Button(root, text="Browse", command=self.browse_folder).grid(row=1, column=2)

        # File formats
        Label(root, text="File Formats:").grid(row=2, column=0)
        self.format_listbox = Listbox(root, selectmode=MULTIPLE)
        self.format_listbox.grid(row=2, column=1, padx=10, pady=10)
        self.format_listbox.insert(END, ".mp3", ".jpg")

        self.custom_format_entry = Entry(root, width=10)
        self.custom_format_entry.grid(row=3, column=1, padx=5, pady=5)
        Button(root, text="Add Format", command=self.add_custom_format).grid(row=3, column=2)
        Button(root, text="Remove Selected", command=self.remove_selected_formats).grid(row=4, column=1, pady=5)

        Button(root, text="Download", command=self.start_download).grid(row=5, column=1, pady=10)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, pady=10)

        self.status_var = StringVar()
        self.status_label = Label(root, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=3)

        # Add signature
        Label(root, text="KrakenIT", font=("Arial", 12)).grid(row=8, column=0, columnspan=3, pady=10)

        # Error label
        self.error_var = StringVar()
        self.error_label = Label(root, textvariable=self.error_var, fg="red")
        self.error_label.grid(row=9, column=0, columnspan=3)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.delete(0, 'end')
        self.folder_path.insert(0, folder_selected)

    def add_custom_format(self):
        custom_format = self.custom_format_entry.get().strip().lower()
        if custom_format and not custom_format.startswith('.'):
            custom_format = '.' + custom_format
        if custom_format and custom_format not in self.format_listbox.get(0, END):
            self.format_listbox.insert(END, custom_format)
        self.custom_format_entry.delete(0, 'end')

    def remove_selected_formats(self):
        selected_indices = self.format_listbox.curselection()
        for index in reversed(selected_indices):
            self.format_listbox.delete(index)

    def start_download(self):
        self.error_var.set("")
        url = self.url_entry.get()
        download_folder = self.folder_path.get()

        if not url:
            self.error_var.set("URL cannot be empty")
            return
        if not download_folder:
            self.error_var.set("Download folder cannot be empty")
            return
        if self.format_listbox.size() == 0:
            self.error_var.set("No file formats selected")
            return

        threading.Thread(target=self.fetch_and_download_files, args=(url, download_folder)).start()

    def fetch_and_download_files(self, url, folder):
        try:
            self.status_var.set("Fetching file list...")
            self.root.update_idletasks()

            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            selected_formats = [self.format_listbox.get(i) for i in range(self.format_listbox.size())]

            files_to_download = []
            for fmt in selected_formats:
                files_to_download += [link['href'] for link in soup.find_all('a', href=True) if link['href'].endswith(fmt)]
                files_to_download += [img['src'] for img in soup.find_all('img', src=True) if img['src'].endswith(fmt)]

            total_files = len(files_to_download)
            if total_files == 0:
                self.error_var.set("No files found for the selected formats")
                self.status_var.set("")
                return

            self.progress['maximum'] = total_files
            self.progress['value'] = 0

            for i, file_path in enumerate(files_to_download, start=1):
                self.download_file(url, file_path, folder)
                self.progress['value'] = i
                self.status_var.set(f"Downloading {i}/{total_files} files...")
                self.root.update_idletasks()

            self.status_var.set("Download complete")
        except Exception as e:
            self.error_var.set(f"Error: {str(e)}")
            self.status_var.set("")

    def download_file(self, base_url, file_path, folder):
        try:
            file_url = file_path if bool(urlparse(file_path).netloc) else urljoin(base_url, file_path)
            file_name = os.path.basename(file_path)
            local_path = os.path.join(folder, file_name)
            urllib.request.urlretrieve(file_url, local_path)
            print(f"Downloaded: {local_path}")
        except Exception as e:
            raise Exception(f"Failed to download {file_path}: {e}")

if __name__ == "__main__":
    root = Tk()
    app = SiteFileDownloaderApp(root)
    root.mainloop()