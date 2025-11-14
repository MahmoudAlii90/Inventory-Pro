import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self.create_all_tables()
        self.ensure_default_roles()
        self.ensure_admin_user()

    # ===============================================================
    # إنشاء الجداول
    # ===============================================================
    def create_all_tables(self):

        # --- roles ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS roles(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                permissions TEXT
            )
        """)

        # --- users ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                full_name TEXT,
                role_id INTEGER,
                created_at TEXT,
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        # --- activity log ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS activity_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                action TEXT,
                section TEXT,
                details TEXT,
                timestamp TEXT
            )
        """)

        # --- warehouses ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS warehouses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                location TEXT
            )
        """)

        # --- items ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS items(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                sku TEXT,
                quantity INTEGER DEFAULT 0,
                min_quantity INTEGER DEFAULT 0,
                warehouse_id INTEGER,
                FOREIGN KEY(warehouse_id) REFERENCES warehouses(id)
            )
        """)

        # --- suppliers ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS suppliers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                address TEXT
            )
        """)

        # --- customers ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS customers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                address TEXT
            )
        """)

        # --- transactions ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                item_id INTEGER,
                quantity INTEGER,
                from_warehouse INTEGER,
                to_warehouse INTEGER,
                user TEXT,
                notes TEXT,
                date TEXT,
                FOREIGN KEY(item_id) REFERENCES items(id),
                FOREIGN KEY(from_warehouse) REFERENCES warehouses(id),
                FOREIGN KEY(to_warehouse) REFERENCES warehouses(id)
            )
        """)

        # --- sales invoices ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_invoices(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total REAL,
                date TEXT,
                user TEXT
            )
        """)

        # --- sales items ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_items(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                item_id INTEGER,
                qty INTEGER,
                price REAL,
                FOREIGN KEY(invoice_id) REFERENCES sales_invoices(id),
                FOREIGN KEY(item_id) REFERENCES items(id)
            )
        """)

        # --- purchases invoices ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_invoices(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                total REAL,
                date TEXT,
                user TEXT
            )
        """)

        # --- purchase items ---
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_items(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                item_id INTEGER,
                qty INTEGER,
                price REAL,
                FOREIGN KEY(invoice_id) REFERENCES purchase_invoices(id),
                FOREIGN KEY(item_id) REFERENCES items(id)
            )
        """)

        self.conn.commit()

    # ===============================================================
    # أدوار وصلاحيات
    # ===============================================================
    def get_default_permissions(self):
        sections = [
            "dashboard", "items", "warehouses", "partners",
            "transactions", "price_list", "sales", "purchases",
            "profit", "reports", "activity", "backup", "users", "roles"
        ]

        perms = {}
        for s in sections:
            perms[s] = {"view": 1, "add": 1, "edit": 1, "delete": 1}

        return perms

    def ensure_default_roles(self):
        self.cur.execute("SELECT COUNT(*) FROM roles")
        if self.cur.fetchone()[0] == 0:
            self.add_role("مدير النظام", self.get_default_permissions())

    def ensure_admin_user(self):
        self.cur.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cur.fetchone():
            self.cur.execute("SELECT id FROM roles WHERE name='مدير النظام'")
            role_id = self.cur.fetchone()["id"]

            self.cur.execute("""
                INSERT INTO users(username, password, full_name, role_id)
                VALUES('admin', 'admin', 'Administrator', ?)
            """, (role_id,))
            self.conn.commit()

    def add_role(self, name, permissions):
        self.cur.execute("""
            INSERT INTO roles(name, permissions)
            VALUES(?, ?)
        """, (name, json.dumps(permissions)))
        self.conn.commit()

    # ===============================================================
    # إحضار جميع الأدوار
    # ===============================================================
    def get_roles(self):
        self.cur.execute("""
            SELECT id, name, permissions
            FROM roles
            ORDER BY id DESC
        """)
        roles = []
        for r in self.cur.fetchall():
            roles.append({
                "id": r["id"],
                "name": r["name"],
                "permissions": json.loads(r["permissions"]) if r["permissions"] else {}
            })
        return roles


    # ===============================================================
    # المستخدمين
    # ===============================================================
    def validate_user(self, username, password):
        self.cur.execute("""
            SELECT u.*, r.permissions AS role_permissions, r.name AS role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE username=? AND password=?
        """, (username, password))

        row = self.cur.fetchone()
        if not row: return None

        return {
            "username": row["username"],
            "full_name": row["full_name"],
            "role": row["role_name"],
            "permissions": json.loads(row["role_permissions"])
        }

    def get_users(self):
        self.cur.execute("""
            SELECT u.id, u.username, u.full_name, r.name AS role_name
            FROM users u
            LEFT JOIN roles r ON r.id = u.role_id
            ORDER BY u.id DESC
        """)
        return [dict(r) for r in self.cur.fetchall()]

    # ===============================================================
    # المخازن + الأصناف
    # ===============================================================
    def get_warehouses(self):
        self.cur.execute("SELECT * FROM warehouses")
        return [dict(r) for r in self.cur.fetchall()]

    def get_items(self):
        self.cur.execute("""
            SELECT items.*, warehouses.name AS warehouse
            FROM items
            LEFT JOIN warehouses ON warehouses.id = items.warehouse_id
        """)
        return [dict(r) for r in self.cur.fetchall()]

    # ===============================================================
    # الموردين + العملاء
    # ===============================================================
    def get_suppliers(self):
        self.cur.execute("SELECT * FROM suppliers")
        return [dict(r) for r in self.cur.fetchall()]

    def get_customers(self):
        self.cur.execute("SELECT * FROM customers")
        return [dict(r) for r in self.cur.fetchall()]

    # ===============================================================
    # العمليات (transactions)
    # ===============================================================
    def get_transactions(self):
        self.cur.execute("""
            SELECT 
                t.*, 
                items.name AS item_name,
                w1.name AS from_wh,
                w2.name AS to_wh
            FROM transactions t
            LEFT JOIN items ON items.id = t.item_id
            LEFT JOIN warehouses w1 ON w1.id = t.from_warehouse
            LEFT JOIN warehouses w2 ON w2.id = t.to_warehouse
            ORDER BY t.id DESC
        """)
        return [dict(r) for r in self.cur.fetchall()]

    # ===============================================================
    # الفواتير (مبيعات/مشتريات)
    # ===============================================================
    def get_sales_invoices(self):
        self.cur.execute("SELECT * FROM sales_invoices ORDER BY id DESC")
        return [dict(r) for r in self.cur.fetchall()]

    def get_purchase_invoices(self):
        self.cur.execute("SELECT * FROM purchase_invoices ORDER BY id DESC")
        return [dict(r) for r in self.cur.fetchall()]

    # ===============================================================
    # أرباح المبيعات
    # ===============================================================
    def get_sales_profit_data(self):
        self.cur.execute("""
            SELECT 
                s.id AS invoice_id,
                s.date,
                si.item_id,
                si.qty,
                si.price AS sale_price,
                items.name AS item_name,
                items.min_quantity,
                items.quantity
            FROM sales_items si
            LEFT JOIN sales_invoices s ON s.id = si.invoice_id
            LEFT JOIN items ON items.id = si.item_id
            ORDER BY s.id DESC
        """)
        return [dict(r) for r in self.cur.fetchall()]


    # ===============================================================
    # تكلفة المشتريات
    # ===============================================================
    def get_purchase_cost_data(self):
        self.cur.execute("""
            SELECT 
                p.id AS invoice_id,
                p.date,
                pi.item_id,
                pi.qty,
                pi.price AS cost_price,
                items.name AS item_name
            FROM purchase_items pi
            LEFT JOIN purchase_invoices p ON p.id = pi.invoice_id
            LEFT JOIN items ON items.id = pi.item_id
            ORDER BY p.id DESC
        """)
        return [dict(r) for r in self.cur.fetchall()]



    # ===============================================================
    # سجل النشاط
    # ===============================================================
    def add_log(self, user, action, section, details):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("""
            INSERT INTO activity_log(user, action, section, details, timestamp)
            VALUES(?, ?, ?, ?, ?)
        """, (user, action, section, details, ts))
        self.conn.commit()

    def get_logs(self):
        self.cur.execute("SELECT * FROM activity_log ORDER BY id DESC")
        return [dict(r) for r in self.cur.fetchall()]
