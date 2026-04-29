# Unit test file
import pytest
from app import app, data


@pytest.fixture(autouse=True)
def clear_data():
    """Reset the in-memory store before every test."""
    data.clear()
    yield
    data.clear()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ── UI route ──────────────────────────────────────────────────────────────────

def test_index_returns_200(client):
    res = client.get('/')
    assert res.status_code == 200


def test_index_returns_html(client):
    res = client.get('/')
    assert b'Product Store' in res.data


# ── GET /products ─────────────────────────────────────────────────────────────

def test_get_products_empty(client):
    res = client.get('/products')
    assert res.status_code == 200
    assert res.get_json() == []


def test_get_products_after_create(client):
    client.post('/products', json={'name': 'Widget', 'description': 'A widget'})
    res = client.get('/products')
    assert res.status_code == 200
    products = res.get_json()
    assert len(products) == 1
    assert products[0]['name'] == 'Widget'


# ── POST /products ────────────────────────────────────────────────────────────

def test_create_product(client):
    res = client.post('/products', json={'name': 'Widget', 'description': 'A widget'})
    assert res.status_code == 201
    body = res.get_json()
    assert body['name'] == 'Widget'
    assert body['description'] == 'A widget'
    assert 'id' in body


def test_create_product_missing_name(client):
    res = client.post('/products', json={'description': 'No name'})
    assert res.status_code == 400


def test_create_product_no_body(client):
    res = client.post('/products', content_type='application/json', data='')
    assert res.status_code == 400


# ── GET /products/<id> ────────────────────────────────────────────────────────

def test_get_single_product(client):
    created = client.post('/products', json={'name': 'Gadget'}).get_json()
    res = client.get(f'/products/{created["id"]}')
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Gadget'


def test_get_product_not_found(client):
    res = client.get('/products/nonexistent-id')
    assert res.status_code == 404


# ── PUT /products/<id> ────────────────────────────────────────────────────────

def test_update_product(client):
    created = client.post('/products', json={'name': 'Old'}).get_json()
    res = client.put(f'/products/{created["id"]}', json={'name': 'New', 'description': 'Updated'})
    assert res.status_code == 200
    body = res.get_json()
    assert body['name'] == 'New'
    assert body['description'] == 'Updated'


def test_update_product_not_found(client):
    res = client.put('/products/bad-id', json={'name': 'X'})
    assert res.status_code == 404


def test_update_product_missing_name(client):
    created = client.post('/products', json={'name': 'Old'}).get_json()
    res = client.put(f'/products/{created["id"]}', json={'description': 'No name'})
    assert res.status_code == 400


# ── DELETE /products/<id> ─────────────────────────────────────────────────────

def test_delete_product(client):
    created = client.post('/products', json={'name': 'Temp'}).get_json()
    res = client.delete(f'/products/{created["id"]}')
    assert res.status_code == 204
    assert client.get(f'/products/{created["id"]}').status_code == 404


def test_delete_product_not_found(client):
    res = client.delete('/products/bad-id')
    assert res.status_code == 404
