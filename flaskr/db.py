import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        #current app points to flask app handling the request
        #get db will be called when the app has been created and is handling a request, so current_app can be used here
        #lastly, we are connecting to the file that is set in the 'DATABASE' key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        #tells connection to return rows that behave like dicts (so can access col by name)
        g.db.row_factory = sqlite3.Row    
    return g.db

def close_db(e=None):
    db=g.pop('db',None)

    if db is not None:
        db.close

#g is a speical obj that is unique for each request - it is used to store data that might be accessed during the request 
#so here we are basically just returning the db connection if they call it again instead of creating a new one 


#add funcs that will run the sql commands 
def init_db():
    db = get_db()

    #open resource opens a file relative to the flaskr package (useful for deployment cause u wont necessarily know where this is)
    with current_app.open_resource('schema.sql') as f:
        #using a database connection from get_db to execute a read command
        db.executescript(f.read().decode('utf8'))
    

@click.command('init-db') #defines a command line init-db that called init_db func and shows a succesful message to user so if im in the CL and type init-db it will run the function
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables'''
    init_db()
    click.echo('Initialized the database')


#close_Db and init_db_command need to be added to app instance - but this isn't available when writing the functions 
def init_app(app):
    #teardown context manager for the db connection
    app.teardown_appcontext(close_db)
    #this adds an optional command to the 'flask' command to run the init_db_command func defined above 
    app.cli.add_command(init_db_command)
