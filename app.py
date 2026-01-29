from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import requests
from io import BytesIO
import os
import uuid

app = Flask(__name__)

# Créer le dossier pour stocker les images composées
COMPOSED_DIR = os.path.join('static', 'composed')
os.makedirs(COMPOSED_DIR, exist_ok=True)

@app.route('/compose', methods=['POST'])
def compose_images():
    try:
        data = request.json
        avatar_url = data.get('avatar_url')
        product_url = data.get('product_url')
        
        if not avatar_url or not product_url:
            return jsonify({'error': 'Missing avatar_url or product_url'}), 400
        
        # Télécharger les images
        avatar_response = requests.get(avatar_url)
        product_response = requests.get(product_url)
        
        avatar_img = Image.open(BytesIO(avatar_response.content))
        product_img = Image.open(BytesIO(product_response.content))
        
        # Redimensionner les images à 512x512
        avatar_img = avatar_img.resize((512, 512))
        product_img = product_img.resize((512, 512))
        
        # Créer une nouvelle image 720x512 (70% avatar + 30% produit)
        composed = Image.new('RGB', (720, 512))
        
        # Avatar : 70% de la largeur (504 pixels)
        avatar_resized = avatar_img.resize((504, 512))
        composed.paste(avatar_resized, (0, 0))
        
        # Produit : 30% de la largeur (216 pixels)
        product_resized = product_img.resize((216, 512))
        composed.paste(product_resized, (504, 0))
        
        # Générer un nom de fichier unique
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(COMPOSED_DIR, filename)
        
        # Sauvegarder l'image
        composed.save(filepath, 'JPEG', quality=95)
        
        # Construire l'URL publique
        # Railway injecte la variable PORT, on utilise l'URL du service
        base_url = request.host_url.rstrip('/')
        image_url = f"{base_url}/static/composed/{filename}"
        
        return jsonify({'composed_image_url': image_url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/composed/<filename>')
def serve_composed_image(filename):
    return send_from_directory(COMPOSED_DIR, filename)

@app.route('/')
def home():
    return jsonify({'status': 'Image Composer Service is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
