from sqlalchemy import text
from app.database import engine

def add_youtube_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE exercise ADD COLUMN youtube_url VARCHAR"))
            conn.commit()
            print("✅ Added youtube_url column to exercise table")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("ℹ️ Column youtube_url already exists")
            else:
                print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    add_youtube_column()