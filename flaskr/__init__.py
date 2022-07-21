import os
from tempfile import TemporaryFile
from flask import Flask

def create_app(test_config=None):
    #instance_relative_config = True means that config files are relative to instance folder 
    #instance folder should be outside of flaskr package and contain local data that shouldnt be committed to version control
    app = Flask(__name__,instance_relative_config=True)
    
    #set default configurations for the app to use
    app.config.from_mapping(
        SECRET_KEY='dev', #this value should be over ridden with random value when deploying 
        DATABASE = os.path.join(app.instance_path,'flaskr.sqlite'), #this is where SQLite db file will be saved
    )

    if test_config == None:
        #load the instance config if none is given
        app.config.from_pyfile('config.py',silent=True)#overrides default configuration with falues from this folder...when deploying this could be used to keep real SECRET_KEY
    
    else:
        #load test config passed in argument
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)#makes sure that the instance path exists 
    except OSError:
        pass


    @app.route('/hello')
    def hello():
        return 'Hello World'

    from . import db 
    #here we are teardown method and adding the command init_db to the app defined in db.py
    #so now we can call init-db with the flask command! 
    db.init_app(app)

    #register blueprint in main app
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    #adding blog to main index url
    app.add_url_rule('/',endpoint='index')


    return app