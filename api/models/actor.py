# import db from __init__.py
from api.models import db, film_actor

# represents table
class Actor(db.Model):
    
    actor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)

    # many-to-many relationship
    films = db.relationship('Film', secondary=film_actor, back_populates='actors')



