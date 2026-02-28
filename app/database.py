import os
from sqlmodel import create_engine, SQLModel, Session

# En prod (Docker) la base est dans /data, sinon dans le dossier local
DB_PATH = os.getenv("DB_PATH", "recipes.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session