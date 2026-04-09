import requests
import typer
from sqlmodel import select

from app.database import create_db_and_tables, drop_all, get_cli_session
from app.models.exercise import Exercise
from app.models.user import User
from app.utilities.security import encrypt_password

cli = typer.Typer()

API_URL = "https://7rjbixjepp.ufs.sh/f/3TSyxQfJpchbFREfy5mwSaRJOTILDMBYzexUbq4u9ciXQ7Hp"


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
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return

    if not isinstance(data, list):
        print("Unexpected API response format.")
        return

    inserted = 0
    skipped = 0

    with get_cli_session() as session:
        for item in data:
            exercise_id = item.get("exerciseId")
            if not exercise_id:
                skipped += 1
                continue

            existing = session.exec(
                select(Exercise).where(Exercise.exercise_id == exercise_id)
            ).first()

            if existing:
                skipped += 1
                continue

            image_urls = item.get("imageUrls", {})
            gif_urls = item.get("gifUrls", {})

            exercise = Exercise(
                exercise_id=exercise_id,
                name=item.get("name", "").strip(),
                image_url=image_urls.get("720p") or image_urls.get("480p") or image_urls.get("360p"),
                gif_url=gif_urls.get("720p") or gif_urls.get("480p") or gif_urls.get("360p"),
                body_part=", ".join(item.get("bodyParts", [])) if item.get("bodyParts") else None,
                target_muscle=", ".join(item.get("targetMuscles", [])) if item.get("targetMuscles") else None,
                secondary_muscle=", ".join(item.get("secondaryMuscles", [])) if item.get("secondaryMuscles") else None,
                equipment=", ".join(item.get("equipments", [])) if item.get("equipments") else None,
                difficulty=item.get("difficulty"),
                exercise_type=", ".join(item.get("exerciseTypes", [])) if item.get("exerciseTypes") else None,
                overview=item.get("overview"),
                instructions="\n".join(item.get("instructions", [])) if item.get("instructions") else None,
                related_exercise_ids=", ".join(item.get("relatedExerciseIds", [])) if item.get("relatedExerciseIds") else None,
            )

            session.add(exercise)
            inserted += 1

        session.commit()

    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    cli()