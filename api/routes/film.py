from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from api.models import db
from api.models.film import Film
from api.models.actor import Actor

from api.schemas.film import (
    film_schema, 
    films_schema, 
    film_create_update_schema
)
from api.schemas.actor import actors_schema
from api.utils.pagination import paginate_query

# here we implement a RESTFul "actors" resource

# create a a blueprint, or module
# we can insert this into our Flask app
films_router = Blueprint('films',__name__, url_prefix ='/films')


@films_router.get('')
def get_all_films():

    release_year = request.args.get("release_year", type=int)
    language_id = request.args.get("language_id", type=int)
    original_language_id = request.args.get("original_language_id", type=int)
    rental_duration = request.args.get("rental_duration", type=int)
    rental_rate = request.args.get("rental_rate", type=float)
    length = request.args.get("length", type=int)
    replacement_cost = request.args.get("replacement_cost", type=float)
    rating = request.args.get("rating")
    special_features = request.args.get("special_features")


    # start query
    query = Film.query

    # apply filters
    filter_conditions = []

    # validate queries
    
    if release_year is not None:
        if release_year < 1850 or release_year > 2025:
            return jsonify({"error": "Invalid release year. Must be between 1850 and present year"}), 400
        filter_conditions.append(Film.release_year == release_year)

    if language_id is not None:
        if language_id <= 0:
            return jsonify({"error": "Invalid language id"}), 400
        filter_conditions.append(Film.language_id == language_id)

    if original_language_id is not None:
        if original_language_id <= 0:
            return jsonify({"error": "Invalid language id"}), 400
        filter_conditions.append(Film.original_language_id == original_language_id)

    if rental_duration is not None:
        if rental_duration <= 0:
            return jsonify({"error": "Invalid rental duration"}), 400
        filter_conditions.append(Film.rental_duration == rental_duration)

    if rental_rate is not None:
        if rental_rate <= 0:
            return jsonify({"error": "Invalid rental rate"}), 400
        filter_conditions.append(Film.rental_rate == rental_rate)

    if length is not None:
        if length <= 0:
            return jsonify({"error": "Invalid length"}), 400
        filter_conditions.append(Film.length == length)

    if replacement_cost is not None:
        if replacement_cost <= 0:
            return jsonify({"error": "Invalid replacement cost"}), 400
        filter_conditions.append(Film.replacement_cost == replacement_cost)

    if rating is not None:
        if rating not in ['G', 'PG', 'PG-13', 'R', 'NC-17']:
            return jsonify({"error": "Invalid rating. Options are G, PG, PG-13, R and NC-17"}), 400
        filter_conditions.append(Film.rating == rating)

    if special_features:

        all_features = {'Trailers', 'Commentaries', 'Deleted Scenes', 'Behind the Scenes'}
        requested_features = [feat.strip() for feat in special_features.split(",")]
        
        # validate
        if not set(requested_features).issubset(all_features):
            return jsonify({"error": "Invalid special feature"}), 400
        
        # one filter per requested feature
        for feature in requested_features:
            filter_conditions.append(Film.special_features.ilike(f'%{feature}%'))

    # apply all filters with AND logic
    if filter_conditions:
        query = query.filter(db.and_(*filter_conditions))

    # apply pagination
    result,status = paginate_query(
        query=query,
        schema=films_schema,
        endpoint='api.films.get_all_films',
        # include search param in pagination links
        release_year=release_year,
        language_id=language_id,
        original_language_id=original_language_id,
        rental_duratio=rental_duration,
        rental_rate=rental_rate,
        length=length,
        replacement_cost=replacement_cost,
        rating=rating,
        special_features=special_features
    )
    if status != 200:
        return result,status
        

    # rename 'items' to 'actors' for clarity
    response = {
        'films': result['items'],
        'pagination': result['pagination'],
        '_links': result['_links']
    }
    
    return jsonify(response), status


@films_router.get('/<film_id>')
def get_film(film_id):
    # when we refer to it statically 
    # refer to whole table
    film = Film.query.get(film_id)

    if film is None:
        return jsonify({"error":"Film not found"}), 404
        
    return film_schema.dump(film)

@films_router.get('/<film_id>/actors')
def get_film_actors(film_id):

    film = Film.query.get(film_id)

    if film is None:
        return jsonify({"error":"Film not found"}), 404
    
    query = Actor.query.join(Film.actors).filter(Film.film_id == film_id)
        
    # apply pagination
    result,status = paginate_query(
        query=query,
        schema=actors_schema,
        endpoint='api.films.get_film_actors',
        film_id=film_id
    )

    if status != 200:
        return result,status

    # rename 'items' to 'actors' for clarity
    response = {
        'film_id': film_id,
        'actors': result['items'],
        'pagination': result['pagination'],
        '_links': result['_links']
    }
    
    return jsonify(response), status


@films_router.post('')
def create_film():
    # get json data from request
    film_data = request.json

    try:
        # check that it fits with schema
        film = film_create_update_schema.load(film_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if hasattr(film_create_update_schema, "_actors_to_associate"):
        film.actors = film_create_update_schema._actors_to_associate


    try:
        # add to database
        db.session.add(film)
        # update database
        db.session.commit()
        # serialise created film, outputted to user
        return jsonify(film_schema.dump(film)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update film"}), 500

@films_router.put('/<film_id>')
def replace_film(film_id):
    
    film_data = request.json

    old_film = Film.query.get(film_id)

    if old_film is None:
        return jsonify({"error":"Film not found"}), 404
    
    try:
        # load into existing object (partial allows missing fields)
        updated_film = film_create_update_schema.load(
            film_data,
            instance=old_film,
            partial = False
        )
        if hasattr(film_create_update_schema, "_actors_to_associate"):
            updated_film.actors = film_create_update_schema._actors_to_associate
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        db.session.commit()
        return jsonify(film_schema.dump(old_film)), 200
    except:
        # rollback current transaction
        db.session.rollback()
        return jsonify({"error": "Failed to replace film"}), 500


@films_router.patch('/<film_id>')
def edit_film(film_id):
    
    film_data = request.json

    old_film = Film.query.get(film_id)

    if old_film is None:
        return jsonify({"error":"Film not found"}), 404
    
    try:
        # load into existing object (partial allows missing fields)
        updated_film = film_create_update_schema.load(
            film_data,
            instance=old_film,
            partial=True
        )
        if hasattr(film_create_update_schema, "_actors_to_associate"):
            updated_film.actors = film_create_update_schema._actors_to_associate
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        db.session.commit()
        return jsonify(film_schema.dump(old_film)), 200
    except:
        # rollback current transaction
        db.session.rollback()
        return jsonify({"error": "Failed to replace film"}), 500


@films_router.delete('/<film_id>')
def delete_film(film_id):

    film = Film.query.get(film_id)

    if film is None:
        return jsonify({"Error":"Film not found"}), 404
    
    db.session.delete(film)
    db.session.commit()
    return jsonify({}), 204

