import sqlite3


import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close(app):
    with app.app_context():
        #test that the same connection is created each time 
        db = get_db()
        assert db is get_db()
    
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    
    #assure that db connection is closed after being opened
    assert 'closed' in str(e.value)

def test_init_db_command(runner,monkeypatch):
    class Recorder(object):
        #initialize it as false so we can test monkeypatch below
        called=False
    

    def fake_init_db():
        Recorder.called = True

    #this allows you to 'fake' make an API or db connection call. You won't actually make the call, but you know what to expect in the return
    #so you 'patch' the function and the desired return behavior here and it simulates it 
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)

    #call 'init-db' as argument in command line 
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    #using result of monkey patch.settattr, Recorder should be calleed 
    assert Recorder.called


