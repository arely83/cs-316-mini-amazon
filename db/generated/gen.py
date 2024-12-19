from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 200
num_products = 2000
num_purchases = 2500
num_wishlists = 2500
num_orders = 2500
num_reviews = 2000
num_carts = 200

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    with open('NewUsersAgain.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = (plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address']
            account_balance = 0
            account_type = 'Buyer'
            writer.writerow([uid, email, password, firstname, lastname, address, account_balance, account_type])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.unique.sentence(nb_words=3)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            category = category = fake.random_element(elements=('Beauty','Books','Food', 'Clothing', 'Health', 'Home', 'Toys'))
            description = fake.paragraph(nb_sentences=1)
            sellerid = -1
            writer.writerow([pid, name, price, available, category, description, sellerid])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_purchased = fake.date_time()
            quantity = fake.random_int(min=1, max=10)
            writer.writerow([id, uid, pid, time_purchased, quantity])
        print(f'{num_purchases} generated')
    return


def gen_wishlist(num_wishlists, available_pids):
    with open('Wishlist.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Wishlist...', end=' ', flush=True)
        for id in range(num_wishlists):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_added = fake.date_time()
            writer.writerow([id, uid, pid, time_added])
        print(f'{num_wishlists} generated')
    return

def gen_orders(num_orders, available_pids):
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for id in range(num_orders):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_ordered = fake.date_time()
            writer.writerow([id, uid, pid, time_ordered])
        print(f'{num_orders} generated')
    return

def gen_reviews(num_reviews, available_pids):
    with open("Reviews.csv", 'w') as f:
        writer = get_csv_writer(f)
        print('Reviews...', end = ' ', flush = True)
        for id in range(num_reviews):
            if id % 100 == 0:
                print(f'{id}', end = ' ', flush = True)
            uid = fake.random_int(min = 0, max = num_users - 1)
            pid = fake.random_element(elements = available_pids)
            rating = fake.random_int(min = 1, max = 5)
            time_posted = fake.date_time()
            details = fake.sentence(nb_words = 5)[:-1]
            writer.writerow([id, pid, uid, rating, time_posted, details])
        print(f'{num_reviews} generated')
    return




def gen_carts(num_carts, available_pids):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for id in range(num_carts):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            quantity = fake.random_int(1, 10)
            total_price = 0
            writer.writerow([id, uid, pid, quantity, total_price])
        print(f'{num_carts} generated')
    return


# gen_users(num_users)
available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
# gen_wishlist(num_wishlists, available_pids)
# gen_orders(num_orders, available_pids)
# gen_reviews(num_reviews, available_pids)
gen_carts(num_carts, available_pids)
