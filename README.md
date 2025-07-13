# Pantry Recipe Finder

A web app to suggest recipes based on your pantry and fridge items, with filtering, pantry profiles, and more.

## Features
- Enter ingredients with tag-style input and autocomplete
- Always-in-pantry items, editable and toggleable per search
- Save/load pantry profiles (e.g., Home, Vacation)
- Recipe filtering (diet, cuisine, meal type, max prep time)
- Recipe cards with images, prep time, servings, summary, nutrition
- Caching for fast repeated searches

## Deployment

### Render (recommended for free hosting)
1. Create a free account at [Render.com](https://render.com/)
2. Create a new Web Service, connect your repo, and set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variable:** `SPOONACULAR_API_KEY` (your API key)
3. Deploy and visit your app URL!

### Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Run:
   ```sh
   heroku create
   heroku config:set SPOONACULAR_API_KEY=your_api_key_here
   git push heroku main
   ```
3. Open your app with `heroku open`

### PythonAnywhere
1. Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your files, set up a Flask web app, and set the environment variable for your API key.

## Local Development
```sh
pip install -r requirements.txt
python app.py
```
Visit [http://localhost:5000](http://localhost:5000) 