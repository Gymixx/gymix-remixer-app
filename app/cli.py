import requests
import typer
from sqlmodel import select

from app.database import create_db_and_tables, drop_all, get_cli_session
from app.models.exercise import Exercise
from app.models.user import User
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.utilities.security import encrypt_password

cli = typer.Typer()

API_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"


@cli.command()
def initialize():
    create_db_and_tables()

    with get_cli_session() as session:
        existing = session.exec(
            select(User).where(User.username == "bob")
        ).first()

        if not existing:
            bob = User(
                username="bob",
                email="bob@mail.com",
                password=encrypt_password("bobpass"),
                role="admin"
            )

            session.add(bob)
            session.commit()
            session.refresh(bob)

            print("Bob user created!")
        else:
            print("Bob already exists!")

        existing2 = session.exec(
            select(User).where(User.username == "bob2")
        ).first()

        if not existing2:
            bob2 = User(
                username="bob2",
                email="bob2@mail.com",
                password=encrypt_password("bob2pass"),
                role="user"
            )

            session.add(bob2)
            session.commit()
            session.refresh(bob2)

            print("Bob2 user created!")
        else:
            print("Bob2 already exists!")

    print("Database initialized!")


@cli.command()
def reset():
    drop_all()
    create_db_and_tables()
    print("Database reset complete!")


@cli.command("seed-exercises")
def seed_exercises():
    create_db_and_tables()

    try:
        response = requests.get(API_URL, timeout=60)
        response.raise_for_status()
        data = response.json()
        print(f"Total exercises fetched: {len(data)}")
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return

    if not isinstance(data, list):
        print("Unexpected API response python cli.py seed-exercisesformat.")
        return

    inserted = 0
    skipped = 0

    with get_cli_session() as session:
        for item in data:
            exercise_id = item.get("id")
            if not exercise_id:
                skipped += 1
                continue

            existing = session.exec(
                select(Exercise).where(Exercise.exercise_id == exercise_id)
            ).first()

            if existing:
                skipped += 1
                continue

            images = item.get("images", [])
            image_url = IMAGE_BASE_URL + images[0] if images else None

            exercise = Exercise(
                exercise_id=exercise_id,
                name=item.get("name", "").strip(),
                image_url=image_url,
                gif_url=None,
                body_part=item.get("category"),
                target_muscle=", ".join(item.get("primaryMuscles", [])) if item.get("primaryMuscles") else None,
                secondary_muscle=", ".join(item.get("secondaryMuscles", [])) if item.get("secondaryMuscles") else None,
                equipment=item.get("equipment"),
                difficulty=item.get("level"),
                exercise_type=item.get("mechanic"),
                overview=None,
                instructions="\n".join(item.get("instructions", [])) if item.get("instructions") else None,
                related_exercise_ids=None,
            )

            session.add(exercise)
            inserted += 1

        session.commit()

    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    cli()