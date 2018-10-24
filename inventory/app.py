# imports - standard imports
import os
import datetime
import sqlite3

# imports - third party imports
from flask import Flask, url_for, request, redirect
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
    msg = None
    q_data, warehouse, products = None, None, None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM location")  # <---------------------------------FIX THIS
        warehouse = cursor.fetchall()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        cursor.execute("SELECT prod.prod_name, logs.prod_quantity, loc.loc_name FROM products prod, logistics logs, location loc \
        WHERE prod.prod_id == logs.prod_id AND logs.to_loc_id == loc.loc_id GROUP BY logs.to_loc_id")
        q_data = cursor.fetchall()
    except sqlite3.Error as e:
        msg = f"An error occurred: {e.args[0]}"
    if msg:
        print(msg)

    return render('index.html', link=link, title="Summary", warehouses=warehouse, products=products, database=q_data)


@app.route('/product', methods=['POST', 'GET'])
def product():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    prod_name TEXT UNIQUE NOT NULL, \
                    prod_quantity INTEGER NOT NULL )")
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if request.method == 'POST':
        prod_name = request.form['prod_name']
        quantity = request.form['prod_quantity']

        transaction_allowed = False
        if prod_name not in ['', ' ', None]:
            if quantity not in ['', ' ', None]:
                transaction_allowed = True

        if transaction_allowed:
            try:
                cursor.execute("INSERT INTO products (prod_name, prod_quantity) VALUES (?, ?)", (prod_name, quantity))
                db.commit()
            except sqlite3.Error as e:
                msg = f"An error occurred: {e.args[0]}"
            else:
                msg = f"{prod_name} added successfully"

            return redirect(url_for('product'))
    if msg:
        print(msg)

    return render('product.html',
                  link=link, products=products, transaction_message=msg,
                  title="Products Log")


@app.route('/location', methods=['POST', 'GET'])
def location():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS location(loc_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                 loc_name TEXT UNIQUE NOT NULL)")
    db.commit()
    cursor.execute("SELECT * FROM location")
    warehouse_data = cursor.fetchall()

    if request.method == 'POST':
        warehouse_name = request.form['warehouse_name']

        transaction_allowed = False
        if warehouse_name not in ['', ' ', None]:
            transaction_allowed = True

        if transaction_allowed:
            try:
                cursor.execute("INSERT INTO location (loc_name) VALUES (?)", (warehouse_name,))
                db.commit()
            except sqlite3.Error as e:
                msg = f"An error occurred: {e.args[0]}"
            else:
                msg = f"{warehouse_name} added successfully"
            print(msg)
            return redirect(url_for('location'))

    return render('location.html',
                  link=link, warehouses=warehouse_data, transaction_message=msg,
                  title="Warehouse Locations")


@app.route('/movement', methods=['POST', 'GET'])
def movement():
    msg = None
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logistics(trans_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                prod_id INTEGER NOT NULL, \
                                from_loc_id INTEGER NOT NULL, \
                                to_loc_id INTEGER NOT NULL, \
                                prod_quantity INTEGER NOT NULL, \
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


@app.route('/delete')   # , methods=['POST', 'GET'])
def delete():
    type_ = request.args.get('type')
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()

    if type_ == 'location':
        id_ = request.args.get('loc_id')
        cursor.execute("DELETE FROM location WHERE loc_id == ?", str(id_))
        db.commit()
        return redirect(url_for('location'))

    elif type_ == 'product':
        id_ = request.args.get('prod_id')
        cursor.execute("DELETE FROM products WHERE prod_id == ?", str(id_))
        db.commit()
        return redirect(url_for('product'))


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    type_ = request.args.get('type')
    db = sqlite3.connect(DATABASE_NAME)
    cursor = db.cursor()

    if type_ == 'location' and request.method == 'POST':
        loc_id = request.form['loc_id']
        loc_name = request.form['loc_name']

        if loc_name:
            cursor.execute("UPDATE location SET loc_name = ? WHERE loc_id == ?", (loc_name, str(loc_id)))

        db.commit()
        return redirect(url_for('location'))

    elif type_ == 'product' and request.method == 'POST':
        prod_id = request.form['prod_id']
        prod_name = request.form['prod_name']
        prod_quantity = request.form['prod_quantity']

        if prod_name:
            cursor.execute("UPDATE products SET prod_name = ? WHERE prod_id == ?", (prod_name, str(prod_id)))
        if prod_quantity:
            cursor.execute("UPDATE products SET prod_quantity = ? WHERE prod_id == ?", (prod_quantity, str(prod_id)))
        db.commit()
        return redirect(url_for('product'))

    print("IT SHOULDN'T REACH HERE--------> app.py line 204")
    return render(type_+'.html')


if __name__ == '__main__':
    app.run(debug=True)
