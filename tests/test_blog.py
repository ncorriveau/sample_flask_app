import pytest
from flaskr.db import get_db

def test_index(client,auth):
    '''test index page for both when not logged in (first scenario) and logged in (second scenario)'''
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    #login as user 'test' 'test'
    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

#create parametrization to test multiple urls 
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_create(client,path):
    '''test post to multiple create URLs without being logged in - should redirect us to login page'''
    response = client.post(path)
    assert response.header['Location'] == "/auth/login"

def test_author_required(app,client,auth):
    ''''Change author_id to wrong id for given username and then confirm we get 403 (forbidden) when we try to modify posts'''
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id=2 WHERE id=1")
        db.commit()
    
    #current user cant modify posts
    auth.login()
    assert client.post('/1/update').status_code ==403
    assert client.post('/1/delete').status_code ==403

    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path',(
    '/2/update',
    '/2/delete'
))
def test_exists_required_(client,auth,path):
    '''after changine ID variable to proper context, login and confirm we get 404 when post doesn't exist  '''
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    '''login and test that we get a 200 status code from the create page, then create a post and confirm this is our second post'''
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    '''login and confirm we can get into proper id/update url. then update post and test that our updated was stored in db'''
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    '''test a couple URLs after logging in making sure that we are requiring a title to post to these sites'''
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    '''login and use delete URL - confirm that it redirects to index page and that when we query for post we get nothing back'''
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None