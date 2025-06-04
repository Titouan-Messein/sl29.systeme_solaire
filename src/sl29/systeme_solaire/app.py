"""Un module pour l'application"""

import json
from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import FileField, HiddenField, SubmitField
from flask_wtf.file import FileAllowed
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'une-cle-secrete-a-changer'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class ImageUploadForm(FlaskForm):
    id = HiddenField()
    image = FileField('Importer une image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images seulement !')])
    submit = SubmitField('Envoyer')

# Chargement des données
with open('src/sl29/systeme_solaire/data/planets.json', 'r', encoding='utf-8') as f:
    PLANETS = json.load(f)

with open('src/sl29/systeme_solaire/data/satellites.json', 'r', encoding='utf-8') as f:
    SATELLITES = json.load(f)

@app.route('/')
def index():
    """Page d'accueil montrant comment les paramètres fonctionnent"""
    return render_template('index.html', planets=PLANETS)

@app.route('/planete')
def show_planet():
    """Démontre l'utilisation de request.args.get()"""
    # Récupération du paramètre 'id' de la requête
    planet_id = request.args.get('id', type=int)

    # Vérification si le paramètre existe et est valide
    if planet_id is None:
        return "Erreur: Le paramètre 'id' est requis. Exemple: /planete?id=3", 400

    # Recherche de la planète
    planet_data = get_planet_by_id(planet_id)
    image_url = get_image_url(planet_id)
    if not planet_data:
        return f"Erreur: Aucune planète trouvée avec l'ID {planet_id}", 404

    # Récupération des satellites
    planet_satellites = [s for s in SATELLITES if s['planetId'] == planet_id]

    return render_template('planet.html',
                         planet=planet_data,
                         satellites=planet_satellites,
                         request_args=dict(request.args))  # Pour démo pédagogique

@app.route('/planete/upload_image', methods=['POST'])
def upload_image():
    form = ImageUploadForm()
    print("Validate:", form.validate())
    print("Errors:", form.errors)
    if form.validate_on_submit():
        file = form.image.data
        planet_id = int(form.id.data)

        filename = secure_filename(file.filename)
        name, extension = filename.split(".")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"planet_{planet_id}.{extension}")
        file.save(filepath)

        planet = get_planet_by_id(planet_id)
        if planet:
            planet['image'] = filepath

        return redirect(f"/planete?id={planet_id}")
    
    return "Formulaire invalide", 400

@app.route('/planete/edit', methods=['GET', 'POST'])
def edit_planet():
    planet_id = request.args.get('id', type=int)
    if planet_id is None:
        return "Erreur: Le paramètre 'id' est requis.", 400

    planet_data = get_planet_by_id(planet_id)
    if not planet_data:
        return f"Erreur: Aucune planète trouvée avec l'ID {planet_id}", 404

    form = ImageUploadForm()
    form.id.data = planet_id

    return render_template('planet_edit.html', planet=planet_data, form=form)

@app.route('/satellite')
def show_satellite():
    """Montre comment gérer plusieurs paramètres"""

    # A FAIRE

    satellite_id = request.args.get('id', type=int)

    if satellite_id is None:
        return "Erreur", 404

    # Récuperer les données du satellite
    sat = get_satellite_by_id(satellite_id)
    # Si aucune donnée trouvée, retourner un message d'erreur et un status 404
    if not sat:
        return "Erreur", 404

    # récupérer les données de la planète associée.
    planet_id = sat.get("planetId")
    planet = get_planet_by_id(planet_id)

    # retourner le template 'satellite.html' avec les variables:
    # - satellite
    # - planet
    return render_template('satellite.html',
                        satellite=sat,
                         planet=planet)


def get_planet_by_id(planet_id:int)->dict|None:
    """Retourne la planète sous forme de dictionnaire

    :param planet_id: l'id de la planète
    :type planet_id: int
    :return:la planète ou None
    :rtype: dict|None
    """
    for planet in PLANETS:
        if planet['id'] == planet_id:
            return planet
    return None  # Si aucune planète trouvée

def get_satellite_by_id(satellite_id:int)->dict|None:
    """Retourne la planète sous forme de dictionnaire

    :param planet_id: l'id de la planète
    :type planet_id: int
    :return:la planète ou None
    :rtype: dict|None
    """
    for satellite in SATELLITES:
        if satellite['id'] == satellite_id:
            return satellite
    return None  # Si aucun satellite trouvée

def get_image_url(planet_id: int) -> str:
    """Retourne le chemin relatif de l'image si elle existe, sinon une chaîne vide.

    :param planet_id: l'ID de la planète
    :type planet_id: int
    :return: le chemin relatif vers l'image ou une chaîne vide
    :rtype: str
    """
    # Nom de fichier attendu
    filename = f"uploads/planet_{planet_id}.png"

    # Chemin absolu sur le système de fichiers
    full_path = os.path.join('static', filename)

    if os.path.exists(full_path):
        return filename  # on retourne le chemin relatif à 'static'
    return ""

if __name__ == '__main__':
    app.run(debug=True)