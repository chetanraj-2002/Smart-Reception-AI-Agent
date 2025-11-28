import sqlite3
import os
from typing import List, Dict
from config import DB_NAME
from datetime import datetime

def init_db():
    """Initialize the SQLite database with the tickets table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            caller_name TEXT,
            caller_contact TEXT,
            intent_category TEXT NOT NULL,
            department TEXT NOT NULL,
            priority TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary_short TEXT NOT NULL,
            summary_full TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_ticket(ticket_data: Dict) -> int:
    """
    Insert a new ticket into the database.
    
    Args:
        ticket_data (Dict): Dictionary containing ticket information
        
    Returns:
        int: The ID of the inserted ticket
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Add timestamp if not present
    if 'created_at' not in ticket_data:
        ticket_data['created_at'] = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO tickets (
            created_at, caller_name, caller_contact, intent_category,
            department, priority, sentiment, transcript, summary_short, summary_full
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_data['created_at'],
        ticket_data.get('caller_name'),
        ticket_data.get('caller_contact'),
        ticket_data['intent_category'],
        ticket_data['department'],
        ticket_data['priority'],
        ticket_data['sentiment'],
        ticket_data['transcript'],
        ticket_data['summary_short'],
        ticket_data['summary_full']
    ))
    
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return ticket_id

def fetch_recent_tickets(limit: int = 5) -> List[Dict]:
    """
    Fetch the most recent tickets from the database.
    
    Args:
        limit (int): Maximum number of tickets to fetch
        
    Returns:
        List[Dict]: List of ticket dictionaries
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tickets 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    tickets = [dict(row) for row in rows]
    return tickets

def fetch_all_tickets() -> List[Dict]:
    """
    Fetch all tickets from the database, sorted by latest first.
    
    Returns:
        List[Dict]: List of all ticket dictionaries
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tickets 
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    tickets = [dict(row) for row in rows]
    return tickets

def get_ticket_count() -> int:
    """
    Get the total number of tickets in the database.
    
    Returns:
        int: Total number of tickets
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM tickets')
    count = cursor.fetchone()[0]
    conn.close()
    
    return count