from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Product

products_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')

@products_bp.route('/', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id')
    query = Product.query.filter_by(active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    products = query.all()
    
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': p.price,
            'stock': p.stock,
            'image_url': p.image_url,
            'category_id': p.category_id
        })
    return jsonify(result), 200

@products_bp.route('/<slug>', methods=['GET'])
def get_product(slug):
    p = Product.query.filter_by(slug=slug, active=True).first_or_404()
    return jsonify({
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': p.price,
        'stock': p.stock,
        'description': p.description,
        'image_url': p.image_url,
        'category_id': p.category_id
    }), 200

@products_bp.route('/', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data.get('name'),
        slug=data.get('slug'),
        sku=data.get('sku') if data.get('sku') else None,
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        image_url=data.get('image_url'),
        category_id=data.get('category_id')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'id': new_product.id, 'name': new_product.name, 'slug': new_product.slug}), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    p = Product.query.get_or_404(product_id)
    data = request.get_json()
    p.name = data.get('name', p.name)
    p.slug = data.get('slug', p.slug)
    p.price = data.get('price', p.price)
    p.stock = data.get('stock', p.stock)
    p.image_url = data.get('image_url', p.image_url)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
