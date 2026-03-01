from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


# Table de liaison recette <-> tag
class RecipeTagLink(SQLModel, table=True):
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str  # "origin" ou "type"

    recipes: List["Recipe"] = Relationship(back_populates="tags", link_model=RecipeTagLink)


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    ingredients: str
    instructions: str
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    notes: Optional[str] = None

    tags: List[Tag] = Relationship(back_populates="recipes", link_model=RecipeTagLink)