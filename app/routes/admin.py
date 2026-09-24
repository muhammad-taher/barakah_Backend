from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Product, Order, Category

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'Completed').scalar() or 0
    total_products = Product.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    processing_orders = Order.query.filter_by(status='Processing').count()
    
    return jsonify({
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders
    }), 200

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    from app.models.core import OrderItem, Product
    orders = Order.query.order_by(Order.created_at.desc()).all()
    result = []
    for o in orders:
        items = OrderItem.query.filter_by(order_id=o.id).all()
        items_data = []
        for item in items:
            product = Product.query.get(item.product_id)
            items_data.append({
                'product_name': product.name if product else 'Unknown Product',
                'quantity': item.quantity,
                'unit_price': item.unit_price
            })
            
        result.append({
            'id': o.id,
            'order_number': o.order_number,
            'customer_name': o.customer_name,
            'phone': o.phone,
            'address': o.address,
            'total_amount': o.total_amount,
            'status': o.status,
            'created_at': o.created_at.isoformat(),
            'items': items_data
        })
    return jsonify(result), 200

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'}), 200

@admin_bp.route('/orders/bulk-status', methods=['PUT'])
@jwt_required()
def update_bulk_order_status():
    data = request.get_json()
    order_ids = data.get('order_ids', [])
    new_status = data.get('status')
    
    if not order_ids or not new_status:
        return jsonify({'message': 'Missing order_ids or status'}), 400
        
    Order.query.filter(Order.id.in_(order_ids)).update({'status': new_status}, synchronize_session=False)
    db.session.commit()
    
    return jsonify({'message': f'Status updated to {new_status} for {len(order_ids)} orders'}), 200

