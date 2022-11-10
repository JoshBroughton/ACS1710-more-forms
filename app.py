"""
app.py is a Flask server with routes to forms which compliment the user,
dish some sweet animal facts, apply filter to user uploaded images,
and search for gifs using the tenor GIF API
"""
import os
import json
import random

from PIL import Image, ImageFilter
from dotenv import load_dotenv
import requests
from flask import Flask, request, render_template


load_dotenv()


app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    num_compliments = int(request.args.get('num_compliments'))
    compliment_list = random.sample(list_of_compliments, k=num_compliments)
    context = {
        'users_name': request.args.get('users_name'),
        'wants_compliments': request.args.get('wants_compliments'),
        'num_compliments': num_compliments,
        'compliment_list': compliment_list
    }

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.',
    'chameleon': 'A chameleon\'s tongue is as long as its body.',
    'humingbird': 'Humminbirds wings flap at up to 200 beats per second.',
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""
    chosen_animal_facts = []
    chosen_animals = request.args.getlist('animal')
    if chosen_animals:
        for animal in chosen_animals:
            chosen_animal_facts.append(animal_to_fact[animal])
    else:
        chosen_animal_facts.append('Please choose some animals from the drop down!')

    context = {
        'list_of_animals': animal_to_fact.keys(),
        'chosen_animal_facts': chosen_animal_facts,
        'chosen_animals': chosen_animals,
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == 'POST':
        filter_type = request.form.get('filter_type')
        image = request.files.get('users_image')
        image_file_path = save_image(image, filter_type)
        apply_filter(image_file_path, filter_type)

        image_url = f'./static/images/{image.filename}'

        context = {
            'filter_types': filter_types,
            'image_url': image_url,
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            'filter_types': filter_types_dict.keys(),
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################
API_KEY = os.getenv('API_KEY')
#altered url to use tenor API v2 with a google developer API
TENOR_URL = 'https://tenor.googleapis.com/v2/search'


@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        limit = request.form.get('quantity')
        #added timout to get rid of pylint squigglies
        response = requests.get(TENOR_URL, {
            'q': search_query,
            'key': API_KEY,
            'limit': limit,
            }, timeout=5.0)
        #get the results object of the response
        gifs = json.loads(response.content)['results']

        context = {
            'gifs': gifs,
        }

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
