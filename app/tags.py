from sqlmodel import Session, select
from app.models import Tag

# Tags prédéfinis par catégorie
PREDEFINED_TAGS = {
    "origin": [
        "France", "Inde", "Japon", "Italie", "Corée", "Madagascar", "Chine",
        "Maroc", "Mexique", "Grèce", "États-Unis", "Thaïlande", "Liban",
        "Portugal", "Espagne", "Angleterre", "Turquie", "Vietnam",
    ],
    "type": [
        "Entrée", "Plat", "Dessert", "Boisson", "Cocktail",
    ],
    "diet": [
        "Végétarien",
    ],
}

# Ordre d'affichage pour le tri par type
TYPE_ORDER = ["Entrée", "Plat", "Dessert", "Boisson", "Cocktail"]


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
    result = {"origin": [], "type": [], "diet": []}
    for tag in tags:
        if tag.category in result:
            result[tag.category].append(tag)
    # Trier les types dans le bon ordre
    result["type"].sort(key=lambda t: TYPE_ORDER.index(t.name) if t.name in TYPE_ORDER else 99)
    return result