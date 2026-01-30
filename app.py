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
        
        avatar_img = Image.open(BytesIO(avatar_response.content)).convert('RGBA')
        product_img = Image.open(BytesIO(product_response.content)).convert('RGBA')
        
        # Créer l'image finale (format 9:16 pour TikTok)
        width, height = 720, 1280
        composed = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        
        # Avatar en pleine image
        avatar_resized = avatar_img.resize((width, height))
        composed.paste(avatar_resized, (0, 0), avatar_resized if avatar_resized.mode == 'RGBA' else None)
        
        # Produit superposé au centre (35% de la largeur)
        product_width = int(width * 0.35)
        product_height = int(product_width * product_img.height / product_img.width)
        product_resized = product_img.resize((product_width, product_height))
        
        # Position : centre horizontal, 60% de la hauteur (zone des mains)
        x = (width - product_width) // 2
        y = int(height * 0.6) - (product_height // 2)
        
        # Coller le produit avec transparence
        composed.paste(product_resized, (x, y), product_resized if product_resized.mode == 'RGBA' else None)
        
        # Convertir en RGB pour JPEG
        final = Image.new('RGB', (width, height), (255, 255, 255))
        final.paste(composed, (0, 0), composed if composed.mode == 'RGBA' else None)
        
        # Générer un nom de fichier unique
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(COMPOSED_DIR, filename)
        
        # Sauvegarder l'image
        final.save(filepath, 'JPEG', quality=95)
        
        # Construire l'URL publique
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
