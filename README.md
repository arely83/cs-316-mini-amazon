# Mini Amazon Project

This is the repo from our CompSci 316 web app project, which is a
storefront where users can buy and sell products. Each member of
the team Ashton Caldwell, Angel Huang, Alveena Nadeem, Arely Sun,
and Liam Williams contributed to a section: Social, Account/Purchases,
Cart, Product, and Inventory/Order Fulfillment.

I worked on Product, which involves creating a shop page to display
products, individual product pages, and pages where an authenticated
user can create and edit their own products that they well. In addition
to "Add to Cart," "Add to Wishlist," and quick views for the product
image and description, a user can filter by a search term, price range,
or product category, and they can also sort by product ID, name, price,
rating, and product category in ascending or descending order. The
individual product detail page provides a list of available sellers
with the count of the product in their inventory. The product detail
page also includes product reviews and recommended related products.

Demo video: [https://drive.google.com/file/d/19ORQtDtYF916XbHmHt9_840wBkwut4ws/view?usp=drive_link]

To run the website, in your container shell, go into the repository
directory and issue the following commands:
```
poetry shell
flask run
```
If you use containers on your own laptop, point your browser to
http://localhost:8080/
