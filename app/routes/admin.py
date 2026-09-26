from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Product, Order, Category
from app.services.steadfast import create_consignment, check_status_by_consignment_id
import logging

logger = logging.getLogger(__name__)

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
            'items': items_data,
            'steadfast_consignment_id': o.steadfast_consignment_id,
            'steadfast_tracking_code': o.steadfast_tracking_code,
            'steadfast_status': o.steadfast_status
        })
    return jsonify(result), 200


def _handle_steadfast_for_order(order):
    """
    If the order is being set to Processing and doesn't have a consignment yet,
    create one via SteadFast API.
    Returns (success: bool, error_message: str or None)
    """
    if order.steadfast_consignment_id:
        # Already has a consignment, skip
        return True, None
    
    try:
        consignment_id, tracking_code, status = create_consignment(order)
        order.steadfast_consignment_id = consignment_id
        order.steadfast_tracking_code = tracking_code
        order.steadfast_status = status
        return True, None
    except Exception as e:
        logger.error(f"Failed to create SteadFast consignment for order {order.order_number}: {e}")
        return False, str(e)


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    order = Order.query.get_or_404(order_id)
    
    old_status = order.status
    order.status = new_status
    
    steadfast_error = None
    # When switching to Processing, auto-create SteadFast consignment
    if new_status == 'Processing' and old_status != 'Processing':
        success, error = _handle_steadfast_for_order(order)
        if not success:
            steadfast_error = error
    
    db.session.commit()
    
    response = {'message': 'Status updated successfully'}
    if steadfast_error:
        response['steadfast_error'] = steadfast_error
        response['message'] = 'Status updated but SteadFast consignment creation failed'
    
    return jsonify(response), 200

@admin_bp.route('/orders/bulk-status', methods=['PUT'])
@jwt_required()
def update_bulk_order_status():
    data = request.get_json()
    order_ids = data.get('order_ids', [])
    new_status = data.get('status')
    
    if not order_ids or not new_status:
        return jsonify({'message': 'Missing order_ids or status'}), 400
    
    orders = Order.query.filter(Order.id.in_(order_ids)).all()
    steadfast_errors = []
    
    for order in orders:
        old_status = order.status
        order.status = new_status
        
        # When switching to Processing, auto-create SteadFast consignment
        if new_status == 'Processing' and old_status != 'Processing':
            success, error = _handle_steadfast_for_order(order)
            if not success:
                steadfast_errors.append(f"Order {order.order_number}: {error}")
    
    db.session.commit()
    
    response = {'message': f'Status updated to {new_status} for {len(orders)} orders'}
    if steadfast_errors:
        response['steadfast_errors'] = steadfast_errors
    
    return jsonify(response), 200


@admin_bp.route('/orders/<int:order_id>/steadfast-status', methods=['GET'])
@jwt_required()
def refresh_steadfast_status(order_id):
    """Refresh the SteadFast delivery status for a single order."""
    order = Order.query.get_or_404(order_id)
    
    if not order.steadfast_consignment_id:
        return jsonify({'message': 'No SteadFast consignment for this order'}), 400
    
    try:
        delivery_status = check_status_by_consignment_id(order.steadfast_consignment_id)
        if delivery_status:
            order.steadfast_status = delivery_status
            db.session.commit()
        return jsonify({
            'message': 'Status refreshed',
            'steadfast_status': order.steadfast_status,
            'steadfast_tracking_code': order.steadfast_tracking_code,
            'steadfast_consignment_id': order.steadfast_consignment_id
        }), 200
    except Exception as e:
        return jsonify({'message': f'Failed to refresh status: {str(e)}'}), 500


@admin_bp.route('/orders/bulk-steadfast-status', methods=['POST'])
@jwt_required()
def refresh_bulk_steadfast_status():
    """Refresh SteadFast delivery status for multiple orders."""
    data = request.get_json()
    order_ids = data.get('order_ids', [])
    
    if not order_ids:
        return jsonify({'message': 'No order IDs provided'}), 400
    
    orders = Order.query.filter(
        Order.id.in_(order_ids),
        Order.steadfast_consignment_id.isnot(None)
    ).all()
    
    updated = 0
    errors = []
    for order in orders:
        try:
            delivery_status = check_status_by_consignment_id(order.steadfast_consignment_id)
            if delivery_status:
                order.steadfast_status = delivery_status
                updated += 1
        except Exception as e:
            errors.append(f"Order {order.order_number}: {str(e)}")
    
    db.session.commit()
    
    response = {'message': f'Refreshed status for {updated} orders'}
    if errors:
        response['errors'] = errors
    return jsonify(response), 200
