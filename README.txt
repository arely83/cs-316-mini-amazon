TEAM 4AL

TEAM MEMBERS
    Ashton Caldwell - Social
    Angel Huang - Account / Purchases
    Alveena Nadeem - Cart
    Arely Sun - Product
    Phillip Williams - Inventory / Order Fulfillment

We have chosen the mini Amazon project where we will be selling household goods.

Each of us have contributed to creating the ER diagram, writing up the schema, and designing the website.

Repo: https://gitlab.oit.duke.edu/pcw14/mini-amazon/-/tree/main 

MS3:
Demo video: https://drive.google.com/file/d/1qbW-KJBy5MBWOSa_UxrexXebadWeOkpQ/view?usp=sharing

All models that were created for our five API endpoints can be found in mini-amazon/app/models:
    order.py : Implementation for the sellers guru.
    product.py : Implementation for the products guru.
    purchase.py : Implementation for the users guru.
    review.py : Implementation for the social guru.
    carts.py : Implementation for the carts guru.

All templates that were created for our frontend display of our five API endpoints can be found in mini-amazon/app/templates:
    orders.html : Template for the sellers guru.
    product.html : Template for the products guru.
    purchases.html : Template for the users guru.
    reviews.html : Template for the social guru.
    carts.html : Template for the carts guru.

Data created for our five API endpoints can be found in mini-amazon/db/data:
    Orders.csv : Data for the sellers guru.
    Products.csv : Data for the products guru.
    Purchases.csv : Data for the users guru.
    Reviews.csv : Data for the social guru.
    Carts.csv : Data for the carts guru.

Other files that have been changed for the implementation of all five API endpoints:
    base.html : Changed to include buttons for API endpoints on the front page (mini-amazon/app/templates).
    index.html : “Add to Inventory” button was added for products on the front page (mini-amazon/app/templates).
    __init__.py : All implementations were added to be initialized (mini-amazon/app).
    create.sql : All tables for the API endpoints were created in this file (mini-amazon/db).
    load.sql : All tables for the API endpoints were loaded by this file (mini-amazon/db).
    Users.csv : Changed by the users guru (mini-amazon/db/data).



MS4:
Demo video: https://drive.google.com/file/d/1Ya9kTgoaLdZkjga5dr6rkoTjn6dqfUX1/view

All models that were updated/created for new implementations for this milestone can be found in mini-amazon/app/models:
    carts.py - updated
    order.py - updated
    product.py - updated
    review.py - updated
    user.py - updated

All templates that were updated/created for new frontend displays can be found in mini-amazon/app/templates:
    account_deleted.html - created
    base.html - updated
    carts.html - updated
    product.html - updated
    profile.html - created
    rate.html - created
    reviews.html - updated

Location of code where we generated a large database: mini-amazon/db/generated/gen.py

Generated data used for this milestone (all in mini-amazon/db/generated):
    Carts.csv
    NewUsers2.csv
    Orders.csv
    Products.csv
    Purchases.csv
    Reviews.csv
    Wishlist.csv

Other files that have been updated/created:
    mini-amazon/app/__init__.py : updated
    mini-amazon/app/carts.py : updated
    mini-amazon/app/index.py : updated
    mini-amazon/app/product.py : updated
    mini-amazon/app/profile.py : created
    mini-amazon/app/reviews.py : updated
    mini-amazon/app/users.py : updated
    mini-amazon/db/create.sql : updated
    mini-amazon/db/load.sql : updated


