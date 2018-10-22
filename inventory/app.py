# imports - standard imports
import os
import datetime
import sqlite3

# imports - third party imports
from flask import Flask, url_for, request
from flask import render_template as render


class Database:
    def __init__(self):
        self.connect = sqlite3.connect('inventory.db') #, check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                             prod_name TEXT UNIQUE NOT NULL)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS location(loc_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                             loc_name TEXT UNIQUE NOT NULL)")

        self.

        self.connect.commit()
        self.cursor.close()

    # updating/editing tables
    def update_product(self):
        self.connect.commit()

    def update_warehouse(self):
        self.connect.commit()

    def update_logs(self):
        self.connect.commit()

    # adding rows in tables
    def add_product(self, prod_name):
        try:
            self.cursor = self.connect.cursor()
            self.cursor.execute(f"INSERT INTO products (prod_name) VALUES ({prod_name})")
            self.connect.commit()
        except sqlite3.Error as e:
            return f"An error occurred: {e.args[0]}"
        return f"{prod_name} added successfully"

    def add_warehouse(self, loc_name):
        try:
            self.cursor = self.connect.cursor()
            self.cursor.execute(f"INSERT INTO products (prod_name) VALUES ({loc_name})")
            self.connect.commit()
        except sqlite3.Error as e:
            return f"An error occurred: {e.args[0]}"
        return f"{loc_name} added successfully"

    def add_logs(self, prod_name, from_loc, to_loc, quantity):
        curr_time = str(datetime.datetime.now())
        try:
            self.cursor = self.connect.cursor()
            self.cursor.execute(f"INSERT INTO logistics (prod_id, from_loc_id, to_loc_id, quantity, trans_time )"
                                f" VALUES ({prod_name}, {from_loc}, {to_loc}, {quantity}, {curr_time})")
            self.connect.commit()
        except sqlite3.Error as e:
            return f"An error occurred: {e.args[0]}"
        return f"Transaction added successfully"

    # viewing tables
    def view_product(self):
        self.cursor.execute("SELECT * FROM products")

    def view_warehouse(self):
        self.cursor.execute("SELECT * FROM warehouses")

    def view_logs(self):
        self.cursor.execute("SELECT * FROM logistics")

    def close(self):
        self.cursor.close()
        self.connect.close()

    def __del__(self):
        self.cursor.close()
        self.connect.close()


# setting up Flask instance
app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'inventory.db'),
    )
app.config.from_pyfile('config.py', silent=True)

# setting up database instance
db = Database()

# listing views
link = {x: x for x in ["location", "product", "movement"]}
link["index"] = '/'


@app.route('/')
def summary():
    return render('index.html', link=link, warehouses=warehouse, products=products, title="Summary")


@app.route('/product', methods=['POST', 'GET'])
def product():
    if request.method == 'POST':
        prod_name = request.form['prod_name']
        db.add_product(prod_name)
    return render('product.html', link=link, products=products, title="Products Log")


@app.route('/location', methods=['POST', 'GET'])
def location():
    if request.method == 'POST':
        warehouse_name = request.form['warehouse_name']
        db.add_warehouse(warehouse_name)
    return render('location.html', link=link, warehouses=warehouse, title="Warehouse Locations")


@app.route('/movement', methods=['POST', 'GET'])
def movement():
    msg = None
    if request.method == 'POST':
        prod_name = request.form['prod_name']
        from_loc = request.form['from_loc']
        to_loc = request.form['to_loc']
        quantity = request.form['quantity']

        msg = db.add_logs(prod_name, from_loc, to_loc, quantity)

    print(msg)
    return render('movement.html', link=link, trans_message=msg, title="ProductMovement")


if __name__ == '__main__':
    app.run(debug=True)
