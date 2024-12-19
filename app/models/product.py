from flask import current_app as app
import os
class Product:
    def __init__(self, id, name, price, available, category, description, sellerid):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.category = category
        self.sellerid = sellerid
        self.description = description
        #self.image_path = "/static/css/images/defaultproduct.png" # Fall back to default image
        
        image_folder = os.path.join(app.static_folder, 'css/images')  # Path to image folder
        image_path = os.path.join(image_folder, f"{id}.jpeg")
        # Check if the specific product image exists
        print(f"Checking path: {image_path}")
        if os.path.exists(image_path):
            self.image_path = f"/static/css/images/{id}.jpeg"
        else:
            self.image_path = "/static/css/images/defaultproduct.png" # Fall back to default image

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, name, price, available, category, description, sellerid
            FROM Products
            WHERE id = :id
        ''', id=id)
        return Product(*(rows[0])) if rows else None
    
    def get_by_pid(pid):
        rows = app.db.execute('''
            SELECT id, name, price, available, category, description, sellerid
            FROM Products
            WHERE Products.id = :pid
        ''', pid=pid)
        return Product(*(rows[0])) if rows else None
        
    def get_sellerid_by_pid(pid):
        rows = app.db.execute('''
            SELECT sellerid
            FROM Products
            WHERE Products.id = :pid
        ''', pid=pid)
        return rows if rows else None

    def get_name(pid):
        rows = app.db.execute('''
            SELECT name
            FROM Products
            WHERE Products.id = :pid
        ''', pid = pid)
        return rows[0][0] if rows else None


    @staticmethod
    def get_all(sort_by='id', order='asc', available=True):
        valid_sort_columns = {'id', 'name', 'price', 'category', 'avg_rating'}
        if sort_by not in valid_sort_columns:
            sort_by = 'id'  # Default to 'id' if the sort_by value is invalid
        if order not in {'asc', 'desc'}:
            order = 'asc'  # Default to 'asc' if the order value is invalid
        query = f'''
            SELECT p.id, p.name, p.price, p.available, p.category, p.description, p.sellerid,
                COALESCE(AVG(r.rating), 0) AS avg_rating
            FROM Products p
            LEFT JOIN Reviews r on p.id = r.pid
            WHERE available = :available
            GROUP BY p.id
            ORDER BY {sort_by} {order}
        '''
        rows = app.db.execute(query, available=available)
        return rows
#        return [Product(*row) for row in rows]

    @staticmethod
    def get_filtered(search=None, min_price=None, max_price=None, category=None, rating_min=None,
                    sort_by='id', order='asc', k=None, offset=0, available=True):
        query = '''
            SELECT p2.id, p2.name, p2.price, p2.available, p2.category, p2.description, p2.sellerid, p2.avg_rating
            FROM (SELECT p.id, p.name, p.price, p.available, p.category, p.description, p.sellerid, COALESCE(AVG(r.rating), 0) AS avg_rating
                    FROM Products p
                    LEFT JOIN Reviews r ON p.id = r.pid
                    GROUP BY p.id) p2
            WHERE p2.available = :available
        '''
        params = {'available': available}

        if min_price is not None:
            query += ' AND p2.price >= :min_price'
            params['min_price'] = min_price
        if max_price is not None:
            query += ' AND p2.price <= :max_price'
            params['max_price'] = max_price
        if search:
            query += ' AND p2.name ILIKE :search'
            params['search'] = f'%{search}%'
        if category:
            query += ' AND p2.category = :category'
            params['category'] = category
        if rating_min is not None:
            query += ' AND p2.avg_rating >= :rating_min'
            params['rating_min'] = rating_min

        query += f' ORDER BY {sort_by} {order} LIMIT :k OFFSET :offset'
        params['k'] = k
        params['offset'] = offset

        rows = app.db.execute(query, **params)

        # Map rows to Product objects and separate avg_rating
        products = [
            Product(
                id=row[0],          # Index 0 for id
                name=row[1],        # Index 1 for name
                price=row[2],       # Index 2 for price
                available=row[3],   # Index 3 for available
                category=row[4],    # Index 4 for category
                description=row[5], # Index 5 for description
                sellerid=row[6]     # Index 6 for sellerid
            ) for row in rows
        ]

        avg_ratings = [row[7] for row in rows]  # Index 7 for avg_rating

        return products, avg_ratings


    @staticmethod
    def get_count(search=None, min_price=None, max_price=None, category=None, rating_min=None, available=True):
        query = '''
            SELECT COUNT(*)
            FROM (SELECT p.id, p.name, p.price, p.available, p.category, p.description, p.sellerid, COALESCE(AVG(r.rating), 0) AS avg_rating
                    FROM Products p
                    LEFT JOIN Reviews r ON p.id = r.pid
                    GROUP BY p.id)
            WHERE available = :available
        '''
        params = {'available': available}
        if min_price is not None:
            query += ' AND price >= :min_price'
            params['min_price'] = min_price
        if max_price is not None:
            query += ' AND price <= :max_price'
            params['max_price'] = max_price
        if search:
            query += ' AND name ILIKE :search'
            params['search'] = f'%{search}%'
        if category:
            query += ' AND category = :category'
            params['category'] = category
        if rating_min is not None:
            query += ' AND avg_rating >= :rating_min'
            params['rating_min'] = rating_min
        result = app.db.execute(query, **params)
        return result[0][0] if result else 0


    @staticmethod
    def create(name, price, available, category, description, sellerid):
        """Insert a new product into the database and return its ID."""
        rows = app.db.execute('''
            INSERT INTO Products (name, price, available, category, description, sellerid)
            VALUES (:name, :price, :available, :category, :description, :sellerid)
            RETURNING id
        ''', name=name, price=price, available=available, category=category, description=description, sellerid=sellerid)
        return rows[0][0]  # Return the ID of the new product

    def update(product_id, name, price, category, description):
        """Update an existing product in the database."""
        app.db.execute('''
            UPDATE Products
            SET name = :name, price = :price, category = :category, description = :description
            WHERE id = :product_id
        ''', product_id=product_id, name=name, price=price, category=category, description=description)

    @staticmethod
    def get_related_products(category, exclude_product_id, k=5, offset=0):
        query = '''
            SELECT id, name, price, available, category, description, sellerid
            FROM Products
            WHERE category = :category AND id != :exclude_product_id AND available = TRUE
            LIMIT :k OFFSET :offset
        '''
        params = {
            'category': category,
            'exclude_product_id': exclude_product_id,
            'k': k,
            'offset': offset
        }
        rows = app.db.execute(query, **params)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_by_name(name):
        rows = app.db.execute('''
            SELECT id, name, price, available, category, description, sellerid
            FROM Products
            WHERE LOWER(name) = LOWER(:name)
        ''', name=name)
        return Product(*(rows[0])) if rows else None