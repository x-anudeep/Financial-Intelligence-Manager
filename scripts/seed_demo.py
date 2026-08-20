from app.database.session import SessionLocal
from app.services.seed import seed_database


if __name__ == "__main__":
    with SessionLocal() as db:
        print(seed_database(db))
