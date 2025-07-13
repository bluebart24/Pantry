from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
import time
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', '4256ad2a43f448a6bd7f6c1f45e9d894')

# Common default set of stable pantry ingredients
DEFAULT_PANTRY = [
    "salt", "black pepper", "olive oil", "vegetable oil", "canola oil", "flour", "sugar", "brown sugar", "baking powder", "baking soda",
    "soy sauce", "vinegar", "honey", "mustard", "ketchup", "mayonnaise", "butter", "eggs", "milk", "garlic powder", "onion powder",
    "dried oregano", "dried basil", "dried thyme", "dried rosemary", "dried parsley", "cinnamon", "nutmeg", "paprika", "red pepper flakes",
    "rice", "pasta", "breadcrumbs", "cornstarch", "chicken broth", "beef broth", "tomato paste", "peanut butter",
    # Canned and frozen vegetables, meats, and juices
    "canned corn", "canned green beans", "canned beans", "ground beef", "chicken breasts", "tomato juice", "frozen vegetable mix",
    # Added sauces and bases
    "red pasta sauce", "chicken base", "cream of chicken soup", "cream of mushroom soup",
    # Bean varieties
    "kidney beans", "black beans", "garbanzo beans",
    # Grains
    "quinoa"
]

# Simple in-memory cache for recipe lookups
CACHE = {}
CACHE_TTL = 600  # 10 minutes

def get_pantry():
    if 'pantry' not in session:
        session['pantry'] = DEFAULT_PANTRY.copy()
    return session['pantry']

def get_profiles():
    if 'pantry_profiles' not in session:
        session['pantry_profiles'] = {}
    return session['pantry_profiles']

def get_cache_key(params):
    # Use a tuple of sorted params for a stable key
    return tuple(sorted(params.items()))

@app.route('/save_profile', methods=['POST'])
def save_profile():
    profile_name = request.form.get('profile_name', '').strip()
    if profile_name:
        profiles = get_profiles()
        profiles[profile_name] = get_pantry().copy()
        session['pantry_profiles'] = profiles
    return redirect(url_for('index'))

@app.route('/load_profile', methods=['POST'])
def load_profile():
    profile_name = request.form.get('profile_to_load', '').strip()
    profiles = get_profiles()
    if profile_name in profiles:
        session['pantry'] = profiles[profile_name].copy()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    error = None
    used_ingredients = []
    pantry = get_pantry()
    profiles = get_profiles()
    if request.method == 'POST' and request.form.get('form_type') == 'ingredients':
        ingredients = request.form.get('ingredients', '')
        diet = request.form.get('diet', '')
        cuisine = request.form.get('cuisine', '')
        meal_type = request.form.get('type', '')
        max_time = request.form.get('max_time', '')
        pantry_for_search = request.form.get('pantry_for_search', '')
        # Combine user ingredients with checked pantry items
        user_ingredients = [i.strip() for i in ingredients.split(',') if i.strip()]
        pantry_checked = [i.strip() for i in pantry_for_search.split(',') if i.strip()]
        all_ingredients = list(set(user_ingredients + pantry_checked))
        used_ingredients = all_ingredients
        if all_ingredients:
            try:
                params = {
                    'ingredients': ','.join(all_ingredients),
                    'number': 5,
                    'apiKey': SPOONACULAR_API_KEY
                }
                if diet:
                    params['diet'] = diet
                if cuisine:
                    params['cuisine'] = cuisine
                if meal_type:
                    params['type'] = meal_type
                if max_time:
                    params['maxReadyTime'] = max_time
                cache_key = get_cache_key(params)
                now = time.time()
                if cache_key in CACHE and now - CACHE[cache_key]['time'] < CACHE_TTL:
                    recipes = CACHE[cache_key]['data']
                else:
                    response = requests.get(
                        'https://api.spoonacular.com/recipes/findByIngredients',
                        params=params
                    )
                    response.raise_for_status()
                    recipes_basic = response.json()
                    # Fetch more details for each recipe
                    recipes = []
                    for r in recipes_basic:
                        details = {}
                        try:
                            details_resp = requests.get(
                                f'https://api.spoonacular.com/recipes/{r["id"]}/information',
                                params={
                                    'includeNutrition': 'true',
                                    'apiKey': SPOONACULAR_API_KEY
                                }
                            )
                            details_resp.raise_for_status()
                            details = details_resp.json()
                        except Exception:
                            details = {}
                        r['details'] = details
                        recipes.append(r)
                    CACHE[cache_key] = {'data': recipes, 'time': now}
            except Exception as e:
                error = str(e)
    return render_template('index.html', recipes=recipes, error=error, used_ingredients=used_ingredients, pantry=pantry, profiles=profiles)

@app.route('/update_pantry', methods=['POST'])
def update_pantry():
    pantry_items = request.form.get('pantry_items', '')
    pantry = [i.strip() for i in pantry_items.split(',') if i.strip()]
    session['pantry'] = pantry
    return redirect(url_for('index'))

@app.route('/autocomplete_ingredient')
def autocomplete_ingredient():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    try:
        resp = requests.get(
            'https://api.spoonacular.com/food/ingredients/autocomplete',
            params={
                'query': q,
                'number': 8,
                'apiKey': SPOONACULAR_API_KEY
            }
        )
        resp.raise_for_status()
        suggestions = [item['name'] for item in resp.json()]
        return jsonify(suggestions)
    except Exception:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True) 