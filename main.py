# main.py
import shopify
import json
from config import SHOPIFY_API_KEY, SHOPIFY_API_PASSWORD, SHOPIFY_STORE_URL

# Initialize the Shopify API
shop_url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_API_PASSWORD}@{SHOPIFY_STORE_URL}/admin"
shopify.ShopifyResource.set_site(shop_url)

def test_api_connection():
    try:
        products = shopify.Product.find(limit=1)
        if products:
            print("Connection successful. Product found:", products[0].title)
        else:
            print("Connection successful. No products found.")
    except Exception as e:
        print(f"Error: {e}")

# Test the API connection
# test_api_connection()

def get_all_products():
    all_products = []
    page = 1
    products = shopify.Product.find(limit=250)

    while products:
        for product in products:
            product_data = {
                "id": product.id,
                "title": product.title,
                "variants": [variant.to_dict() for variant in product.variants],
                "price": product.variants[0].price if product.variants else None,
                "collections": [collection.title for collection in product.collections()],
                "content": product.body_html,
                "featured_image": product.image.src if product.image else None,
                "handle": product.handle,
                "images_count": len(product.images),
                "tags": product.tags,
                "type": product.product_type,
                "url": f"https://{SHOPIFY_STORE_URL}/products/{product.handle}"
            }
            all_products.append(product_data)

        print(f"Fetched page {page} with {len(products)} products.")
        page += 1
        try:
            products = products.next_page()
        except Exception as e:
            print(f"Failed to fetch next page: {e}")
            break

    return all_products

def get_all_custom_collections():
    all_custom_collections = []
    page = 1
    custom_collections = shopify.CustomCollection.find(limit=250)

    while True:
        for collection in custom_collections:
            # Fetching products for each collection might require additional API calls
            collection_products = shopify.Product.find(collection_id=collection.id)

            # for the products array
            products_info = [{
                "id": product.id,
                "title": product.title,
                "handle": product.handle
            } for product in collection_products]

            # Ensure to handle collections without images
            featured_image = None
            if hasattr(collection, 'featured_image') and collection.image:
                featured_image = collection.image.src

            collection_data = {
                "id": collection.id,
                "title": collection.title,
                "handle": collection.handle,
                "all_products_count": len(collection_products),
                "featured_image": featured_image,
                # "all_tags": list(set(tag for product in collection_products for tag in product.tags)),
                # "all_types": list(set(product.product_type for product in collection_products)),
                "description": collection.body_html,
                "products_count": len(collection_products),
                "url": f"https://{SHOPIFY_STORE_URL}/collections/{collection.handle}",
                "products": products_info  # Adding the array of products
            }
            all_custom_collections.append(collection_data)

        print(f"Fetched page {page} with {len(custom_collections)} custom collections.")
        page += 1

        # Check if there is a next page
        if not custom_collections.has_next_page():
            break

        try:
            custom_collections = custom_collections.next_page()
        except Exception as e:
            print(f"Failed to fetch next page: {e}")
            break

    return all_custom_collections

def export_data(data, filename='shopify_data_map.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data exported to {filename}")

# uncomment to fetch prorduct data
# all_products_data = get_all_products()
# export_data(all_products_data, 'all_products_data.json')

# uncomment to fetch collections data
custom_collections_data = get_all_custom_collections()
export_data(custom_collections_data, 'custom_collections.json')
# smart_collections_data = get_all_smart_collections()
# export_data(smart_collections_data, 'smart_collections.json')

# Potential further functions to create
# get_all_customers()
# get_all_orders()
# get_all_pages()
# get_all_blogs_and_articles()
