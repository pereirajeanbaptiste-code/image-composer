from flask import Flask, request, jsonify, send_file
from PIL import Image
import requests
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/compose', methods=['POST'])
def compose_images():
    try:
        data = request.json
        avatar_url = data.get('avatar_url')
        product_url = data.get('product_url')
        
        if not avatar_url or not product_url:
            return jsonify({"error": "avatar_url and product_url required"}), 400
        
        # Télécharge les images
        avatar_response = requests.get(avatar_url, timeout=10)
        product_response = requests.get(product_url, timeout=10)
        
        avatar_img = Image.open(BytesIO(avatar_response.content)).convert('RGBA')
        product_img = Image.open(BytesIO(product_response.content)).convert('RGBA')
        
        # Dimensions cible (format TikTok 9:16)
        target_width = 1080
        target_height = 1920
        
        # Avatar occupe 70% de la largeur (gauche)
        avatar_width = int(target_width * 0.7)
        avatar_img_resized = avatar_img.resize((avatar_width, target_height), Image.Resampling.LANCZOS)
        
        # Produit occupe 30% de la largeur (droite)
        product_width = int(target_width * 0.3)
        # Garde ratio du produit
        product_ratio = product_img.height / product_img.width
        product_height = int(product_width * product_ratio)
        
        # Limite la hauteur du produit à 80% de la hauteur totale
        max_product_height = int(target_height * 0.8)
        if product_height > max_product_height:
            product_height = max_product_height
            product_width = int(product_height / product_ratio)
        
        product_img_resized = product_img.resize((product_width, product_height), Image.Resampling.LANCZOS)
        
        # Crée le canvas final
        composed = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 255))
        
        # Place avatar à gauche
        composed.paste(avatar_img_resized, (0, 0), avatar_img_resized)
        
        # Place produit à droite, centré verticalement
        product_y = (target_height - product_height) // 2
        product_x = avatar_width + (target_width - avatar_width - product_width) // 2
        composed.paste(product_img_resized, (product_x, product_y), product_img_resized)
        
        # Convertit en RGB (enlève alpha pour JPEG)
        composed_rgb = Image.new('RGB', composed.size, (255, 255, 255))
        composed_rgb.paste(composed, mask=composed.split()[3])
        
        # Sauvegarde en mémoire
        img_io = BytesIO()
        composed_rgb.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
