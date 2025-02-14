import tkinter as tk
from tkinter import ttk, messagebox
from db import DBConnect
import sqlite3
import sys
import traceback
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from pathlib import Path

class ListComp:
    def __init__(self):
        try:
            self.setup_error_handling()
            self.load_settings()
            self.setup_window()
            self.create_styles()
            self.create_widgets()
            self.load_complaints()
            self.run()
        except Exception as e:
            self.handle_fatal_error("Initialization Error", e)

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

    def setup_error_handling(self):
        """Setup global error handling"""
        sys.excepthook = self.handle_uncaught_exception

    def load_settings(self):
        """Load saved settings"""
        try:
            settings_path = Path('data/settings.json')
            if settings_path.exists():
                with open(settings_path) as f:
                    self.settings = json.load(f)
            else:
                self.settings = {'theme': 'light'}
        except Exception:
            self.settings = {'theme': 'light'}

    def setup_window(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        self.root.title('Resolve-IQ - Complaint List')
        self.root.geometry('1200x800')
        self.root.configure(bg='#f0f0f0')
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def create_styles(self):
        """Create custom styles"""
        self.style = ttk.Style()
        self.apply_theme(self.settings.get('theme', 'light'))

    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        if theme_name == 'dark':
            bg_color = '#2d2d2d'
            fg_color = '#ffffff'
        else:
            bg_color = '#ffffff'
            fg_color = '#333333'

        self.style.configure('Custom.Treeview',
                           background=bg_color,
                           foreground=fg_color,
                           rowheight=25,
                           fieldbackground=bg_color)
        self.style.configure('Custom.Treeview.Heading',
                           background='#4a90e2',
                           foreground='white',
                           padding=(5, 5))
        self.style.map('Custom.Treeview',
                      background=[('selected', '#4a90e2')])

    def create_widgets(self):
        """Create all widgets"""
        self.create_notebook()
        self.create_search_frame()
        self.create_tree_frame()
        self.create_status_frame()
        self.create_dashboard_frame()

    def create_notebook(self):
        """Create notebook for different views"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # Main list view
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text='Complaints List')

        # Dashboard view
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text='Dashboard')

    def create_search_frame(self):
        """Create advanced search frame"""
        self.search_frame = ttk.LabelFrame(self.list_frame, text="Search & Filter", padding="10")
        self.search_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Search criteria
        current_row = 0

        # Text search
        ttk.Label(self.search_frame, text="Search:").grid(row=current_row, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=current_row, column=1, padx=5)

        # Status filter
        ttk.Label(self.search_frame, text="Status:").grid(row=current_row, column=2, padx=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(self.search_frame, 
                                       textvariable=self.status_var,
                                       values=['All', 'Pending', 'In Progress', 'Resolved', 'Closed'],
                                       state='readonly',
                                       width=15)
        self.status_combo.set('All')
        self.status_combo.grid(row=current_row, column=3, padx=5)

        # Priority filter
        ttk.Label(self.search_frame, text="Priority:").grid(row=current_row, column=4, padx=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(self.search_frame,
                                         textvariable=self.priority_var,
                                         values=['All', 'High', 'Medium', 'Low'],
                                         state='readonly',
                                         width=15)
        self.priority_combo.set('All')
        self.priority_combo.grid(row=current_row, column=5, padx=5)
        current_row += 1

        # Date range
        ttk.Label(self.search_frame, text="Date From:").grid(row=current_row, column=0, padx=5)
        self.date_from_var = tk.StringVar()
        self.date_from_entry = ttk.Entry(self.search_frame, textvariable=self.date_from_var, width=15)
        self.date_from_entry.grid(row=current_row, column=1, padx=5)

        ttk.Label(self.search_frame, text="Date To:").grid(row=current_row, column=2, padx=5)
        self.date_to_var = tk.StringVar()
        self.date_to_entry = ttk.Entry(self.search_frame, textvariable=self.date_to_var, width=15)
        self.date_to_entry.grid(row=current_row, column=3, padx=5)

        # Search buttons
        button_frame = ttk.Frame(self.search_frame)
        button_frame.grid(row=current_row, column=4, columnspan=2, pady=5)

        ttk.Button(button_frame, text="Search", command=self.apply_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Filter", command=self.save_filter).pack(side=tk.LEFT, padx=5)

    def create_tree_frame(self):
        """Create tree view frame"""
        self.tree_frame = ttk.Frame(self.list_frame)
        self.tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview with multiple selection enabled
        self.tree = ttk.Treeview(self.tree_frame,
                                style='Custom.Treeview',
                                yscrollcommand=self.scrollbar.set,
                                selectmode='extended')  # Allow multiple selections
        
        # Configure columns
        self.tree['columns'] = ('ID', 'Name', 'Gender', 'Category', 'Priority', 
                              'Status', 'Date', 'Updated')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('Name', width=150, anchor=tk.W)
        self.tree.column('Gender', width=80, anchor=tk.CENTER)
        self.tree.column('Category', width=100, anchor=tk.CENTER)
        self.tree.column('Priority', width=80, anchor=tk.CENTER)
        self.tree.column('Status', width=100, anchor=tk.CENTER)
        self.tree.column('Date', width=100, anchor=tk.CENTER)
        self.tree.column('Updated', width=100, anchor=tk.CENTER)

        # Configure headings
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_complaints(c))

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.tree.yview)

    def create_status_frame(self):
        """Create status update frame"""
        self.status_frame = ttk.LabelFrame(self.list_frame, text="Bulk Actions", padding="10")
        self.status_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        # Bulk status update
        ttk.Label(self.status_frame, text="Update Status:").pack(side=tk.LEFT, padx=5)
        self.bulk_status_var = tk.StringVar()
        self.bulk_status_combo = ttk.Combobox(self.status_frame,
                                            textvariable=self.bulk_status_var,
                                            values=['Pending', 'In Progress', 'Resolved', 'Closed'],
                                            state='readonly',
                                            width=15)
        self.bulk_status_combo.set('Pending')  # Set default value
        self.bulk_status_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.status_frame,
                  text="Update Selected",
                  command=self.bulk_update_status).pack(side=tk.LEFT, padx=5)
        
        # Add delete button
        ttk.Button(self.status_frame,
                  text="Delete Resolved",
                  command=self.delete_resolved).pack(side=tk.LEFT, padx=5)

    def delete_resolved(self):
        """Delete selected resolved complaints"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select complaints to delete")
                return

            # Get complaint IDs
            complaint_ids = [self.tree.item(item)['values'][0] for item in selection]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete the selected resolved complaints?"):
                self.dbconnect.delete_resolved_complaints(complaint_ids)
                self.load_complaints()  # Refresh the list
                messagebox.showinfo("Success", "Deleted resolved complaints")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete complaints: {str(e)}")

    def create_dashboard_frame(self):
        """Create dashboard with statistics and charts"""
        # Statistics frame
        self.stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Statistics", padding="10")
        self.stats_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

        # Charts frame
        self.charts_frame = ttk.Frame(self.dashboard_frame)
        self.charts_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        # Create figures for charts
        self.create_charts()

        # Refresh button
        ttk.Button(self.dashboard_frame,
                  text="Refresh Dashboard",
                  command=self.refresh_dashboard).grid(row=2, column=0, pady=5)

    def create_charts(self):
        """Create matplotlib charts"""
        # Status distribution pie chart
        self.fig1 = plt.Figure(figsize=(6, 4))
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.charts_frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

        # Resolution time trend line chart
        self.fig2 = plt.Figure(figsize=(6, 4))
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.charts_frame)
        self.canvas2.get_tk_widget().grid(row=0, column=1, padx=5, pady=5)

    def refresh_dashboard(self):
        """Update dashboard with latest statistics"""
        try:
            stats = self.dbconnect.get_statistics()
            
            # Update statistics labels
            self.update_statistics_labels(stats)
            
            # Update charts
            self.update_charts(stats)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dashboard: {str(e)}")

    def update_statistics_labels(self, stats):
        """Update statistics labels with new data"""
        labels = [
            f"Total Complaints: {stats['total']}",
            f"Pending: {stats['status_breakdown'].get('Pending', 0)}",
            f"In Progress: {stats['status_breakdown'].get('In Progress', 0)}",
            f"Resolved: {stats['status_breakdown'].get('Resolved', 0)}",
            f"Average Resolution Time: {stats.get('avg_resolution_days', 0):.1f} days"
        ]

        # Clear existing labels
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Create new labels
        for i, text in enumerate(labels):
            ttk.Label(self.stats_frame, text=text).grid(row=i, column=0, padx=5, pady=2, sticky='w')

    def update_charts(self, stats):
        """Update charts with new data"""
        # Clear previous charts
        self.ax1.clear()
        self.ax2.clear()

        # Status distribution pie chart
        status_data = stats['status_breakdown']
        self.ax1.pie(status_data.values(),
                    labels=status_data.keys(),
                    autopct='%1.1f%%')
        self.ax1.set_title('Complaint Status Distribution')

        # Priority distribution bar chart
        priority_data = stats['priority_breakdown']
        self.ax2.bar(priority_data.keys(), priority_data.values())
        self.ax2.set_title('Complaints by Priority')
        self.ax2.set_ylabel('Number of Complaints')

        # Refresh canvases
        self.canvas1.draw()
        self.canvas2.draw()

    def load_complaints(self):
        """Load complaints from database"""
        try:
            print("Attempting to connect to database...")  # Debug
            self.dbconnect = DBConnect()
            print("Database connection successful")  # Debug
            cursor = self.dbconnect.get_all_complaints()
            print("Retrieved complaints from database")  # Debug
            self.update_tree(cursor)
            print("Updated tree view with complaints")  # Debug
        except Exception as e:
            print(f"Error loading complaints: {str(e)}")  # Debug
            messagebox.showerror("Error", f"Failed to load complaints: {str(e)}")

    def update_tree(self, cursor):
        """Update treeview with complaint data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new data
        for row in cursor:
            values = (
                row['ID'],
                row['Name'],
                row['Gender'],
                row['Category'],
                row['Priority'],
                row['Status'],
                row['DateSubmitted'],
                row['LastUpdated']
            )
            self.tree.insert('', 'end', values=values)

    def sort_complaints(self, column):
        """Sort complaints by column"""
        try:
            cursor = self.dbconnect.sort_complaints(column)
            self.update_tree(cursor)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sort complaints: {str(e)}")

    def apply_search(self):
        """Apply search criteria"""
        try:
            criteria = {
                'name': self.search_var.get(),
                'status': self.status_var.get() if self.status_var.get() != 'All' else None,
                'priority': self.priority_var.get() if self.priority_var.get() != 'All' else None,
                'date_from': self.date_from_var.get(),
                'date_to': self.date_to_var.get()
            }
            
            cursor = self.dbconnect.advanced_search(criteria)
            self.update_tree(cursor)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def reset_search(self):
        """Reset search criteria"""
        self.search_var.set('')
        self.status_var.set('All')
        self.priority_var.set('All')
        self.date_from_var.set('')
        self.date_to_var.set('')
        self.load_complaints()

    def save_filter(self):
        """Save current search criteria"""
        try:
            name = messagebox.askstring("Save Filter", "Enter a name for this filter:")
            if name:
                criteria = {
                    'name': self.search_var.get(),
                    'status': self.status_var.get(),
                    'priority': self.priority_var.get(),
                    'date_from': self.date_from_var.get(),
                    'date_to': self.date_to_var.get()
                }
                
                # Save to file
                filters_file = Path('data/saved_filters.json')
                filters = {}
                if filters_file.exists():
                    with open(filters_file) as f:
                        filters = json.load(f)
                
                filters[name] = criteria
                
                filters_file.parent.mkdir(parents=True, exist_ok=True)
                with open(filters_file, 'w') as f:
                    json.dump(filters, f)
                
                messagebox.showinfo("Success", "Filter saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save filter: {str(e)}")

    def bulk_update_status(self):
        """Update status for selected complaints"""
        try:
            selection = self.tree.selection()
            print(f"Selected items: {selection}")  # Debug
            if not selection:
                messagebox.showwarning("Warning", "Please select complaints to update")
                return

            new_status = self.bulk_status_var.get()
            print(f"New status: {new_status}")  # Debug
            if not new_status:
                messagebox.showwarning("Warning", "Please select a status")
                return

            complaint_ids = [self.tree.item(item)['values'][0] for item in selection]
            print(f"Complaint IDs to update: {complaint_ids}")  # Debug
            self.dbconnect.bulk_update_status(complaint_ids, new_status)
            self.load_complaints()
            messagebox.showinfo("Success", f"Updated {len(selection)} complaints")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")

    def run(self):
        """Start the complaint list window"""
        self.root.mainloop()

if __name__ == '__main__':
    app = ListComp()
