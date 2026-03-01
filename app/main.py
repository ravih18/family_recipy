import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional

from app.database import create_db, get_session
from app.models import Recipe, Tag
from app.auth import is_authenticated, create_session_cookie, APP_PASSWORD, COOKIE_NAME
from app.tags import init_tags, get_all_tags

# Chemins absolus basés sur l'emplacement de ce fichier
BASE_DIR = Path(__file__).parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def on_startup():
    from app.database import engine
    create_db()
    with Session(engine) as session:
        init_tags(session)


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------

@app.get("/login")
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == APP_PASSWORD:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            key=COOKIE_NAME,
            value=create_session_cookie(),
            httponly=True,
            max_age=60 * 60 * 24 * 30,
        )
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Mot de passe incorrect."})


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------------------------------------------------------------------------
# Liste des recettes
# ---------------------------------------------------------------------------

@app.get("/")
def list_recipes(request: Request, session: Session = Depends(get_session)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipes = session.exec(select(Recipe)).all()
    recipes = sorted(recipes, key=lambda r: r.id, reverse=True)
    all_tags = get_all_tags(session)
    return templates.TemplateResponse("list.html", {
        "request": request,
        "recipes": recipes,
        "all_tags": all_tags,
    })


@app.get("/search")
def search_recipes(
    request: Request,
    q: str = "",
    tags: List[int] = Query(default=[]),
    sort: str = "recent",
    session: Session = Depends(get_session),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    query = select(Recipe)

    # Filtre par recherche textuelle
    if q:
        query = query.where(
            Recipe.title.ilike(f"%{q}%") |
            Recipe.description.ilike(f"%{q}%")
        )

    recipes = session.exec(query).all()

    # Filtre par tags
    if tags:
        recipes = [r for r in recipes if any(t.id in tags for t in r.tags)]

    # Tri
    type_order = ["Entrée", "Plat", "Dessert", "Boisson", "Cocktail"]

    if sort == "recent":
        recipes = sorted(recipes, key=lambda r: r.id, reverse=True)
    elif sort == "oldest":
        recipes = sorted(recipes, key=lambda r: r.id)
    elif sort == "alpha":
        recipes = sorted(recipes, key=lambda r: r.title.lower())
    elif sort == "type":
        def type_sort_key(recipe):
            type_tags = [t for t in recipe.tags if t.category == "type"]
            if type_tags:
                name = type_tags[0].name
                return type_order.index(name) if name in type_order else 99
            return 99
        recipes = sorted(recipes, key=type_sort_key)

    return templates.TemplateResponse("partials/recipe_list.html", {
        "request": request,
        "recipes": recipes,
    })


# ---------------------------------------------------------------------------
# Ajout d'une recette
# ---------------------------------------------------------------------------

@app.get("/add")
def add_recipe_form(request: Request, session: Session = Depends(get_session)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    all_tags = get_all_tags(session)
    return templates.TemplateResponse("add.html", {"request": request, "all_tags": all_tags})


@app.post("/add")
def add_recipe(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    ingredients: str = Form(...),
    instructions: str = Form(...),
    servings: Optional[int] = Form(None),
    prep_time: Optional[int] = Form(None),
    cook_time: Optional[int] = Form(None),
    tag_ids: List[int] = Form(default=[]),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipe = Recipe(
        title=title,
        description=description,
        ingredients=ingredients,
        instructions=instructions,
        servings=servings,
        prep_time=prep_time,
        cook_time=cook_time,
        notes=notes,
    )
    for tag_id in tag_ids:
        tag = session.get(Tag, tag_id)
        if tag:
            recipe.tags.append(tag)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return RedirectResponse(url=f"/recipe/{recipe.id}", status_code=303)


# ---------------------------------------------------------------------------
# Détail d'une recette
# ---------------------------------------------------------------------------

def recipe_template_context(request, recipe, extra={}):
    ingredients = [i for i in recipe.ingredients.splitlines() if i.strip()]
    instructions = [i for i in recipe.instructions.splitlines() if i.strip()]
    origin_tags = [t for t in recipe.tags if t.category == "origin"]
    type_tags = [t for t in recipe.tags if t.category == "type"]
    return {
        "request": request,
        "recipe": recipe,
        "ingredients": ingredients,
        "instructions": instructions,
        "origin_tags": origin_tags,
        "type_tags": type_tags,
        **extra,
    }


@app.get("/recipe/{recipe_id}")
def view_recipe(recipe_id: int, request: Request, session: Session = Depends(get_session)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("recipe.html", recipe_template_context(request, recipe))


# ---------------------------------------------------------------------------
# Modification d'une recette
# ---------------------------------------------------------------------------

@app.get("/recipe/{recipe_id}/edit")
def edit_recipe_form(recipe_id: int, request: Request, session: Session = Depends(get_session)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return RedirectResponse(url="/")
    all_tags = get_all_tags(session)
    selected_tag_ids = [t.id for t in recipe.tags]
    return templates.TemplateResponse("add.html", {
        "request": request,
        "all_tags": all_tags,
        "recipe": recipe,
        "selected_tag_ids": selected_tag_ids,
    })


@app.post("/recipe/{recipe_id}/edit")
def edit_recipe(
    recipe_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    ingredients: str = Form(...),
    instructions: str = Form(...),
    servings: Optional[int] = Form(None),
    prep_time: Optional[int] = Form(None),
    cook_time: Optional[int] = Form(None),
    tag_ids: List[int] = Form(default=[]),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return RedirectResponse(url="/")
    recipe.title = title
    recipe.description = description
    recipe.ingredients = ingredients
    recipe.instructions = instructions
    recipe.servings = servings
    recipe.prep_time = prep_time
    recipe.cook_time = cook_time
    recipe.notes = notes
    recipe.tags.clear()
    for tag_id in tag_ids:
        tag = session.get(Tag, tag_id)
        if tag:
            recipe.tags.append(tag)
    session.add(recipe)
    session.commit()
    return RedirectResponse(url=f"/recipe/{recipe_id}", status_code=303)


# ---------------------------------------------------------------------------
# Suppression d'une recette
# ---------------------------------------------------------------------------

@app.post("/recipe/{recipe_id}/delete")
def delete_recipe(
    recipe_id: int,
    request: Request,
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return RedirectResponse(url="/")
    if password != APP_PASSWORD:
        return templates.TemplateResponse("recipe.html", recipe_template_context(
            request, recipe, {"delete_error": "Mot de passe incorrect.", "show_delete_modal": True}
        ))
    session.delete(recipe)
    session.commit()
    return RedirectResponse(url="/", status_code=303)