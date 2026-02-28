from sqlmodel import Session, select
from app.models import Tag

# Tags prédéfinis par catégorie
PREDEFINED_TAGS = {
    "origin": [
        "France", "Italie", "Espagne", "Japon", "Chine", "Inde",
        "Maroc", "Mexique", "Grèce", "États-Unis", "Thaïlande", "Liban",
    ],
    "type": [
        "Entrée", "Plat principal", "Accompagnement", "Apéritif",
        "Dessert", "Soupe", "Salade", "Boisson", "Cocktail",
    ],
}


def init_tags(session: Session):
    """Crée les tags prédéfinis s'ils n'existent pas encore."""
    for category, names in PREDEFINED_TAGS.items():
        for name in names:
            existing = session.exec(select(Tag).where(Tag.name == name)).first()
            if not existing:
                session.add(Tag(name=name, category=category))
    session.commit()


def get_all_tags(session: Session) -> dict:
    """Retourne les tags groupés par catégorie."""
    tags = session.exec(select(Tag)).all()
    result = {"origin": [], "type": []}
    for tag in tags:
        if tag.category in result:
            result[tag.category].append(tag)
    return result