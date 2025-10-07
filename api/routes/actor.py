from flask import (
    Blueprint, 
    request, 
    jsonify, 
    url_for
)

from marshmallow import ValidationError

from api.models import db
from api.models.actor import Actor
from api.models.film import Film

from api.schemas.actor import (
    actor_schema, 
    actors_schema, 
    actor_create_update_schema
)

from api.schemas.film import films_schema
from api.utils.pagination import paginate_query

# here we implement a RESTFul "actors" resource

# create a a blueprint, or module
# we can insert this into our Flask app
actors_router = Blueprint('actors', __name__, url_prefix ='/actors')

@actors_router.get('/')
def get_all_actors():

    # base query
    query = Actor.query

    # filtering
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")

    if first_name and len(first_name) > 45:
        return jsonify({"error":"Invalid first name length"}), 400

    if last_name and len(last_name) > 45:
        return jsonify({"error":"Invalid last name length"}), 400

    # apply filters
    filter_conditions = []
    
    if first_name:
        filter_conditions.append(Actor.first_name.ilike(f'%{first_name}%'))
    
    if last_name:
        filter_conditions.append(Actor.last_name.ilike(f'%{last_name}%'))
    
    # apply all filters with AND logic
    if filter_conditions:
        query = query.filter(db.and_(*filter_conditions))

    # apply pagination
    result,status = paginate_query(
        query=query,
        schema=actors_schema,
        endpoint='api.actors.get_all_actors',
        # include search param in pagination links
        first_name=first_name,
        last_name=last_name
    )

    if status != 200:
        return result,status

    # rename 'items' to 'actors' for clarity
    response = {
        'actors': result['items'],
        'pagination': result['pagination'],
        '_links': result['_links']
    }
    
    return jsonify(response), status



@actors_router.get('/<actor_id>')
def get_actor(actor_id):
    # when we refer to it statically 
    # refer to whole table
    actor = Actor.query.get(actor_id)

    if actor is None:
        return jsonify({"error":"Actor not found"}), 404
        
    return actor_schema.dump(actor)


@actors_router.get('/<actor_id>/films')
def get_actor_films(actor_id):

    actor = Actor.query.get(actor_id)

    if actor is None:
        return jsonify({"error":"Actor not found"}), 404
    
    # find all films with actor
    query = Film.query.join(Actor.films).filter(Actor.actor_id == actor_id)

    # pagination
    result, status = paginate_query(
        query=query,
        schema=films_schema,
        endpoint='api.actors.get_actor_films',
        actor_id=actor_id
    )

    if status != 200:
        return result,status

    response = {
        'actor_id': actor_id,
        'films': result['items'],
        'pagination': result['pagination'],
        '_links': result['_links']
    }
    
    return jsonify(response), status

@actors_router.post('/')
def create_actor():
    # get json data from request
    actor_data = request.json

    try:
        # check that it fits with schema
        actor = actor_create_update_schema.load(actor_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if hasattr(actor_create_update_schema, "_films_to_associate"):
        actor.films = actor_create_update_schema._films_to_associate

    try:
        # add Actor model object to database
        db.session.add(actor)
        # update database
        db.session.commit()
        # serialize created actor, outputted to user
        return jsonify(actor_schema.dump(actor)), 201
    except Exception as e:
        # rollback current transaction
        db.session.rollback()
        return jsonify({"error": "Failed to create actor"}), 500


@actors_router.put('/<actor_id>')
def replace_actor(actor_id):

    updated_actor_data = request.json

    old_actor = Actor.query.get(actor_id)

    if old_actor is None:
        return jsonify({"error":"Actor not found"}), 404


    try:
        # check that it fits with schema
        updated_actor = actor_create_update_schema.load(
            updated_actor_data,
            instance = old_actor,
            partial = False
        )
        if hasattr(actor_create_update_schema, "_films_to_associate"):
            updated_actor.films = actor_create_update_schema._films_to_associate
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        db.session.commit()
        return jsonify(actor_schema.dump(old_actor)), 200
    except:
        # rollback current transaction
        db.session.rollback()
        return jsonify({"error": "Failed to replace actor"}), 500


@actors_router.patch('/<actor_id>')
def edit_actor(actor_id):
    updated_actor_data = request.json

    old_actor = Actor.query.get(actor_id)

    if old_actor is None:
        return jsonify({"error":"Actor not found"}), 404


    try:
        # check that it fits with schema
        updated_actor = actor_create_update_schema.load(
            updated_actor_data,
            instance = old_actor,
            partial=True
        )
        if hasattr(actor_create_update_schema, "_films_to_associate"):
            updated_actor.films = actor_create_update_schema._films_to_associate
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    try:
        db.session.commit()
        return jsonify(actor_schema.dump(old_actor)), 200
    except:
        # rollback current transaction
        db.session.rollback()
        return jsonify({"error": "Failed to update actor"}), 500



@actors_router.delete('/<actor_id>')
def delete_actor(actor_id):

    actor = Actor.query.get(actor_id)

    if actor is None:
        return jsonify({"Error": "Actor not found"}), 404

    # delete
    db.session.delete(actor)
    db.session.commit()
    return jsonify({}), 204
    
