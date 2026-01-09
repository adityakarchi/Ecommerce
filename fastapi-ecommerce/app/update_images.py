import json
import random

# Load the products
with open('data/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Extensive image library with unique images for each brand and category
laptop_images = [
    'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500',
    'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500',
    'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500',
    'https://images.unsplash.com/photo-1593642532400-2682810df593?w=500',
    'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=500',
    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500',
    'https://images.unsplash.com/photo-1526657782461-9fe13402a841?w=500',
    'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
    'https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=500',
    'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500',
    'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500',
    'https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=500',
    'https://images.unsplash.com/photo-1602080858428-57174f9431cf?w=500',
    'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=500',
    'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=500',
    'https://images.unsplash.com/photo-1619252584172-a83a949b6efd?w=500',
]

mobile_images = [
    'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500',
    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
    'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=500',
    'https://images.unsplash.com/photo-1611472173362-3f53dbd65d80?w=500',
    'https://images.unsplash.com/photo-1565849904461-04ec9f2fa0f5?w=500',
    'https://images.unsplash.com/photo-1592286927505-b0e0dd0a5e49?w=500',
    'https://images.unsplash.com/photo-1611791483458-6da70a21c1d8?w=500',
    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500',
    'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500',
    'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500',
    'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500',
    'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500',
    'https://images.unsplash.com/photo-1605236453806-6ff36851218e?w=500',
    'https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=500',
    'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=500',
]

electronics_images = [
    'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=500',
    'https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=500',
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500',
    'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500',
    'https://images.unsplash.com/photo-1572635196243-4dd75fbdbd7f?w=500',
    'https://images.unsplash.com/photo-1563203369-26f2e4a5ccf7?w=500',
    'https://images.unsplash.com/photo-1585790050230-5dd28404f80a?w=500',
    'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=500',
    'https://images.unsplash.com/photo-1560343090-f0409e92791a?w=500',
]

tablet_images = [
    'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500',
    'https://images.unsplash.com/photo-1585790050230-5dd28404f80a?w=500',
    'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500',
    'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500',
    'https://images.unsplash.com/photo-1527698266440-12104e498b76?w=500',
    'https://images.unsplash.com/photo-1527698266440-12104e498b76?w=500',
    'https://images.unsplash.com/photo-1527698266440-12104e498b76?w=500',
    'https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=500',
]

# Category to image pool mapping
category_images = {
    'laptops': laptop_images,
    'mobiles': mobile_images,
    'electronics': electronics_images,
    'tablets': tablet_images
}

# Track used images to maximize variety
used_images = set()

# Update each product with unique images
for idx, product in enumerate(products):
    category = product.get('category', 'electronics')
    
    # Get the appropriate image pool for this category
    image_pool = category_images.get(category, electronics_images)
    
    # Create a pool of available images (not yet used for this product)
    available_images = [img for img in image_pool if img not in used_images]
    
    # If we've used most images, reset the used set but keep some variety
    if len(available_images) < 2:
        used_images.clear()
        available_images = image_pool.copy()
    
    # Randomly select 2-3 unique images for this product
    num_images = random.choice([2, 3])
    selected_images = random.sample(available_images, min(num_images, len(available_images)))
    
    product['image_urls'] = selected_images
    
    # Mark these images as used (to avoid immediate repetition)
    for img in selected_images[:1]:  # Only mark first image to allow some reuse
        used_images.add(img)

# Save updated products
with open('data/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"✅ Updated images for {len(products)} products!")
