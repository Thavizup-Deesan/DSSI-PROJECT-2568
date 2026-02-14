import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def fix_schema():
    with connection.cursor() as cursor:
        print("Auditing schema...")
        
        # 1. Ensure tables exist
        tables_to_create = {
            'partial_receive_items': """
                CREATE TABLE IF NOT EXISTS partial_receive_items (
                    item_id SERIAL PRIMARY KEY,
                    partial_receive_id INTEGER NOT NULL REFERENCES partial_receives(receive_id) ON DELETE CASCADE,
                    order_item_id INTEGER NOT NULL REFERENCES order_items(item_id) ON DELETE CASCADE,
                    quantity INTEGER DEFAULT 0
                )
            """,
            'inspections': """
                CREATE TABLE IF NOT EXISTS inspections (
                    inspection_id SERIAL PRIMARY KEY,
                    partial_receive_id INTEGER UNIQUE NOT NULL REFERENCES partial_receives(receive_id) ON DELETE CASCADE,
                    committee_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    inspection_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    result VARCHAR(20),
                    comment TEXT
                )
            """
        }

        for table, sql in tables_to_create.items():
            cursor.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"Creating missing table '{table}'...")
                cursor.execute(sql)
            else:
                print(f"Table '{table}' already exists.")

        # 2. Fix purchase_orders
        po_columns = [
            ('inspection_committee_id', 'INTEGER REFERENCES users(user_id) ON DELETE SET NULL'),
            ('inspection_committee_name', 'VARCHAR(255)'),
            ('rejection_reason', 'TEXT'),
            ('approver_id', 'INTEGER REFERENCES users(user_id) ON DELETE SET NULL'),
            ('reason', 'TEXT'),
        ]
        for col, definition in po_columns:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'purchase_orders' AND column_name = '{col}'")
            if not cursor.fetchone():
                print(f"Adding missing column '{col}' to 'purchase_orders'...")
                cursor.execute(f"ALTER TABLE purchase_orders ADD COLUMN {col} {definition}")

        # 3. Fix partial_receives
        pr_columns = [
            ('committee_id', 'INTEGER REFERENCES users(user_id) ON DELETE SET NULL'),
            ('receipt_no', 'VARCHAR(100)'),
            ('receipt_file_path', 'VARCHAR(500)'),
        ]
        for col, definition in pr_columns:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'partial_receives' AND column_name = '{col}'")
            if not cursor.fetchone():
                print(f"Adding missing column '{col}' to 'partial_receives'...")
                cursor.execute(f"ALTER TABLE partial_receives ADD COLUMN {col} {definition}")

        # 4. Fix users
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role'")
        if not cursor.fetchone():
            print("Adding missing column 'role' to 'users'...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'User'")

        print("Schema audit complete.")

if __name__ == "__main__":
    fix_schema()
