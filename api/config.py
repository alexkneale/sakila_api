# conifguration for application and flask plug ins

# here we have one config for productioin evironments, and other for development

import os

class Config(object):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = []   # default empty


# production,, with database uri

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:Shalom!@localhost:3306/sakila"
    CORS_ORIGINS = ["http://localhost:5173"]


match os.getenv('ENV'):
    case 'PRODUCTION':
        config = ProdConfig
    case _:
        config = DevConfig
