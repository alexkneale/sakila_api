from marshmallow import fields, post_dump, ValidationError, validates_schema
from api.models.actor import Actor
from api.models.film import Film
from api.models import db

from api.schemas import ma
from flask import url_for, jsonify

# inherit from Marshmallow class -> serializer
 
#  auto-generate a schema for getting Actor models
# can use this serialize and validate actor data
class ActorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Actor
        # makes load() return model instance
        load_instance = True
        # exclude films this actor is in in serialization (as only want it as link)
        exclude = ['films']  
        

    # after serializing
    @post_dump
    def add_links(self, data, **kwargs):
        data['_links'] = {
            "self": {
                "href": url_for("api.actors.get_actor", actor_id=data['actor_id'], _external=True)
            },
            "films": {
                "href": url_for("api.actors.get_actor_films", actor_id=data['actor_id'], _external=True)
            }
        }
        return data


#  auto-generate a schema for getting Actor models
# can use this serialize and validate actor data
class ActorCreateUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Actor
        # makes load() return model instance
        load_instance = True
        sqla_session = db.session
        # exclude films this actor is in in serialization (as only want it as link)
        exclude = ['films']  
        
    
    # accept list of film IDs for creating/updating relationships
    film_ids = fields.List(fields.Integer(), allow_none=True)


    @validates_schema
    def validate_and_associate_films(self, data, **kwargs):
        # process film IDs before loading
        film_ids = data.pop('film_ids', [])

        # validate film IDs
        if film_ids:
            # get IDs of all films that exist in our database
            existing_films = Film.query.filter(Film.film_id.in_(film_ids)).all()
            existing_film_ids = [f.film_id for f in existing_films]

            invalid_ids = [f_id for f_id in film_ids if f_id not in existing_film_ids]

            if invalid_ids:
                raise ValidationError(f"Invalid film IDs: {invalid_ids}")

            # store films (NB not IDs), add to actor object later
            self._films_to_associate = existing_films
        else:
            self._films_to_associate = []

    # after serializing
    @post_dump
    def add_links(self, data, **kwargs):
        data['_links'] = {
            "self": {
                "href": url_for("api.actors.get_actor", actor_id=data['actor_id'], _external=True)
            },
            "films": {
                "href": url_for("api.actors.get_actor_films", actor_id=data['actor_id'], _external=True)
            }
        }
        return data
    


# for get requests
actor_schema = ActorSchema()
actors_schema = ActorSchema(many=True)
# for post/put/patch requests
actor_create_update_schema = ActorCreateUpdateSchema()