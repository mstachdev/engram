import sqlite3
import uuid
import json
from datetime import datetime
from dateutil import tz
from pathlib import Path

# Database path
DB_PATH = Path("cortex/data/fragments.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_database():
    """Initialize the fragments database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create fragments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fragments (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata TEXT,
            processed BOOLEAN DEFAULT FALSE,
            memory_id TEXT
        )
    ''')
    
    # Create sessions table for grouping fragments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT,
            created_at TEXT NOT NULL,
            metadata TEXT
        )
    ''')
    
    # Create fragment_sessions junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fragment_sessions (
            fragment_id TEXT,
            session_id TEXT,
            PRIMARY KEY (fragment_id, session_id),
            FOREIGN KEY (fragment_id) REFERENCES fragments(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_fragment(content, source="user", metadata=None, session_id=None):
    """Add a new fragment to the database."""
    fragment_id = str(uuid.uuid4())
    created_at = datetime.now(tz=tz.UTC).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO fragments (id, content, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (fragment_id, content, source, created_at, json.dumps(metadata or {})))
    
    # Link to session if provided
    if session_id:
        cursor.execute('''
            INSERT OR IGNORE INTO fragment_sessions (fragment_id, session_id)
            VALUES (?, ?)
        ''', (fragment_id, session_id))
    
    conn.commit()
    conn.close()
    
    return fragment_id

def get_fragments(session_id=None, processed=None, limit=None):
    """Retrieve fragments from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM fragments"
    params = []
    conditions = []
    
    if session_id:
        query = '''
            SELECT f.* FROM fragments f
            JOIN fragment_sessions fs ON f.id = fs.fragment_id
            WHERE fs.session_id = ?
        '''
        params.append(session_id)
    
    if processed is not None:
        if session_id:
            query += " AND f.processed = ?"
        else:
            conditions.append("processed = ?")
        params.append(processed)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    cursor.execute(query, params)
    fragments = cursor.fetchall()
    conn.close()
    
    # Convert to dict format
    columns = ['id', 'content', 'source', 'created_at', 'metadata', 'processed', 'memory_id']
    return [dict(zip(columns, fragment)) for fragment in fragments]

def create_session(name=None, metadata=None):
    """Create a new session for grouping fragments."""
    session_id = str(uuid.uuid4())
    created_at = datetime.now(tz=tz.UTC).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (id, name, created_at, metadata)
        VALUES (?, ?, ?, ?)
    ''', (session_id, name, created_at, json.dumps(metadata or {})))
    
    conn.commit()
    conn.close()
    
    return session_id

def mark_fragments_processed(fragment_ids, memory_id):
    """Mark fragments as processed and link to memory."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in fragment_ids])
    cursor.execute(f'''
        UPDATE fragments 
        SET processed = TRUE, memory_id = ?
        WHERE id IN ({placeholders})
    ''', [memory_id] + fragment_ids)
    
    conn.commit()
    conn.close()

def get_sessions():
    """Get all sessions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'name', 'created_at', 'metadata']
    return [dict(zip(columns, session)) for session in sessions]

# Initialize database on import
init_database() 