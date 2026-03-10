# database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Database:
    """Class to manage the SQLite database for the karting repairs management system."""

    # ---- STATUS CONSTANTS ----
    KART_AVAILABLE = 0
    KART_MAINTENANCE = 1
    KART_RETIRED = 2

    PIECE_OK = 0
    PIECE_TO_ORDER = 1

    REPAIR_OPEN = 0
    REPAIR_CLOSED = 1

    ROLE_ADMIN = 0
    ROLE_USER = 1

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.create_tables()

        # add admin user if not exists
        admin = self.execute_query("""
        SELECT * FROM users WHERE user_role = ?
        """, (self.ROLE_ADMIN,), fetch=True)
        if not admin:
            self.create_user("admin", "karting", role=self.ROLE_ADMIN)

    # ---------------------------
    # CONNECTION
    # ---------------------------
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    # ---------------------------
    # GENERIC QUERY
    # ---------------------------

    def execute_query(self, query, params=None, fetch=False):
        if not self.conn:
            raise Exception("Database connection is not established.")

        cursor = self.conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        self.conn.commit()

        if fetch:
            rows = cursor.fetchall()

            # converte sqlite3.Row -> dict
            result = []
            for row in rows:
                result.append(dict(row))

            return result

    # ---------------------------
    # TABLE CREATION
    # ---------------------------
    def create_tables(self):

        # ---- KARTS ----
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS karts (
            kart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kart_num INTEGER UNIQUE NOT NULL,
            kart_mod TEXT,
            kart_note TEXT,
            kart_status INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---- PIECES ----
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS pieces (
            piece_id INTEGER PRIMARY KEY AUTOINCREMENT,
            piece_num INTEGER UNIQUE,
            piece_name TEXT NOT NULL,
            piece_model TEXT,
            piece_note TEXT,
            piece_quantity INTEGER DEFAULT 0,
            piece_status INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---- USERS ----
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_username TEXT UNIQUE NOT NULL,
            user_password TEXT NOT NULL,
            user_role INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ---- REPAIRS ----
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS repairs (
                repair_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_kart_id INTEGER NOT NULL,
                repair_user_id INTEGER NOT NULL,
                repair_note TEXT,
                repair_status INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME,
                FOREIGN KEY (repair_kart_id) REFERENCES karts(kart_id) ON DELETE CASCADE,
                FOREIGN KEY (repair_user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)

        # ---- REPAIR PIECES (many-to-many) ----
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS repair_pieces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repair_id INTEGER NOT NULL,
            piece_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (repair_id) REFERENCES repairs(repair_id) ON DELETE CASCADE,
            FOREIGN KEY (piece_id) REFERENCES pieces(piece_id)
        )
        """)

    # ---------------------------
    # USER MANAGEMENT
    # ---------------------------
    def create_user(self, username, password, role=ROLE_USER):
        hashed_password = generate_password_hash(password)

        self.execute_query("""
        INSERT INTO users (user_username, user_password, user_role)
        VALUES (?, ?, ?)
        """, (username, hashed_password, role))

    def verify_user(self, username, password):
        user = self.execute_query("""
        SELECT * FROM users WHERE user_username = ?
        """, (username,), fetch=True)

        if user:
            user = user[0]
            if check_password_hash(user["user_password"], password):
                return user
        return None
    
    def get_all_users(self):
        return self.execute_query("""
        SELECT user_id, user_username, user_role, created_at
        FROM users
        """, fetch=True)
    
    def update_user_role(self, user_id, new_role):
        self.execute_query("""
        UPDATE users
        SET user_role = ?
        WHERE user_id = ?
        """, (new_role, user_id))

    def delete_user(self, user_id):
        self.execute_query("""
        DELETE FROM users WHERE user_id = ?
        """, (user_id,))

    # ---------------------------
    # REPAIR MANAGEMENT
    # ---------------------------
    def close_repair(self, repair_id):
        self.execute_query("""
        UPDATE repairs
        SET repair_status = ?, closed_at = ?
        WHERE repair_id = ?
        """, (self.REPAIR_CLOSED, datetime.now(), repair_id))

    # ---------------------------
    # KART MANAGEMENT
    # ---------------------------

    def get_filtered_karts(self, num=None, model=None, status=None):

        query = "SELECT * FROM karts WHERE 1=1"
        params = []

        if num:
            query += " AND kart_num = ?"
            params.append(num)

        if model:
            query += " AND kart_mod LIKE ?"
            params.append(f"%{model}%")

        if status is not None and status != "":
            query += " AND kart_status = ?"
            params.append(status)

        return self.execute_query(query, params, fetch=True)

    def get_kart_models(self):
        return self.execute_query("""
            SELECT DISTINCT kart_mod
            FROM karts
            WHERE kart_mod IS NOT NULL AND kart_mod != ''
            ORDER BY kart_mod
        """, fetch=True)

    def get_all_karts(self):
        """Return all karts ordered by kart number."""
        return self.execute_query("""
            SELECT *
            FROM karts
            ORDER BY kart_num
        """, fetch=True)

    def get_kart_by_id(self, kart_id):
        """Return a single kart by its ID."""
        result = self.execute_query("""
            SELECT *
            FROM karts
            WHERE kart_id = ?
        """, (kart_id,), fetch=True)
        return result[0] if result else None

    def create_kart(self, num, model, note):
        """Create a new kart with default status AVAILABLE."""
        self.execute_query("""
            INSERT INTO karts (kart_num, kart_mod, kart_note)
            VALUES (?, ?, ?)
        """, (num, model, note))

    def update_kart(self, kart_id, num=None, model=None, note=None, status=None):
        """Update kart fields selectively. If a field is None, it is not updated."""
        kart = self.get_kart_by_id(kart_id)
        if not kart:
            raise Exception(f"Kart with ID {kart_id} does not exist.")

        new_num = num if num is not None else kart["kart_num"]
        new_model = model if model is not None else kart["kart_mod"]
        new_note = note if note is not None else kart["kart_note"]
        new_status = status if status is not None else kart["kart_status"]

        self.execute_query("""
            UPDATE karts
            SET kart_num = ?, kart_mod = ?, kart_note = ?, kart_status = ?
            WHERE kart_id = ?
        """, (new_num, new_model, new_note, new_status, kart_id))

    def update_kart_status(self, kart_id, new_status):
        """Change only the status of a kart."""
        self.execute_query("""
            UPDATE karts
            SET kart_status = ?
            WHERE kart_id = ?
        """, (new_status, kart_id))

    def delete_kart(self, kart_id):
        """Delete a kart by its ID."""
        self.execute_query("""
            DELETE FROM karts
            WHERE kart_id = ?
        """, (kart_id,))

    def get_kart_status_text(self, status):
        """Utility function to get human-readable status."""
        return {
            self.KART_AVAILABLE: "Available",
            self.KART_MAINTENANCE: "Under Maintenance",
            self.KART_RETIRED: "Retired"
        }.get(status, "Unknown")
    
    # ---------------------------
    # PIECE MANAGEMENT
    # ---------------------------

    def create_piece(self, name, model, quantity, note):

        quantity = int(quantity)


        # se quantità = 0 -> da ordinare
        status = self.PIECE_TO_ORDER if quantity == 0 else self.PIECE_OK

        self.execute_query("""
            INSERT INTO pieces (
                piece_name,
                piece_model,
                piece_quantity,
                piece_note,
                piece_status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (name, model, quantity, note, status))

    def get_all_pieces(self):

        return self.execute_query("""
            SELECT *
            FROM pieces
            ORDER BY piece_name
        """, fetch=True)


    def get_filtered_pieces(self, name=None, model=None, status=None):

        query = "SELECT * FROM pieces WHERE 1=1"
        params = []

        if name:
            query += " AND piece_name LIKE ?"
            params.append(f"%{name}%")

        if model:
            query += " AND piece_model LIKE ?"
            params.append(f"%{model}%")

        if status is not None and status != "":
            query += " AND piece_status = ?"
            params.append(status)

        query += " ORDER BY piece_name"

        return self.execute_query(query, params, fetch=True)


    def update_piece(self, piece_id, name, model, quantity, note, status):

        quantity = int(quantity)

        # se quantità = 0 forza "da ordinare"
        if quantity == 0:
            status = self.PIECE_TO_ORDER

        self.execute_query("""
            UPDATE pieces
            SET
                piece_name = ?,
                piece_model = ?,
                piece_quantity = ?,
                piece_note = ?,
                piece_status = ?
            WHERE piece_id = ?
        """, (name, model, quantity, note, status, piece_id))


    def delete_piece(self, piece_id):

        self.execute_query("""
            DELETE FROM pieces
            WHERE piece_id = ?
        """, (piece_id,))

    # ---------------------------
    # REPAIR MANAGEMENT
    # ---------------------------

    def get_all_repairs(self):

        return self.execute_query("""
            SELECT
                r.repair_id,
                r.repair_note,
                r.updated_at,
                k.kart_num,
                k.kart_mod
            FROM repairs r
            JOIN karts k ON r.repair_kart_id = k.kart_id
            ORDER BY r.updated_at DESC
        """, fetch=True)

    def create_repair(self, kart_id, user_id, note):

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO repairs (repair_kart_id, repair_user_id, repair_note)
            VALUES (?, ?, ?)
        """, (kart_id, user_id, note))

        self.conn.commit()

        return cursor.lastrowid


    def add_piece_to_repair(self, repair_id, piece_id, quantity):

        self.execute_query("""
            INSERT INTO repair_pieces (repair_id, piece_id, quantity)
            VALUES (?, ?, ?)
        """, (repair_id, piece_id, quantity))


    def get_pieces_for_repair(self, repair_id):

        return self.execute_query("""
            SELECT
                p.piece_name,
                rp.quantity
            FROM repair_pieces rp
            JOIN pieces p ON rp.piece_id = p.piece_id
            WHERE rp.repair_id = ?
        """, (repair_id,), fetch=True)


    def get_filtered_repairs(self, kart_num=None, kart_model=None, piece=None):

        query = """
        SELECT
            r.repair_id,
            r.repair_note,
            r.updated_at,
            k.kart_num,
            k.kart_mod
        FROM repairs r
        JOIN karts k ON r.repair_kart_id = k.kart_id
        LEFT JOIN repair_pieces rp ON r.repair_id = rp.repair_id
        LEFT JOIN pieces p ON rp.piece_id = p.piece_id
        WHERE 1=1
        """

        params = []

        if kart_num:
            query += " AND k.kart_num = ?"
            params.append(kart_num)

        if kart_model:
            query += " AND k.kart_mod LIKE ?"
            params.append(f"%{kart_model}%")

        if piece:
            query += " AND p.piece_name LIKE ?"
            params.append(f"%{piece}%")

        query += " GROUP BY r.repair_id ORDER BY r.updated_at DESC"

        return self.execute_query(query, params, fetch=True)
    
    def update_repair_timestamp(self, repair_id):

        self.execute_query("""
        UPDATE repairs
        SET updated_at = CURRENT_TIMESTAMP
        WHERE repair_id = ?
        """, (repair_id,))