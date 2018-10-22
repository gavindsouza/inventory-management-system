# imports - standard imports
import datetime
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


class Database:
    def __init__(self):
        self.connect = sqlite3.connect('inventory.db', check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                             prod_name TEXT UNIQUE NOT NULL)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS location(loc_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                             loc_name TEXT UNIQUE NOT NULL)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS logistics(trans_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                            prod_id INTEGER NOT NULL, \
                            from_loc_id INTEGER NOT NULL, \
                            to_loc_id INTEGER NOT NULL, \
                            quantity INTEGER NOT NULL, \
                            trans_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
                            FOREIGN KEY(prod_id) REFERENCES products(prod_id), \
                            FOREIGN KEY(from_loc_id) REFERENCES location(loc_id), \
                            FOREIGN KEY(to_loc_id) REFERENCES location(loc_id))")

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

db = Database()
db.add_product('A')
db.add_warehouse('B')
db.add_logs('A','B','B', 100)