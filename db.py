import sqlite3
from datetime import datetime
import re
import os
import csv
import json
import hashlib
from pathlib import Path

class DBConnect:
    def __init__(self):
        """Initialize database connection and create tables if not exists"""
        try:
            print("DBConnect: Creating data directories...")  # Debug
            # Ensure data directories exist
            self._create_data_directories()
            
            # Check if database exists
            db_exists = os.path.exists('information.db')
            print(f"DBConnect: Database exists: {db_exists}")  # Debug
            
            # Connect to database
            print("DBConnect: Connecting to database...")  # Debug
            self._db = sqlite3.connect('information.db')
            self._db.row_factory = sqlite3.Row
            print("DBConnect: Database connection established")  # Debug
            
            # Create/verify tables
            if not db_exists:
                print("DBConnect: Creating new tables...")  # Debug
                self._create_tables()
            else:
                print("DBConnect: Verifying table structure...")  # Debug
                self._verify_table_structure()
            print("DBConnect: Initialization complete")  # Debug
                
        except sqlite3.Error as e:
            print(f"DBConnect Error: {str(e)}")  # Debug
            raise Exception(f"Database connection failed: {str(e)}")

    def _create_data_directories(self):
        """Create necessary directories for file attachments and backups"""
        Path('data/attachments').mkdir(parents=True, exist_ok=True)
        Path('data/backups').mkdir(parents=True, exist_ok=True)
        Path('data/exports').mkdir(parents=True, exist_ok=True)

    def _create_tables(self):
        """Create all necessary database tables"""
        try:
            # Complaints table
            self._db.execute('''
                CREATE TABLE IF NOT EXISTS Comp (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name VARCHAR(255) NOT NULL,
                    Gender VARCHAR(50) NOT NULL,
                    Comment TEXT NOT NULL,
                    Status VARCHAR(50) DEFAULT 'Pending',
                    Priority VARCHAR(20) DEFAULT 'Medium',
                    Category VARCHAR(100),
                    Tags TEXT,
                    Resolution TEXT,
                    ResolutionDate DATETIME,
                    DateSubmitted DATETIME,
                    LastUpdated DATETIME,
                    AssignedTo VARCHAR(100),
                    AttachmentPath TEXT
                )
            ''')

            # Users table for authentication
            self._db.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username VARCHAR(100) UNIQUE NOT NULL,
                    PasswordHash TEXT NOT NULL,
                    Role VARCHAR(50) NOT NULL,
                    LastLogin DATETIME,
                    CreatedAt DATETIME,
                    UpdatedAt DATETIME
                )
            ''')

            # Audit log table
            self._db.execute('''
                CREATE TABLE IF NOT EXISTS AuditLog (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    UserID INTEGER,
                    Action VARCHAR(100) NOT NULL,
                    Details TEXT,
                    Timestamp DATETIME,
                    FOREIGN KEY (UserID) REFERENCES Users(ID)
                )
            ''')

            # Search filters table
            self._db.execute('''
                CREATE TABLE IF NOT EXISTS SavedFilters (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    UserID INTEGER,
                    Name VARCHAR(100) NOT NULL,
                    FilterCriteria TEXT NOT NULL,
                    CreatedAt DATETIME,
                    FOREIGN KEY (UserID) REFERENCES Users(ID)
                )
            ''')

            self._db.commit()
        except sqlite3.Error as e:
            raise Exception(f"Table creation failed: {str(e)}")

    def _verify_table_structure(self):
        """Verify and update table structure if needed"""
        try:
            # Get current table info
            cursor = self._db.execute("PRAGMA table_info(Comp)")
            columns = {row[1]: row for row in cursor.fetchall()}
            
            # Add new columns if they don't exist
            new_columns = {
                'Priority': 'VARCHAR(20) DEFAULT "Medium"',
                'Category': 'VARCHAR(100)',
                'Tags': 'TEXT',
                'Resolution': 'TEXT',
                'ResolutionDate': 'DATETIME',
                'AssignedTo': 'VARCHAR(100)',
                'AttachmentPath': 'TEXT'
            }

            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    self._db.execute(f"ALTER TABLE Comp ADD COLUMN {col_name} {col_type}")

            self._db.commit()
        except sqlite3.Error as e:
            raise Exception(f"Table verification failed: {str(e)}")

    def export_to_csv(self, filepath):
        """Export complaints to CSV file"""
        try:
            cursor = self._db.execute('SELECT * FROM Comp')
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([description[0] for description in cursor.description])
                writer.writerows(cursor)
            return True
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")

    def backup_database(self, backup_path):
        """Create a backup of the database"""
        try:
            backup_conn = sqlite3.connect(backup_path)
            self._db.backup(backup_conn)
            backup_conn.close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Backup failed: {str(e)}")

    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                raise Exception("Backup file not found")
            
            # Create a temporary connection to the backup
            backup_conn = sqlite3.connect(backup_path)
            
            # Restore the database
            backup_conn.backup(self._db)
            backup_conn.close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Restore failed: {str(e)}")

    def add_attachment(self, complaint_id, file_path):
        """Add file attachment to a complaint"""
        try:
            # Copy file to attachments directory
            filename = os.path.basename(file_path)
            new_path = f"data/attachments/{complaint_id}_{filename}"
            
            # Copy the file
            with open(file_path, 'rb') as src, open(new_path, 'wb') as dst:
                dst.write(src.read())
            
            # Update database
            self._db.execute('''
                UPDATE Comp 
                SET AttachmentPath = ?, LastUpdated = ?
                WHERE ID = ?
            ''', (new_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), complaint_id))
            
            self._db.commit()
            return True
        except Exception as e:
            raise Exception(f"Failed to add attachment: {str(e)}")

    def advanced_search(self, criteria):
        """Perform advanced search with multiple criteria"""
        try:
            query = "SELECT * FROM Comp WHERE 1=1"
            params = []

            if 'name' in criteria:
                query += " AND Name LIKE ?"
                params.append(f"%{criteria['name']}%")

            if 'status' in criteria:
                query += " AND Status = ?"
                params.append(criteria['status'])

            if 'priority' in criteria:
                query += " AND Priority = ?"
                params.append(criteria['priority'])

            if 'category' in criteria:
                query += " AND Category = ?"
                params.append(criteria['category'])

            if 'date_from' in criteria:
                query += " AND DateSubmitted >= ?"
                params.append(criteria['date_from'])

            if 'date_to' in criteria:
                query += " AND DateSubmitted <= ?"
                params.append(criteria['date_to'])

            if 'tags' in criteria:
                query += " AND Tags LIKE ?"
                params.append(f"%{criteria['tags']}%")

            cursor = self._db.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            raise Exception(f"Search failed: {str(e)}")

    def get_statistics(self):
        """Get complaint statistics"""
        try:
            stats = {}
            
            # Total complaints
            cursor = self._db.execute("SELECT COUNT(*) FROM Comp")
            stats['total'] = cursor.fetchone()[0]
            
            # Status breakdown
            cursor = self._db.execute("""
                SELECT Status, COUNT(*) as count 
                FROM Comp 
                GROUP BY Status
            """)
            stats['status_breakdown'] = dict(cursor.fetchall())
            
            # Priority breakdown
            cursor = self._db.execute("""
                SELECT Priority, COUNT(*) as count 
                FROM Comp 
                GROUP BY Priority
            """)
            stats['priority_breakdown'] = dict(cursor.fetchall())
            
            # Average resolution time
            cursor = self._db.execute("""
                SELECT AVG(julianday(ResolutionDate) - julianday(DateSubmitted)) as avg_days
                FROM Comp 
                WHERE Status = 'Resolved' 
                AND ResolutionDate IS NOT NULL
            """)
            stats['avg_resolution_days'] = cursor.fetchone()[0]
            
            return stats
        except sqlite3.Error as e:
            raise Exception(f"Failed to get statistics: {str(e)}")

    def bulk_update_status(self, complaint_ids, new_status):
        """Update status for multiple complaints"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            placeholders = ','.join('?' for _ in complaint_ids)
            self._db.execute(f'''
                UPDATE Comp 
                SET Status = ?, LastUpdated = ?
                WHERE ID IN ({placeholders})
            ''', [new_status, current_time] + complaint_ids)
            
            self._db.commit()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Bulk update failed: {str(e)}")

    def delete_resolved_complaints(self, complaint_ids):
        """Delete resolved complaints"""
        try:
            placeholders = ','.join('?' for _ in complaint_ids)
            self._db.execute(f'''
                DELETE FROM Comp 
                WHERE ID IN ({placeholders})
                AND Status = 'Resolved'
            ''', complaint_ids)
            
            self._db.commit()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Delete failed: {str(e)}")

    def get_all_complaints(self):
        """Retrieve all complaints from the database"""
        try:
            cursor = self._db.execute('''
                SELECT 
                    ID,
                    Name,
                    Gender,
                    Category,
                    Priority,
                    Status,
                    DateSubmitted,
                    LastUpdated
                FROM Comp
                ORDER BY LastUpdated DESC
            ''')
            return cursor
        except sqlite3.Error as e:
            raise Exception(f"Failed to load complaints: {str(e)}")

    def save_complaint(self, complaint_data):
        """Save a new complaint to the database"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert complaint
            cursor = self._db.execute('''
                INSERT INTO Comp (
                    Name, Gender, Comment, Category, Priority, 
                    Tags, AttachmentPath, DateSubmitted, LastUpdated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                complaint_data['name'],
                complaint_data['gender'],
                complaint_data['details'],
                complaint_data['category'],
                complaint_data['priority'],
                complaint_data['tags'],
                complaint_data['attachment'],
                current_time,
                current_time
            ))
            
            complaint_id = cursor.lastrowid
            self._db.commit()
            
            # Handle attachment if provided
            if complaint_data['attachment']:
                self.add_attachment(complaint_id, complaint_data['attachment'])
            
            return complaint_id
        except sqlite3.Error as e:
            raise Exception(f"Failed to save complaint: {str(e)}")

    def __del__(self):
        """Ensure proper database connection cleanup"""
        try:
            if hasattr(self, '_db'):
                self._db.close()
        except sqlite3.Error:
            pass  # Suppress errors during cleanup
