# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
from typing import List, Dict, Optional
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="E-Commerce Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .product-title {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    .product-price {
        font-size: 24px;
        color: #e74c3c;
        font-weight: bold;
    }
    .discount-badge {
        background-color: #e74c3c;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
    }
    .rating {
        color: #f39c12;
        font-size: 18px;
    }
    .stock-available {
        color: #27ae60;
        font-weight: bold;
    }
    .stock-low {
        color: #e67e22;
        font-weight: bold;
    }
    .stock-out {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def fetch_products(name: Optional[str] = None, 
                   sort_by_price: bool = False,
                   order: str = "asc",
                   limit: int = 100,
                   offset: int = 0) -> Dict:
    """Fetch products from FastAPI backend"""
    try:
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by_price": sort_by_price,
            "order": order
        }
        if name:
            params["name"] = name
        
        response = requests.get(f"{API_BASE_URL}/products", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching products: {str(e)}")
        return {"total": 0, "items": []}

def fetch_product_by_id(product_id: str) -> Optional[Dict]:
    """Fetch a single product by ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching product: {str(e)}")
        return None

def calculate_discounted_price(price: float, discount: float) -> float:
    """Calculate price after discount"""
    return price * (1 - discount / 100)

def get_stock_status(stock: int) -> tuple:
    """Return stock status and CSS class"""
    if stock == 0:
        return "Out of Stock", "stock-out"
    elif stock < 10:
        return f"Only {stock} left!", "stock-low"
    else:
        return f"In Stock ({stock} available)", "stock-available"

def display_product_card(product: Dict):
    """Display a product card"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display product image
        if product.get("image_urls") and len(product["image_urls"]) > 0:
            st.image(product["image_urls"][0])
        else:
            st.image("https://via.placeholder.com/300x300?text=No+Image")
    
    with col2:
        # Product name and brand
        st.markdown(f"<div class='product-title'>{product['name']}</div>", unsafe_allow_html=True)
        st.write(f"**Brand:** {product.get('brand', 'N/A')}")
        st.write(f"**Category:** {product.get('category', 'N/A')}")
        
        # Rating
        rating = product.get('rating', 0)
        st.markdown(f"<span class='rating'>{'⭐' * int(rating)} {rating}/5</span>", unsafe_allow_html=True)
        
        # Price and discount
        price = product.get('price', 0)
        discount = product.get('discount_percent', 0)
        
        if discount > 0:
            discounted_price = calculate_discounted_price(price, discount)
            st.markdown(f"<span class='product-price'>₹{discounted_price:,.2f}</span> "
                       f"<span style='text-decoration: line-through; color: #999;'>₹{price:,.2f}</span> "
                       f"<span class='discount-badge'>{discount}% OFF</span>", 
                       unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='product-price'>₹{price:,.2f}</span>", unsafe_allow_html=True)
        
        # Stock status
        stock = product.get('stock', 0)
        stock_text, stock_class = get_stock_status(stock)
        st.markdown(f"<span class='{stock_class}'>{stock_text}</span>", unsafe_allow_html=True)
        
        # Tags
        if product.get('tags'):
            tags_html = " ".join([f"<span style='background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; margin: 2px; font-size: 12px;'>{tag}</span>" 
                                  for tag in product['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        # View details button
        if st.button("View Details", key=f"btn_{product['id']}"):
            st.session_state.selected_product_id = product['id']
            st.session_state.page = "product_detail"
            st.rerun()

def product_listing_page():
    """Main product listing page"""
    st.title("🛒 E-Commerce Store")
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Search & Filters")
        
        # Search box
        search_query = st.text_input("Search products", placeholder="Enter product name...")
        
        # Category filter (placeholder - you can enhance this)
        st.subheader("Categories")
        categories = ["All", "mobiles", "laptops", "electronics", "tablets"]
        selected_category = st.selectbox("Select Category", categories)
        
        # Price sorting
        st.subheader("Sort By")
        sort_by_price = st.checkbox("Sort by Price")
        if sort_by_price:
            order = st.radio("Order", ["Ascending", "Descending"])
            order_value = "asc" if order == "Ascending" else "desc"
        else:
            order_value = "asc"
        
        # Price range filter (placeholder)
        st.subheader("Price Range")
        price_range = st.slider("Select price range (₹)", 0, 200000, (0, 200000), step=1000)
        
        # Clear filters button
        if st.button("Clear Filters"):
            st.session_state.clear()
            st.rerun()
    
    # Fetch products
    with st.spinner("Loading products..."):
        data = fetch_products(
            name=search_query if search_query else None,
            sort_by_price=sort_by_price,
            order=order_value if sort_by_price else "asc",
            limit=100
        )
    
    products = data.get("items", [])
    total = data.get("total", 0)
    
    # Filter by category (client-side)
    if selected_category != "All":
        products = [p for p in products if p.get("category") == selected_category]
    
    # Filter by price range (client-side)
    products = [p for p in products if price_range[0] <= p.get("price", 0) <= price_range[1]]
    
    # Display results
    st.subheader(f"Found {len(products)} products")
    
    if not products:
        st.info("No products found. Try adjusting your filters.")
    else:
        # Display products in a grid
        for product in products:
            with st.container():
                display_product_card(product)
                st.divider()

def product_detail_page():
    """Product detail page"""
    if "selected_product_id" not in st.session_state:
        st.error("No product selected")
        if st.button("← Back to Products"):
            st.session_state.page = "listing"
            st.rerun()
        return
    
    product_id = st.session_state.selected_product_id
    
    # Back button
    if st.button("← Back to Products"):
        st.session_state.page = "listing"
        st.rerun()
    
    # Fetch product details
    with st.spinner("Loading product details..."):
        product = fetch_product_by_id(product_id)
    
    if not product:
        st.error("Product not found")
        return
    
    # Product details layout
    st.title(product['name'])
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Image gallery
        if product.get("image_urls") and len(product["image_urls"]) > 0:
            selected_image = st.selectbox("View Images", range(len(product["image_urls"])), 
                                         format_func=lambda x: f"Image {x+1}")
            st.image(product["image_urls"][selected_image])
        else:
            st.image("https://via.placeholder.com/500x500?text=No+Image")
    
    with col2:
        # Product info
        st.subheader(f"Brand: {product.get('brand', 'N/A')}")
        st.write(f"**Category:** {product.get('category', 'N/A')}")
        st.write(f"**SKU:** {product.get('sku', 'N/A')}")
        
        # Rating
        rating = product.get('rating', 0)
        st.markdown(f"<span class='rating'>{'⭐' * int(rating)} {rating}/5</span>", unsafe_allow_html=True)
        
        # Price
        price = product.get('price', 0)
        discount = product.get('discount_percent', 0)
        
        if discount > 0:
            discounted_price = calculate_discounted_price(price, discount)
            st.markdown(f"<div style='font-size: 32px;'>"
                       f"<span class='product-price'>₹{discounted_price:,.2f}</span> "
                       f"<span style='text-decoration: line-through; color: #999; font-size: 20px;'>₹{price:,.2f}</span> "
                       f"<span class='discount-badge'>{discount}% OFF</span>"
                       f"</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='product-price'>₹{price:,.2f}</span>", unsafe_allow_html=True)
        
        # Stock status
        stock = product.get('stock', 0)
        stock_text, stock_class = get_stock_status(stock)
        st.markdown(f"<span class='{stock_class}'>{stock_text}</span>", unsafe_allow_html=True)
        
        # Add to cart button (placeholder)
        st.button("🛒 Add to Cart", type="primary", disabled=(stock == 0))
        
        # Description
        st.subheader("Description")
        st.write(product.get('description', 'No description available'))
        
        # Tags
        if product.get('tags'):
            st.subheader("Tags")
            tags_html = " ".join([f"<span style='background-color: #3498db; color: white; padding: 5px 10px; border-radius: 5px; margin: 5px; display: inline-block;'>{tag}</span>" 
                                  for tag in product['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)
    
    # Additional details in tabs
    tab1, tab2, tab3 = st.tabs(["📐 Dimensions", "🏪 Seller Info", "ℹ️ Additional Info"])
    
    with tab1:
        if product.get('dimensions_cm'):
            dims = product['dimensions_cm']
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Length", f"{dims.get('length', 0)} cm")
            col2.metric("Width", f"{dims.get('width', 0)} cm")
            col3.metric("Height", f"{dims.get('height', 0)} cm")
            if 'volume_cm3' in dims:
                col4.metric("Volume", f"{dims['volume_cm3']} cm³")
    
    with tab2:
        if product.get('seller'):
            seller = product['seller']
            st.write(f"**Seller Name:** {seller.get('name', 'N/A')}")
            st.write(f"**Email:** {seller.get('email', 'N/A')}")
            st.write(f"**Website:** {seller.get('website', 'N/A')}")
            st.write(f"**Seller ID:** {seller.get('seller_id', 'N/A')}")
    
    with tab3:
        st.write(f"**Product ID:** {product['id']}")
        st.write(f"**Currency:** {product.get('currency', 'N/A')}")
        st.write(f"**Active Status:** {'✅ Active' if product.get('is_active') else '❌ Inactive'}")
        if product.get('created_at'):
            st.write(f"**Created At:** {product['created_at']}")

def main():
    """Main application"""
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "listing"
    
    # Navigation
    if st.session_state.page == "listing":
        product_listing_page()
    elif st.session_state.page == "product_detail":
        product_detail_page()

if __name__ == "__main__":
    main()