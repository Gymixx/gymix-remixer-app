import time
from googleapiclient.discovery import build
from app.database import get_cli_session
from app.models.exercise import Exercise
from app.config import get_settings
from sqlmodel import select

settings = get_settings()
YOUTUBE_API_KEY = settings.youtube_api_key
BATCH_SIZE = 50

if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY is not set in your .env file.")

def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=f"{query} exercise form",
        type="video",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items", [])
    if items:
        video_id = items[0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def update_exercises():
    with get_cli_session() as session:
        exercises = session.exec(select(Exercise).where(Exercise.youtube_url == None)).all()
        total_missing = len(exercises)
        print(f"Found {total_missing} exercises without YouTube link.")
        if total_missing == 0:
            print("All exercises already have YouTube links!")
            return
        to_process = exercises[:BATCH_SIZE]
        print(f"Processing {len(to_process)} exercises this run.")
        updated = 0
        for idx, ex in enumerate(to_process, 1):
            print(f"[{idx}/{len(to_process)}] Searching: {ex.name}")
            url = search_youtube(ex.name)
            if url:
                ex.youtube_url = url
                session.add(ex)
                session.commit()
                print(f"   ✅ Added: {url}")
                updated += 1
            else:
                print(f"   ❌ No video found")
            time.sleep(0.5)
        print(f"\nDone! Updated {updated} exercises.")
        print(f"Remaining missing: {total_missing - len(to_process)}")

if __name__ == "__main__":
    update_exercises()