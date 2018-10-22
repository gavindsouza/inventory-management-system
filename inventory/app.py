# imports - standard imports
import os
import datetime
import sqlite3

# imports - third party imports
from flask import Flask, url_for, request
from flask import render_template as render

# global constants
DATABASE_NAME = 'inventory.db'

# setting up Flask instance
app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'inventory.db'),
    )
app.config.from_pyfile('config.py', silent=True)

# listing views
link = {x: x for x in ["location", "product", "movement"]}
link["index"] = '/'


@app.route('/')
def summary():
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM location")   # <---------------------------------FIX THIS
    warehouse = cursor.fetchall()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render('index.html', link=link, title="Summary", warehouses=warehouse, products=products)


@app.route('/product', methods=['POST', 'GET'])
def product():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    prod_name TEXT UNIQUE NOT NULL, \
                    quantity INTEGER NOT NULL )")
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    if request.method == 'POST':
        prod_name = request.form['prod_name']

        try:
            cursor.execute("INSERT INTO products (prod_name) VALUES (?)", prod_name)
            db.commit()
        except sqlite3.Error as e:
            msg =  f"An error occurred: {e.args[0]}"
        else:
            msg = f"{prod_name} added successfully"
    if msg:
        print(msg)

    return render('product.html', link=link, products=products, title="Products Log")


@app.route('/location', methods=['POST', 'GET'])
def location():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS location(loc_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                 loc_name TEXT UNIQUE NOT NULL)")
    warehouse_data = cursor.fetchall()
    if request.method == 'POST':
        warehouse_name = request.form['warehouse_name']

        try:
            cursor.execute("INSERT INTO location (loc_name) VALUES (?)", warehouse_name)
            db.commit()
        except sqlite3.Error as e:
            msg = f"An error occurred: {e.args[0]}"
        else:
            msg = f"{warehouse_name} added successfully"
    if msg:
        print(msg)

    return render('location.html', link=link, warehouses=warehouse_data, title="Warehouse Locations")


@app.route('/movement', methods=['POST', 'GET'])
def movement():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logistics(trans_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                prod_id INTEGER NOT NULL, \
                                from_loc_id INTEGER NOT NULL, \
                                to_loc_id INTEGER NOT NULL, \
                                quantity INTEGER NOT NULL, \
                                trans_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                                FOREIGN KEY(prod_id) REFERENCES products(prod_id), \
                                FOREIGN KEY(from_loc_id) REFERENCES location(loc_id), \
                                FOREIGN KEY(to_loc_id) REFERENCES location(loc_id))")
    cursor.execute("SELECT * FROM logistics")
    logistics_data = cursor.fetchall()

    if request.method == 'POST':
        prod_name = request.form['prod_name']
        from_loc = request.form['from_loc']
        to_loc = request.form['to_loc']
        quantity = request.form['quantity']
        curr_time = str(datetime.datetime.now())
        #
        #   BAD QUERY !!!
        #
        try:
            cursor.execute("INSERT INTO logistics (prod_id, from_loc_id, to_loc_id, quantity, trans_time ) "
                           "VALUES (?, ?, ?, ?, ?)", (prod_name, from_loc, to_loc, quantity, curr_time))
            db.commit()
        except sqlite3.Error as e:
            msg = f"An error occurred: {e.args[0]}"
        else:
            msg = f"Transaction added successfully"
    if msg:
        print(msg)

    return render('movement.html', link=link, trans_message=msg, logs=logistics_data, title="ProductMovement")


if __name__ == '__main__':
    app.run(debug=True)
