from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Category

categories_bp = Blueprint('categories', __name__, url_prefix='/api/v1/categories')

@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by(active=True).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in categories]), 200

@categories_bp.route('/', methods=['POST'])
def create_category():
    data = request.get_json()
    new_category = Category(name=data.get('name'), slug=data.get('slug'))
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'id': new_category.id, 'name': new_category.name, 'slug': new_category.slug}), 201
