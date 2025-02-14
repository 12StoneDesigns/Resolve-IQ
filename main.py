import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import DBConnect
from listComp import ListComp
import sqlite3
import sys
import traceback
import json
from pathlib import Path
from datetime import datetime
import os

class ComplaintManager:
    def __init__(self):
        try:
            self.setup_error_handling()
            self.load_settings()
            self.initialize_database()
            self.setup_window()
            self.create_styles()
            self.create_widgets()
            self.setup_layout()
            self.setup_shortcuts()
        except Exception as e:
            self.handle_fatal_error("Application Initialization Error", e)

    def handle_fatal_error(self, title, error):
        """Handle fatal errors that require application shutdown"""
        error_message = f"{title}:\n\n{str(error)}\n\nTraceback:\n{traceback.format_exc()}"
        messagebox.showerror("Fatal Error", error_message)
        if hasattr(self, 'root'):
            self.root.quit()
        sys.exit(1)

    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        error_message = f"An unexpected error occurred:\n\n{exc_type.__name__}: {str(exc_value)}\n\n"
        error_message += "".join(traceback.format_tb(exc_traceback))
        messagebox.showerror("Uncaught Exception", error_message)
        if hasattr(self, 'root'):
            self.root.quit()
        sys.exit(1)

    def handle_callback_error(self, exc, val, tb):
        """Handle Tkinter callback errors"""
        error_message = f"A callback error occurred:\n\n{exc.__name__}: {str(val)}\n\n"
        error_message += "".join(traceback.format_tb(tb))
        messagebox.showerror("Callback Error", error_message)

    def setup_error_handling(self):
        """Setup global error handling"""
        sys.excepthook = self.handle_uncaught_exception

    def load_settings(self):
        """Load application settings"""
        try:
            settings_path = Path('data/settings.json')
            if settings_path.exists():
                with open(settings_path) as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    'theme': 'light',
                    'window_size': '700x400',
                    'shortcuts_enabled': True
                }
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                with open(settings_path, 'w') as f:
                    json.dump(self.settings, f)
        except Exception as e:
            self.settings = {
                'theme': 'light',
                'window_size': '700x400',
                'shortcuts_enabled': True
            }

    def initialize_database(self):
        """Initialize database connection"""
        self.conn = DBConnect()

    def save_settings(self):
        """Save application settings"""
        try:
            with open('data/settings.json', 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to save settings: {str(e)}")

    def setup_window(self):
        """Initialize the main window with error handling"""
        try:
            self.root = tk.Tk()
            self.root.geometry(self.settings['window_size'])
            self.root.title('12Stone Designs - Complaint Management System')
            self.root.configure(bg='#f0f0f0')
            self.root.resizable(True, True)
            
            # Setup window error handling
            self.root.report_callback_exception = self.handle_callback_error
            
            # Bind window resize event
            self.root.bind('<Configure>', self.on_window_resize)
        except Exception as e:
            raise Exception(f"Window initialization failed: {str(e)}")

    def create_styles(self):
        """Create custom styles with error handling"""
        try:
            self.style = ttk.Style()
            self.apply_theme(self.settings['theme'])
        except Exception as e:
            raise Exception(f"Style creation failed: {str(e)}")

    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        if theme_name == 'dark':
            self.style.configure('Custom.TLabel',
                               background='#2d2d2d',
                               foreground='#ffffff',
                               font=('Helvetica', 11))
            self.style.configure('Custom.TButton',
                               background='#4a90e2',
                               foreground='#ffffff',
                               font=('Helvetica', 10, 'bold'))
            self.root.configure(bg='#2d2d2d')
        else:
            self.style.configure('Custom.TLabel',
                               background='#f0f0f0',
                               foreground='#000000',
                               font=('Helvetica', 11))
            self.style.configure('Custom.TButton',
                               background='#4a90e2',
                               foreground='#000000',
                               font=('Helvetica', 10, 'bold'))
            self.root.configure(bg='#f0f0f0')

    def create_widgets(self):
        """Create all widgets with error handling"""
        try:
            self.create_menu()
            self.create_main_frame()
            self.create_form_widgets()
            self.create_status_bar()
        except Exception as e:
            raise Exception(f"Widget creation failed: {str(e)}")

    def create_menu(self):
        """Create application menu"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV", command=self.export_complaints)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_checkbutton(label="Shortcuts Enabled", 
                                variable=tk.BooleanVar(value=self.settings['shortcuts_enabled']),
                                command=self.toggle_shortcuts)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_frame(self):
        """Create main application frame"""
        self.main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        
        # Labels
        self.name_label = ttk.Label(self.main_frame, 
                                  text="Full Name:",
                                  style='Custom.TLabel')
        self.gender_label = ttk.Label(self.main_frame,
                                    text="Gender:",
                                    style='Custom.TLabel')
        self.category_label = ttk.Label(self.main_frame,
                                      text="Category:",
                                      style='Custom.TLabel')
        self.priority_label = ttk.Label(self.main_frame,
                                      text="Priority:",
                                      style='Custom.TLabel')
        self.comment_label = ttk.Label(self.main_frame,
                                     text="Complaint Details:",
                                     style='Custom.TLabel')

    def create_form_widgets(self):
        """Create form input widgets"""
        # Name entry
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.main_frame,
                                  textvariable=self.name_var,
                                  font=('Helvetica', 11),
                                  width=40)

        # Gender selection
        self.gender_var = tk.StringVar()
        self.gender_frame = ttk.Frame(self.main_frame)
        self.male_radio = ttk.Radiobutton(self.gender_frame,
                                        text='Male',
                                        value='male',
                                        variable=self.gender_var)
        self.female_radio = ttk.Radiobutton(self.gender_frame,
                                          text='Female',
                                          value='female',
                                          variable=self.gender_var)
        self.other_radio = ttk.Radiobutton(self.gender_frame,
                                         text='Other',
                                         value='other',
                                         variable=self.gender_var)

        # Category selection
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.main_frame,
                                         textvariable=self.category_var,
                                         values=['General', 'Technical', 'Service', 'Billing', 'Other'],
                                         state='readonly',
                                         width=20)

        # Priority selection
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(self.main_frame,
                                         textvariable=self.priority_var,
                                         values=['High', 'Medium', 'Low'],
                                         state='readonly',
                                         width=20)
        self.priority_combo.set('Medium')

        # Tags entry
        self.tags_label = ttk.Label(self.main_frame,
                                  text="Tags (comma-separated):",
                                  style='Custom.TLabel')
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(self.main_frame,
                                  textvariable=self.tags_var,
                                  font=('Helvetica', 11),
                                  width=40)

        # Comment text area
        self.comment_text = tk.Text(self.main_frame,
                                  width=40,
                                  height=6,
                                  font=('Helvetica', 11),
                                  wrap=tk.WORD)

        # Attachment button
        self.attachment_button = ttk.Button(self.main_frame,
                                          text="Attach File",
                                          command=self.attach_file)
        self.attachment_path = None

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.submit_btn = ttk.Button(self.button_frame,
                                   text='Submit Complaint',
                                   style='Custom.TButton',
                                   command=self.safe_save_complaint)
        self.list_btn = ttk.Button(self.button_frame,
                                 text='View Complaints',
                                 style='Custom.TButton',
                                 command=self.safe_show_complaints)

    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root,
                                  textvariable=self.status_var,
                                  relief=tk.SUNKEN,
                                  anchor=tk.W)
        self.status_var.set("Ready")

    def setup_layout(self):
        """Setup widget layout"""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        # Layout widgets
        current_row = 0

        # Name
        self.name_label.grid(row=current_row, column=0, sticky='w', pady=(0, 10))
        self.name_entry.grid(row=current_row, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        current_row += 1

        # Gender
        self.gender_label.grid(row=current_row, column=0, sticky='w', pady=(0, 10))
        self.gender_frame.grid(row=current_row, column=1, columnspan=2, sticky='w', pady=(0, 10))
        self.male_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.female_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.other_radio.pack(side=tk.LEFT)
        current_row += 1

        # Category
        self.category_label.grid(row=current_row, column=0, sticky='w', pady=(0, 10))
        self.category_combo.grid(row=current_row, column=1, sticky='w', pady=(0, 10))
        current_row += 1

        # Priority
        self.priority_label.grid(row=current_row, column=0, sticky='w', pady=(0, 10))
        self.priority_combo.grid(row=current_row, column=1, sticky='w', pady=(0, 10))
        current_row += 1

        # Tags
        self.tags_label.grid(row=current_row, column=0, sticky='w', pady=(0, 10))
        self.tags_entry.grid(row=current_row, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        current_row += 1

        # Comment
        self.comment_label.grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        self.comment_text.grid(row=current_row, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        current_row += 1

        # Attachment
        self.attachment_button.grid(row=current_row, column=1, sticky='w', pady=(0, 10))
        current_row += 1

        # Buttons
        self.button_frame.grid(row=current_row, column=0, columnspan=3, pady=(10, 0))
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.list_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_bar.grid(row=current_row + 1, column=0, columnspan=3, sticky='ew')

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        if self.settings['shortcuts_enabled']:
            self.root.bind('<Control-s>', lambda e: self.safe_save_complaint())
            self.root.bind('<Control-l>', lambda e: self.safe_show_complaints())
            self.root.bind('<Control-e>', lambda e: self.export_complaints())
            self.root.bind('<Control-t>', lambda e: self.toggle_theme())
            self.root.bind('<F1>', lambda e: self.show_shortcuts())

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.settings['theme'] = 'dark' if self.settings['theme'] == 'light' else 'light'
        self.apply_theme(self.settings['theme'])
        self.save_settings()
        self.update_status("Theme changed to " + self.settings['theme'])

    def toggle_shortcuts(self):
        """Toggle keyboard shortcuts"""
        self.settings['shortcuts_enabled'] = not self.settings['shortcuts_enabled']
        if self.settings['shortcuts_enabled']:
            self.setup_shortcuts()
        else:
            # Unbind shortcuts
            for key in ['<Control-s>', '<Control-l>', '<Control-e>', '<Control-t>', '<F1>']:
                self.root.unbind(key)
        self.save_settings()
        self.update_status("Shortcuts " + ("enabled" if self.settings['shortcuts_enabled'] else "disabled"))

    def attach_file(self):
        """Handle file attachment"""
        try:
            filename = filedialog.askopenfilename()
            if filename:
                self.attachment_path = filename
                self.update_status(f"File attached: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to attach file: {str(e)}")

    def export_complaints(self):
        """Export complaints to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if filename:
                self.conn.export_to_csv(filename)
                self.update_status("Complaints exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def backup_database(self):
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/backups/backup_{timestamp}.db"
            self.conn.backup_database(backup_path)
            self.update_status("Database backup created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def restore_database(self):
        """Restore database from backup"""
        try:
            filename = filedialog.askopenfilename(
                initialdir="data/backups",
                filetypes=[("Database files", "*.db")]
            )
            if filename:
                if messagebox.askyesno("Confirm Restore", 
                                     "This will overwrite the current database. Continue?"):
                    self.conn.restore_database(filename)
                    self.update_status("Database restored successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")

    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts = """
        Keyboard Shortcuts:
        
        Ctrl+S: Submit complaint
        Ctrl+L: View complaints list
        Ctrl+E: Export complaints
        Ctrl+T: Toggle theme
        F1: Show this help
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def show_about(self):
        """Show about dialog"""
        about_text = """
        Complaint Management System
        Version 2.0
        
        Created by T. Landon Love
        12Stone Designs
        
        Contact: 12stonedesigns@gmail.com
        
        © 2023 12Stone Designs
        All rights reserved.
        """
        messagebox.showinfo("About", about_text)

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)

    def on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            self.settings['window_size'] = f"{event.width}x{event.height}"
            self.save_settings()

    def safe_save_complaint(self):
        """Safely save a new complaint"""
        try:
            # Validate required fields
            if not self.name_var.get().strip():
                raise ValueError("Name is required")
            if not self.gender_var.get():
                raise ValueError("Gender is required")
            if not self.category_var.get():
                raise ValueError("Category is required")
            if not self.comment_text.get("1.0", tk.END).strip():
                raise ValueError("Complaint details are required")

            # Save complaint
            complaint_data = {
                'name': self.name_var.get(),
                'gender': self.gender_var.get(),
                'category': self.category_var.get(),
                'priority': self.priority_var.get(),
                'tags': self.tags_var.get(),
                'details': self.comment_text.get("1.0", tk.END),
                'attachment': self.attachment_path
            }
            
            self.conn.save_complaint(complaint_data)
            self.clear_form()
            self.update_status("Complaint submitted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def safe_show_complaints(self):
        """Safely show complaints list"""
        try:
            ListComp()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open complaints list: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.name_var.set("")
        self.gender_var.set("")
        self.category_var.set("")
        self.priority_var.set("Medium")
        self.tags_var.set("")
        self.comment_text.delete("1.0", tk.END)
        self.attachment_path = None

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.handle_fatal_error("Runtime Error", e)

if __name__ == '__main__':
    try:
        app = ComplaintManager()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Fatal Error",
            f"Failed to start application:\n\n{str(e)}\n\nThe application will now close."
        )
        sys.exit(1)
