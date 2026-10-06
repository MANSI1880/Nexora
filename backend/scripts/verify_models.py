import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models import Base

def test_models():
    tables = Base.metadata.tables.keys()
    assert "users" in tables, "users table missing"
    assert "tickets" in tables, "tickets table missing"
    assert "audit_logs" in tables, "audit_logs table missing"
    assert "approvals" in tables, "approvals table missing"
    print("All models loaded successfully!")
    print(f"Discovered tables: {list(tables)}")

if __name__ == "__main__":
    test_models()
