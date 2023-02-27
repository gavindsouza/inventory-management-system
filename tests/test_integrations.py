import os

import pytest
from bs4 import BeautifulSoup

import inventory.app
from inventory.app import VIEWS, app

TEST_DATABASE_NAME = "tests/test.db"


@pytest.fixture
def mocked_client(monkeypatch):
    monkeypatch.setattr(inventory.app, "DATABASE_NAME", TEST_DATABASE_NAME)
    client = app.test_client()
    with app.app_context():
        app.init_db()
    yield client
    os.unlink(TEST_DATABASE_NAME)


def test_routes(mocked_client):
    for route in VIEWS.values():
        res = mocked_client.get(route)
        assert res.status_code == 200


def test_404(mocked_client):
    res = mocked_client.get("/not-a-route")
    assert res.status_code == 404


def test_summary_page(mocked_client):
    res = mocked_client.get("/")
    assert "Summary not available yet" in res.text


def test_product_page(mocked_client):
    res = mocked_client.get("/product")
    soup = BeautifulSoup(res.text, "html.parser")
    assert len(soup.find_all("tr")) == 1  # input form only

    res = mocked_client.post("/product", data={"prod_name": "test product", "prod_quantity": 10})
    assert res.status_code == 302

    soup = BeautifulSoup(mocked_client.get("/product").text, "html.parser")
    assert len(soup.find_all("tr")) == 2  # input form + 1 product
    assert [x.text for x in soup.find_all("tr")[0].contents[2:4]] == ["test product", "10"]


def test_location_page(mocked_client):
    res = mocked_client.get("/location")
    soup = BeautifulSoup(res.text, "html.parser")
    assert len(soup.find_all("tr")) == 1  # input form only

    res = mocked_client.post("/location", data={"warehouse_name": "test location"})
    assert res.status_code == 302

    soup = BeautifulSoup(mocked_client.get("/location").text, "html.parser")
    assert len(soup.find_all("tr")) == 2  # input form + 1 location
    assert [x.text for x in soup.find_all("tr")[0].contents[1:3]] == ["1", "test location"]


def test_transfer_page(mocked_client):
    res = mocked_client.get("/movement")
    assert "Data not available yet" in res.text

    res = mocked_client.post("/location", data={"warehouse_name": "test location"})
    assert res.status_code == 302
    res = mocked_client.post("/product", data={"prod_name": "test product", "prod_quantity": 10})
    assert res.status_code == 302

    res = mocked_client.post(
        "/movement",
        data={
            "prod_name": "test product",
            "from_loc": "",
            "to_loc": "test location",
            "quantity": 5,
        },
        follow_redirects=True,
    )
    assert [
        x.text for x in BeautifulSoup(res.text, "html.parser").find_all("tr")[-1].contents[:-1]
    ] == ["1", "1", "-", "1", "5"]
