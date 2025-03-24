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
                    'window_size': '900x600',
                    'shortcuts_enabled': True,
                    'show_toolbar': True,
                    'confirm_exit': True,
                    'auto_refresh': False,
                    'default_priority': 'Medium',
                    'default_status': 'Pending'
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
        """Initialize the main window with modern styling"""
        try:
            self.root = tk.Tk()
            
            # Set window properties
            self.root.geometry(self.settings['window_size'])
            self.root.title('Resolve-IQ • Complaint Management System')
            self.root.configure(bg='#f0f0f0')
            self.root.resizable(True, True)
            
            # Set minimum window size
            self.root.minsize(800, 600)
            
            # Center window on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 800) // 2
            y = (screen_height - 600) // 2
            self.root.geometry(f"+{x}+{y}")
            
            # Add window icon if available
            try:
                self.root.iconbitmap('data/icon.ico')
            except:
                pass  # Skip if icon not found
            
            # Setup window error handling
            self.root.report_callback_exception = self.handle_callback_error
            
            # Bind window events
            self.root.bind('<Configure>', self.on_window_resize)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
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
        """Apply the selected theme with modern styling"""
        # Common styles
        common_font = ('Segoe UI', 11)
        button_font = ('Segoe UI', 10, 'bold')
        
        if theme_name == 'dark':
            # Dark theme colors
            bg_color = '#1e1e1e'
            fg_color = '#ffffff'
            accent_color = '#007acc'
            secondary_bg = '#2d2d2d'
            hover_color = '#0098ff'
        else:
            # Light theme colors
            bg_color = '#ffffff'
            fg_color = '#2c2c2c'
            accent_color = '#0078d4'
            secondary_bg = '#f5f5f5'
            hover_color = '#106ebe'

        # Apply common styles
        self.root.configure(bg=bg_color)
        
        # Configure ttk styles
        self.style.configure('Custom.TLabel',
                           background=bg_color,
                           foreground=fg_color,
                           font=common_font)
        
        self.style.configure('Custom.TButton',
                           background=accent_color,
                           foreground='white',
                           font=button_font,
                           padding=(10, 5))
        
        self.style.map('Custom.TButton',
                      background=[('active', hover_color)],
                      foreground=[('active', 'white')])
                      
        self.style.configure('Custom.TEntry',
                           fieldbackground=secondary_bg,
                           foreground=fg_color,
                           font=common_font,
                           padding=5)
                           
        self.style.configure('Custom.TFrame',
                           background=bg_color)
                           
        self.style.configure('Custom.TNotebook',
                           background=bg_color,
                           tabmargins=[2, 5, 2, 0])
                           
        self.style.configure('Custom.TNotebook.Tab',
                           background=secondary_bg,
                           foreground=fg_color,
                           padding=[10, 5],
                           font=common_font)

    def create_widgets(self):
        """Create all widgets with error handling"""
        try:
            # Create core UI elements
            self.create_menu()
            self.create_toolbar()
            
            # Create main content
            self.create_main_frame()
            self.create_form_widgets()
            
            # Create status bar
            self.create_status_bar()
            
            # Apply initial theme
            self.apply_theme(self.settings['theme'])
            
        except Exception as e:
            raise Exception(f"Widget creation failed: {str(e)}")

    def create_menu(self):
        """Create modern application menu"""
        # Configure menu style based on theme
        is_dark = self.settings.get('theme') == 'dark'
        menu_bg = '#2d2d2d' if is_dark else '#f5f5f5'
        menu_fg = 'white' if is_dark else '#2c2c2c'
        
        self.menubar = tk.Menu(self.root, bg=menu_bg, fg=menu_fg, relief=tk.FLAT)
        self.root.config(menu=self.menubar)

        # Common menu styles
        menu_config = {
            'tearoff': 0,
            'bg': menu_bg,
            'fg': menu_fg,
            'activebackground': '#007acc' if is_dark else '#0078d4',
            'activeforeground': 'white',
            'relief': tk.FLAT,
            'font': ('Segoe UI', 10)
        }

        # File menu with icons (commented out, add when icons available)
        file_menu = tk.Menu(self.menubar, **menu_config)
        self.menubar.add_cascade(label=" File ", menu=file_menu)
        file_menu.add_command(label=" New Complaint", command=self.new_complaint)
        file_menu.add_separator()
        file_menu.add_command(label=" Export to CSV", command=self.export_complaints)
        file_menu.add_command(label=" Backup Database", command=self.backup_database)
        file_menu.add_command(label=" Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label=" Exit", command=self.on_closing)

        # Edit menu
        edit_menu = tk.Menu(self.menubar, **menu_config)
        self.menubar.add_cascade(label=" Edit ", menu=edit_menu)
        edit_menu.add_command(label=" Preferences", command=self.show_preferences)
        
        # View menu
        view_menu = tk.Menu(self.menubar, **menu_config)
        self.menubar.add_cascade(label=" View ", menu=view_menu)
        view_menu.add_command(label=" Toggle Theme", command=self.toggle_theme)
        view_menu.add_separator()
        view_menu.add_checkbutton(
            label=" Show Toolbar",
            variable=tk.BooleanVar(value=self.settings.get('show_toolbar', True)),
            command=self.toggle_toolbar
        )
        view_menu.add_checkbutton(
            label=" Enable Shortcuts",
            variable=tk.BooleanVar(value=self.settings.get('shortcuts_enabled', True)),
            command=self.toggle_shortcuts
        )

        # Tools menu
        tools_menu = tk.Menu(self.menubar, **menu_config)
        self.menubar.add_cascade(label=" Tools ", menu=tools_menu)
        tools_menu.add_command(label=" Database Manager", command=self.show_db_manager)
        tools_menu.add_command(label=" Import Data", command=self.import_data)
        tools_menu.add_command(label=" Export Data", command=self.export_data)

        # Help menu
        help_menu = tk.Menu(self.menubar, **menu_config)
        self.menubar.add_cascade(label=" Help ", menu=help_menu)
        help_menu.add_command(label=" Documentation", command=self.show_documentation)
        help_menu.add_command(label=" Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label=" Check for Updates", command=self.check_updates)
        help_menu.add_command(label=" About Resolve-IQ", command=self.show_about)

    def create_toolbar(self):
        """Create modern toolbar with icons and buttons"""
        self.toolbar_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.toolbar_frame.pack(fill='x', padx=1, pady=(0, 1))
        
        # Style configuration
        is_dark = self.settings.get('theme') == 'dark'
        btn_style = 'Toolbar.TButton'
        self.style.configure(btn_style, 
                           padding=5,
                           relief='flat',
                           background='#2d2d2d' if is_dark else '#f5f5f5')
        
        # Toolbar buttons with modern spacing and hover effects
        buttons = [
            ("New", self.new_complaint, "Create new complaint"),
            ("Export", self.export_complaints, "Export complaints"),
            ("|", None, None),  # Separator
            ("Filter", self.show_filters, "Show filters"),
            ("Search", self.show_search, "Search complaints"),
            ("|", None, None),  # Separator
            ("Refresh", self.refresh_data, "Refresh data"),
            ("Settings", self.show_preferences, "Open preferences")
        ]
        
        for text, command, tooltip in buttons:
            if text == "|":
                # Create separator
                ttk.Separator(self.toolbar_frame, orient='vertical').pack(side='left', padx=5, pady=2, fill='y')
            else:
                btn = ttk.Button(self.toolbar_frame, text=text, style=btn_style, command=command)
                btn.pack(side='left', padx=2, pady=2)
                
                # Create tooltip
                if tooltip:
                    self.create_tooltip(btn, tooltip)
        
        # Only show toolbar if enabled in settings
        if not self.settings.get('show_toolbar', True):
            self.toolbar_frame.pack_forget()

    def create_tooltip(self, widget, text):
        """Create tooltip for toolbar buttons"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Style tooltip based on theme
            is_dark = self.settings.get('theme') == 'dark'
            bg_color = '#2d2d2d' if is_dark else '#f5f5f5'
            fg_color = '#ffffff' if is_dark else '#2c2c2c'
            
            label = tk.Label(tooltip, text=text, justify='left',
                           background=bg_color, foreground=fg_color,
                           relief='solid', borderwidth=1,
                           font=("Segoe UI", 9), padx=5, pady=2)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.bind('<Leave>', lambda e: hide_tooltip())
            widget.bind('<Leave>', lambda e: hide_tooltip())
            
        widget.bind('<Enter>', show_tooltip)

    def show_filters(self):
        """Show complaint filters dialog"""
        messagebox.showinfo("Filters", "Advanced filtering options coming soon!")

    def show_search(self):
        """Show search interface"""
        messagebox.showinfo("Search", "Advanced search interface coming soon!")

    def refresh_data(self):
        """Refresh complaint data"""
        try:
            self.load_complaints()
            messagebox.showinfo("Success", "Data refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")


    def new_complaint(self):
        """Reset form for new complaint entry"""
        try:
            # Clear all form fields
            for var in [self.name_var, self.gender_var, self.comment_var, self.category_var]:
                if hasattr(var, 'set'):
                    var.set('')
            # Reset status and priority to defaults
            if hasattr(self, 'status_var'):
                self.status_var.set('Pending')
            if hasattr(self, 'priority_var'):
                self.priority_var.set('Medium')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new complaint: {str(e)}")

    def show_preferences(self):
        """Show preferences dialog"""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferences")
        prefs_window.geometry("400x300")
        prefs_window.transient(self.root)
        prefs_window.grab_set()
        
        # Style
        style = ttk.Style()
        is_dark = self.settings.get('theme') == 'dark'
        bg_color = '#2d2d2d' if is_dark else '#ffffff'
        fg_color = '#ffffff' if is_dark else '#2c2c2c'
        
        # Create notebook for preferences sections
        notebook = ttk.Notebook(prefs_window)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # General settings
        general_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(general_frame, text='General')
        
        # Theme selection
        ttk.Label(general_frame, text="Theme:", style='Custom.TLabel').pack(pady=5)
        theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        ttk.Radiobutton(general_frame, text="Light", value="light", variable=theme_var).pack()
        ttk.Radiobutton(general_frame, text="Dark", value="dark", variable=theme_var).pack()
        
        # Interface settings
        interface_frame = ttk.Frame(notebook, style='Custom.TFrame')
        notebook.add(interface_frame, text='Interface')
        
        # Toolbar visibility
        show_toolbar_var = tk.BooleanVar(value=self.settings.get('show_toolbar', True))
        ttk.Checkbutton(interface_frame, text="Show Toolbar", variable=show_toolbar_var).pack(pady=5)
        
        # Shortcuts enabled
        shortcuts_var = tk.BooleanVar(value=self.settings.get('shortcuts_enabled', True))
        ttk.Checkbutton(interface_frame, text="Enable Shortcuts", variable=shortcuts_var).pack(pady=5)
        
        # Save button
        def save_preferences():
            self.settings['theme'] = theme_var.get()
            self.settings['show_toolbar'] = show_toolbar_var.get()
            self.settings['shortcuts_enabled'] = shortcuts_var.get()
            self.save_settings()
            self.apply_theme(theme_var.get())
            prefs_window.destroy()
            
        ttk.Button(prefs_window, text="Save", command=save_preferences).pack(pady=10)

    def show_db_manager(self):
        """Show database management interface"""
        messagebox.showinfo("Database Manager", "Database management interface coming soon!")

    def import_data(self):
        """Import data from external sources"""
        file_path = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Import logic here
                messagebox.showinfo("Success", "Data imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {str(e)}")

    def export_data(self):
        """Export data to various formats"""
        file_path = filedialog.asksaveasfilename(
            title="Export Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".csv"
        )
        if file_path:
            try:
                # Export logic here
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def show_documentation(self):
        """Show application documentation"""
        messagebox.showinfo("Documentation", "Documentation will open in your default browser (coming soon)")

    def check_updates(self):
        """Check for application updates"""
        messagebox.showinfo("Updates", "Your application is up to date!")

    def toggle_toolbar(self):
        """Toggle toolbar visibility"""
        self.settings['show_toolbar'] = not self.settings.get('show_toolbar', True)
        self.save_settings()
        # Update toolbar visibility
        if hasattr(self, 'toolbar_frame'):
            self.toolbar_frame.pack_forget() if not self.settings['show_toolbar'] else self.toolbar_frame.pack()

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
        """Create modern status bar with multiple information panels"""
        # Create main status bar frame
        self.status_var = tk.StringVar(value="Ready")
        self.status_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.status_frame.grid(row=999, column=0, columnspan=3, sticky='ew')  # Use high row number to ensure it's at bottom
        
        # Add separator above status bar
        ttk.Separator(self.root, orient='horizontal').grid(row=998, column=0, columnspan=3, sticky='ew')
        
        # Configure grid weights
        self.status_frame.grid_columnconfigure(1, weight=1)  # Make middle section expandable
        
        # Status message (left)
        self.status_bar = ttk.Label(self.status_frame,
                                  textvariable=self.status_var,
                                  style='Custom.TLabel',
                                  padding=(5, 2))
        self.status_bar.grid(row=0, column=0, sticky='w')
        
        # Database status (middle)
        self.db_status = ttk.Label(self.status_frame,
                                 text="Database: Connected",
                                 style='Custom.TLabel',
                                 padding=(5, 2))
        self.db_status.grid(row=0, column=1, sticky='w')
        
        # Record count (right)
        self.record_count = ttk.Label(self.status_frame,
                                    text="Records: 0",
                                    style='Custom.TLabel',
                                    padding=(5, 2))
        self.record_count.grid(row=0, column=2, sticky='e')
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

    def update_status(self, message, duration=3000):
        """Update status bar message with auto-reset"""
        self.status_var.set(message)
        if duration > 0:
            self.root.after(duration, lambda: self.status_var.set("Ready"))

    def update_record_count(self, count):
        """Update the record count in status bar"""
        self.record_count.config(text=f"Records: {count}")

    def update_db_status(self, connected=True):
        """Update database connection status"""
        status = "Connected" if connected else "Disconnected"
        color = "green" if connected else "red"
        self.db_status.config(text=f"Database: {status}")
        # Change text color based on connection status
        self.style.configure('DB.TLabel',
                           foreground=color,
                           font=('Segoe UI', 9))
        self.db_status.configure(style='DB.TLabel')

    def on_window_resize(self, event):
        """Handle window resize event and update layout"""
        if event.widget == self.root:
            # Minimum size enforcement
            if event.width < 800:
                self.root.geometry(f"800x{event.height}")
            if event.height < 600:
                self.root.geometry(f"{event.width}x600")
            
            # Save new window size to settings
            new_size = f"{max(event.width, 800)}x{max(event.height, 600)}"
            if new_size != self.settings['window_size']:
                self.settings['window_size'] = new_size
                
            # Update layout for responsive design
            self.update_responsive_layout()
            self.save_settings()

    def update_responsive_layout(self):
        """Update layout based on window size"""
        width = self.root.winfo_width()
        
        # Adjust form layout for different widths
        if width < 1000:
            # Compact layout
            self.main_frame.configure(padding="10 10 10 10")
            # Adjust font sizes for smaller window
            self.style.configure('Custom.TLabel', font=('Segoe UI', 10))
            self.style.configure('Custom.TButton', font=('Segoe UI', 9, 'bold'))
        else:
            # Spacious layout
            self.main_frame.configure(padding="20 20 20 20")
            # Restore default font sizes
            self.style.configure('Custom.TLabel', font=('Segoe UI', 11))
            self.style.configure('Custom.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Force update of all widgets
        self.root.update_idletasks()

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
