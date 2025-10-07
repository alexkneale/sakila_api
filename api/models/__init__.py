# initialise here so we can use in our model files
# flask sqla alchemy is an interface btwn mysql and python
from flask_sqlalchemy import SQLAlchemy
# db is entry point interacting with our database
db = SQLAlchemy()

# create models to describe structure of each of our tables, as they exist in the database
# which SQLAlchemy will use to generate SQL queries for our CRUD operations

# the association table for the many-to-many relationship
film_actor = db.Table('film_actor',
                      
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.actor_id'), primary_key=True),
    db.Column('film_id', db.Integer, db.ForeignKey('film.film_id'), primary_key=True),
    db.Column('last_update', db.TIMESTAMP)
)

# import models after association tables are defined
from api.models.actor import Actor
from api.models.film import Film