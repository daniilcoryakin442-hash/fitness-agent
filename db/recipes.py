# db/recipes.py — рецепты

from db.client import get_client

def get_cuisines() -> list:
    res = get_client().table("recipes").select("cuisine").execute()
    return sorted({r["cuisine"] for r in res.data}) if res.data else []

def get_categories(cuisine: str) -> list:
    res = get_client().table("recipes").select("category").eq("cuisine", cuisine).execute()
    return sorted({r["category"] for r in res.data}) if res.data else []

def get_recipes(cuisine: str, category: str) -> list:
    res = get_client().table("recipes")\
        .select("*").eq("cuisine", cuisine).eq("category", category).execute()
    return res.data or []

def get_recipe_by_id(recipe_id: int) -> dict | None:
    res = get_client().table("recipes").select("*").eq("id", recipe_id).execute()
    return res.data[0] if res.data else None
