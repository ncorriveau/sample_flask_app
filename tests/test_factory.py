from flaskr import create_app

def test_config():
    '''test configuration of the create_app function in __init__.py'''

    assert not create_app().testing
    assert create_app({'TESTING': True}).testing 

def test_hello(client):
    '''using client fixture, make 'GET' call to the 'hello' URL, and test that response '''
    response = client.get('/hello')
    assert response.data == b'Hello, World'