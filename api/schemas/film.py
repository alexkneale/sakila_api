from marshmallow import fields, validates, ValidationError, post_dump, validates_schema
from api.models.film import Film
from api.models.actor import Actor

from api.schemas import ma
from flask import url_for
from api.models import db

# inherit from Marshmallow class -> serializer
 
#  auto-generate a schema for Actor models
# can use this serialize and validate actor data
class FilmSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Film
        # makes load() return model instance
        load_instance = True
        # exclude actors from the default serialization
        exclude = ['actors']  
        sqla_session = db.session

    ### validation
    
    # fields
    title = fields.String(required=True)
    release_year = fields.Integer(required=False, allow_none=True)
    language_id = fields.Integer(required=True)
    original_language_id = fields.Integer(required=False, allow_none=True)
    rental_duration = fields.Integer(required=True)
    rental_rate = fields.Decimal(required=True, places=2)
    length = fields.Integer(required=False, allow_none=True)
    replacement_cost = fields.Decimal(required=True, places=2)
    rating = fields.String(required=False, allow_none=True)
    special_features = fields.String(required=False, allow_none=True)


    @post_dump
    def add_links(self, data, **kwargs):
        data['_links'] = {
            "self": {
                "href": url_for("api.films.get_film", film_id=data['film_id'], _external=True)
            },
            "actors": {
                "href": url_for("api.films.get_film_actors", film_id=data['film_id'], _external=True)
            },
        }
        return data


    # check title length
    @validates("title")
    def validate_title_length(self, value, **kwargs):
        if len(value) > 128:
            raise ValidationError("Invalid title length")
        
    # check release year is valid
    @validates("release_year")
    def validate_release_year(self, value, **kwargs):
        if (value is not None) and (value < 1850 or value > 2025):
            raise ValidationError("Invalid year for release year. Must be greater than 1850 and less or equal to current year")

    
    # check language id is valid
    @validates("language_id")
    def validate_language_id(self, value, **kwargs):
        if (value < 1):
            raise ValidationError("Invalid language id")
    
    # check language id is valid
    @validates("original_language_id")
    def validate_original_language_id(self, value, **kwargs):
        if (value is not None) and (value < 1):
            raise ValidationError("Invalid original language id")

    # check language id is valid
    @validates("rental_duration")
    def validate_rental_duration(self, value, **kwargs):
        if value < 1:
            raise ValidationError("Invalid rental duration")

    # check rental rate is valid
    @validates("rental_rate")
    def validate_rental_rate(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Invalid rental rate")
    
    # check length valid
    @validates("length")
    def validate_length(self, value, **kwargs):
        if (value is not None) and (value <= 0):
            raise ValidationError("Invalid length")
    
    # check replacement cost is valid
    @validates("replacement_cost")
    def validate_replacement_cost(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Invalid replacement cost")
    
    
    # check rental rate is valid
    @validates("rating")
    def validate_rating(self, value, **kwargs):
        if value not in ['G', 'PG', 'PG-13', 'R', 'NC-17']:
            raise ValidationError("Invalid rating. Options are G, PG, PG-13, R and NC-17")

    @validates("special_features")
    def validate_special_features(self, value, **kwargs):
        # all allowable features
        all_features = {'Trailers', 'Commentaries', 'Deleted Scenes', 'Behind the Scenes'}
        
        # split string input, trim extra whitespace and create set from it
        value = set(value.split(","))

        # check input set is subset of all features set
        if not value.issubset(all_features):
            raise ValidationError("Invalid special features. Options are: Trailers, Commentaries, Deleted Scenes, Behind the Scenes. Please separate all features with commas.")

class FilmCreateUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Film
        # makes load() return model instance
        load_instance = True
        # exclude actors from the default serialization
        exclude = ['actors']  
        sqla_session = db.session

    # accept list of actor IDs for creating/updating relationships
    actor_ids = fields.List(fields.Integer(), allow_none=True)
    
    ### validation
    
    # fields
    title = fields.String(required=True)
    release_year = fields.Integer(required=False, allow_none=True)
    language_id = fields.Integer(required=True)
    original_language_id = fields.Integer(required=False, allow_none=True)
    rental_duration = fields.Integer(required=True)
    rental_rate = fields.Decimal(required=True, places=2)
    length = fields.Integer(required=False, allow_none=True)
    replacement_cost = fields.Decimal(required=True, places=2)
    rating = fields.String(required=False, allow_none=True)
    special_features = fields.String(required=False, allow_none=True)


    # check title length
    @validates("title")
    def validate_title_length(self, value, **kwargs):
        if len(value) > 128:
            raise ValidationError("Invalid title length")
        
    # check release year is valid
    @validates("release_year")
    def validate_release_year(self, value, **kwargs):
        if (value is not None) and (value < 1850 or value > 2025):
            raise ValidationError("Invalid year for release year. Must be greater than 1850 and less or equal to current year")

    
    # check language id is valid
    @validates("language_id")
    def validate_language_id(self, value, **kwargs):
        if (value < 1):
            raise ValidationError("Invalid language id")
    
    # check language id is valid
    @validates("original_language_id")
    def validate_original_language_id(self, value, **kwargs):
        if (value is not None) and (value < 1):
            raise ValidationError("Invalid original language id")

    # check language id is valid
    @validates("rental_duration")
    def validate_rental_duration(self, value, **kwargs):
        if value < 1:
            raise ValidationError("Invalid rental duration")

    # check rental rate is valid
    @validates("rental_rate")
    def validate_rental_rate(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Invalid rental rate")
    
    # check length valid
    @validates("length")
    def validate_length(self, value, **kwargs):
        if (value is not None) and (value <= 0):
            raise ValidationError("Invalid length")
    
    # check replacement cost is valid
    @validates("replacement_cost")
    def validate_replacement_cost(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Invalid replacement cost")
    
    
    # check rental rate is valid
    @validates("rating")
    def validate_rating(self, value, **kwargs):
        if value not in ['G', 'PG', 'PG-13', 'R', 'NC-17']:
            raise ValidationError("Invalid rating. Options are G, PG, PG-13, R and NC-17")

    @validates("special_features")
    def validate_special_features(self, value, **kwargs):
        # all allowable features
        all_features = {'Trailers', 'Commentaries', 'Deleted Scenes', 'Behind the Scenes'}
        
        # split string input, trim extra whitespace and create set from it
        value = set(value.split(","))

        # check input set is subset of all features set
        if not value.issubset(all_features):
            raise ValidationError("Invalid special features. Options are: Trailers, Commentaries, Deleted Scenes, Behind the Scenes. Please separate all features with commas.")


    @validates_schema
    def validate_and_associate_actors(self, data, **kwargs):
        actor_ids = data.pop('actor_ids', [])
        
        # validate actor IDs
        if actor_ids:
            # get IDs of all actors that exist in our database
            existing_actors = Actor.query.filter(Actor.actor_id.in_(actor_ids)).all()
            existing_actor_ids = [a.actor_id for a in existing_actors]

            invalid_ids = [a_id for a_id in actor_ids if a_id not in existing_actor_ids]

            if invalid_ids:
                raise ValidationError({"actor_ids":f"Invalid actor IDs: {actor_ids}"})
            
            # store actors (NB not IDs), add to film instance later
            self._actors_to_associate = existing_actors
        else:
            self._actors_to_associate =[]
        


    @post_dump
    def add_links(self, data, **kwargs):
        data['_links'] = {
            "self": {
                "href": url_for("api.films.get_film", film_id=data['film_id'], _external=True)
            },
            "actors": {
                "href": url_for("api.films.get_film_actors", film_id=data['film_id'], _external=True)
            },
        }
        return data



# get requests
film_schema = FilmSchema()
films_schema = FilmSchema(many=True)
# create/update requests
film_create_update_schema = FilmCreateUpdateSchema()