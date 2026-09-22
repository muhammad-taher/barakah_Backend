from app import create_app
from app.extensions import db
from app.models import Admin, Category, Product
from werkzeug.security import generate_password_hash

app = create_app()

def seed():
    with app.app_context():
        # Create admin
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('password')
            )
            db.session.add(admin)
        
        # Create category
        if not Category.query.filter_by(slug='electronics').first():
            cat = Category(name='Electronics', slug='electronics')
            db.session.add(cat)
            db.session.flush()
            
            # Create product
            if not Product.query.filter_by(slug='smartphone-x').first():
                prod = Product(
                    name='Smartphone X',
                    slug='smartphone-x',
                    sku='SMX-01',
                    description='Latest model smartphone with advanced features.',
                    price=50000.0,
                    stock=50,
                    category_id=cat.id
                )
                db.session.add(prod)
                
        db.session.commit()
        print('Seed data inserted successfully.')

if __name__ == '__main__':
    seed()
