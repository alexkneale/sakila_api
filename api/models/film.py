# import db from __init__.py
from api.models import db, film_actor

# represents table
class Film(db.Model):

    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    language_id = db.Column(db.SmallInteger, nullable=False)
    original_language_id = db.Column(db.SmallInteger, nullable=True)
    rental_duration = db.Column(db.SmallInteger, nullable=False)
    rental_rate = db.Column(db.Float(asdecimal=True), nullable=False)
    length = db.Column(db.SmallInteger, nullable=True)
    replacement_cost = db.Column(db.Float(asdecimal=True), nullable=False)
    rating = db.Column(db.String(255), nullable=True)
    special_features = db.Column(db.String(255), nullable=True)

    # many-to-many relationship
    actors = db.relationship('Actor', secondary=film_actor, back_populates='films')


