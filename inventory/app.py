# imports - standard imports
import os

# imports - third party imports
from flask import Flask, url_for
from flask import render_template as render


app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'inventory.sqlite'),
    )
app.config.from_pyfile('config.py', silent=True)


warehouse = [
    {
        "name": "warehouse_001",
        "address": "Mumbai"
    },
    {
        "name": "warehouse_002",
        "address": "Pune"
    },
    {
        "name": "warehouse_003",
        "address": "Bhandardara"
    }
]
products = [
    {
        "name": "product_001",
        "count": 100
    },
    {
        "name": "product_002",
        "count": 200
    },
    {
        "name": "product_003",
        "count": 300
    }
]


@app.route('/')
@app.route('/index')
def summary():
    return render('index.html', warehouses=warehouse, products=products, title="Summary")


@app.route('/product')
def product():
    return render('product.html', products=products, title="Products Log")


@app.route('/location')
def location():
    return render('location.html')


@app.route('/movement')
def movement():
    return render('movement.html')


if __name__ == '__main__':
    app.run(debug=True)
