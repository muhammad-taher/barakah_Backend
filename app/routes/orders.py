from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Order, OrderItem, Product
import uuid

orders_bp = Blueprint('orders', __name__, url_prefix='/api/v1/orders')

@orders_bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    customer_name = data.get('customer_name')
    phone = data.get('phone')
    address = data.get('address')
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400
        
    total_amount = 0
    order_items = []
    
    # Validate and calculate totals server-side
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        
        product = Product.query.get(product_id)
        if not product or not product.active:
            return jsonify({'error': f'Invalid product ID {product_id}'}), 400
            
        if product.stock < quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
        line_total = product.price * quantity
        total_amount += line_total
        
        # Deduct stock safely
        product.stock -= quantity
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price
        )
        order_items.append(order_item)
        
    # Create order
    order_number = f"ORD-{str(uuid.uuid4())[:8].upper()}"
    new_order = Order(
        order_number=order_number,
        customer_name=customer_name,
        phone=phone,
        address=address,
        total_amount=total_amount
    )
    
    db.session.add(new_order)
    db.session.flush() # To get order ID
    
    for oi in order_items:
        oi.order_id = new_order.id
        db.session.add(oi)
        
    db.session.commit()
    
    return jsonify({
        'message': 'Order placed successfully',
        'order_number': new_order.order_number,
        'total_amount': total_amount
    }), 201

@orders_bp.route('/track/<order_number>', methods=['GET'])
def track_order(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    items = OrderItem.query.filter_by(order_id=order.id).all()
    items_data = [{'product_id': i.product_id, 'quantity': i.quantity, 'unit_price': i.unit_price} for i in items]
    
    return jsonify({
        'order_number': order.order_number,
        'status': order.status,
        'total_amount': order.total_amount,
        'customer_name': order.customer_name,
        'items': items_data,
        'created_at': order.created_at.isoformat()
    }), 200
