# Image Composer Service

Service Flask pour composer des images d'avatars avec des produits.

## Déploiement sur Railway

1. Va sur https://railway.app
2. Clique sur "Start a New Project"
3. Choisis "Deploy from GitHub repo" (ou "Empty Project")
4. Si Empty Project :
   - Clique sur "New" → "Empty Service"
   - Dans Settings, ajoute ces fichiers :
     - app.py
     - requirements.txt
     - Procfile
5. Railway détectera automatiquement Python et déploiera l'app
6. Une fois déployé, tu auras une URL publique (ex: https://ton-app.railway.app)

## Test de l'API

Endpoint: POST https://ton-app.railway.app/compose

Body JSON:
```json
{
  "avatar_url": "https://example.com/avatar.png",
  "product_url": "https://example.com/product.png"
}
```

Retourne: Image JPEG composée

## Usage dans N8N

Ajouter un node HTTP Request après Nano Banana:
- Method: POST
- URL: https://ton-app.railway.app/compose
- Body: JSON avec avatar_url et product_url
- Le response sera l'image composée
