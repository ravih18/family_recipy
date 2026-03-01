from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io

# Couleurs de l'app
AMBER_DARK = colors.HexColor("#92400e")   # amber-800
AMBER_MID = colors.HexColor("#d97706")    # amber-600
AMBER_LIGHT = colors.HexColor("#fef3c7")  # amber-100
ORANGE_LIGHT = colors.HexColor("#fff7ed") # orange-50
GRAY = colors.HexColor("#6b7280")         # gray-500


def generate_recipe_pdf(recipe, ingredients: list, instructions: list) -> bytes:
    """Génère un PDF pour une recette et retourne les bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=recipe.title,
        author="Recettes de famille",
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    title_style = ParagraphStyle(
        "RecipeTitle",
        parent=styles["Title"],
        fontSize=26,
        textColor=AMBER_DARK,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "RecipeSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=GRAY,
        spaceAfter=12,
        fontName="Helvetica-Oblique",
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=AMBER_DARK,
        spaceBefore=16,
        spaceAfter=8,
        fontName="Helvetica-Bold",
        borderPad=4,
    )

    info_style = ParagraphStyle(
        "InfoStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=AMBER_MID,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#374151"),
        fontName="Helvetica",
        spaceAfter=4,
        leading=16,
    )

    note_style = ParagraphStyle(
        "NoteStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#78350f"),
        fontName="Helvetica-Oblique",
        leading=15,
    )

    tag_style = ParagraphStyle(
        "TagStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=AMBER_MID,
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )

    story = []

    # ── Titre ──────────────────────────────────────────────────────────────────
    story.append(Paragraph(recipe.title, title_style))

    if recipe.description:
        story.append(Paragraph(recipe.description, subtitle_style))

    story.append(HRFlowable(width="100%", thickness=2, color=AMBER_MID, spaceAfter=12))

    # ── Tags ───────────────────────────────────────────────────────────────────
    origin_tags = [t for t in recipe.tags if t.category == "origin"]
    type_tags = [t for t in recipe.tags if t.category == "type"]
    diet_tags = [t for t in recipe.tags if t.category == "diet"]

    all_tag_names = (
        [t.name for t in origin_tags] +
        [t.name for t in type_tags] +
        [t.name for t in diet_tags]
    )

    if all_tag_names:
        story.append(Paragraph("  •  ".join(all_tag_names), tag_style))
        story.append(Spacer(1, 8))

    # ── Infos rapides ──────────────────────────────────────────────────────────
    infos = []
    if recipe.prep_time:
        infos.append(f"⏱ Préparation : {recipe.prep_time} min")
    if recipe.cook_time:
        infos.append(f"🔥 Cuisson : {recipe.cook_time} min")
    if recipe.prep_time and recipe.cook_time:
        infos.append(f"🕐 Total : {recipe.prep_time + recipe.cook_time} min")
    if recipe.servings:
        infos.append(f"🍽 Portions : {recipe.servings}")

    if infos:
        for info in infos:
            story.append(Paragraph(info, info_style))
        story.append(Spacer(1, 8))

    story.append(HRFlowable(width="100%", thickness=0.5, color=AMBER_LIGHT, spaceAfter=4))

    # ── Ingrédients ────────────────────────────────────────────────────────────
    story.append(Paragraph("Ingrédients", section_style))

    ingredient_items = [
        ListItem(Paragraph(ing, body_style), bulletColor=AMBER_MID, leftIndent=16)
        for ing in ingredients if ing.strip()
    ]
    if ingredient_items:
        story.append(ListFlowable(ingredient_items, bulletType="bullet", start="•"))

    story.append(Spacer(1, 8))

    # ── Instructions ───────────────────────────────────────────────────────────
    story.append(Paragraph("Instructions", section_style))

    step_items = [
        ListItem(Paragraph(step, body_style), bulletColor=AMBER_MID, leftIndent=20)
        for step in instructions if step.strip()
    ]
    if step_items:
        story.append(ListFlowable(step_items, bulletType="1", start=1))

    story.append(Spacer(1, 8))

    # ── Notes ──────────────────────────────────────────────────────────────────
    if recipe.notes:
        story.append(HRFlowable(width="100%", thickness=0.5, color=AMBER_LIGHT, spaceAfter=8))
        story.append(Paragraph("💬 Commentaires & variantes", section_style))
        story.append(Paragraph(recipe.notes.replace("\n", "<br/>"), note_style))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=AMBER_LIGHT))
    story.append(Spacer(1, 4))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=GRAY,
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique",
    )
    story.append(Paragraph("Recettes de famille 🍽️", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()