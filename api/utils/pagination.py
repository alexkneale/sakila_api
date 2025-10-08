from flask import request, url_for

def paginate_query(query, schema, endpoint, **kwargs):
    """
    helper function to paginate any SQLAlchemy query
    
    params:
    - query: SQLAlchemy query object
    - schema: marshmallow schema for serialization
    - endpoint: flask endpoint name for generating links
        **kwargs: additional URL parameters to include in links -> queries etc
    
    returns:
        dictionary with paginated results and metadata
    """
    try:
        # request args gets info about parsed contents of the query string (in dictionary) 
        # here we get info about current page (default to page 1)
        page = request.args.get("page", 1, type=int)

        # here we get info about items displayed per page (default to 10)
        per_page = request.args.get('per_page', 10, type=int)

        # validating parameters
        if page < 1:
            return {'error': 'Page number must be 1 or greater'}, 400

        if per_page < 1:
            return {'error': 'Items per page must be 1 or greater'}, 400

        # paginate the query
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        # check if page exists
        if page > pagination.pages and pagination.pages > 0:
            return {'error': f'Page {page} does not exist. Maximum page is {pagination.pages}'}, 404
        

        # serialize the items
        items_data = schema.dump(pagination.items)

        # build base URL parameters
        url_params = {'page': page, 'per_page': per_page, '_external': True}
        # update with all queries (if there are any)
        url_params.update(kwargs)

        # build navigation links
        links = {
            'self': url_for(endpoint, **url_params)
        }

        # if there's a previous page
        # add link to previous page adn first page to links
        if pagination.has_prev:

            # copy url param, and update page with previous page number
            url_params_prev = url_params.copy()
            url_params_prev['page'] = pagination.prev_num
            links['prev'] = url_for(endpoint, **url_params_prev)
            
            # copy url param, and update page with first page number
            url_params_first = url_params.copy()
            url_params_first['page'] = 1
            links['first'] = url_for(endpoint, **url_params_first)

        # if there's a next page
        # add link to next page and last page to links
        if pagination.has_next:

            # copy url param, and update page with next page number
            url_params_next = url_params.copy()
            url_params_next['page'] = pagination.next_num
            links['next'] = url_for(endpoint, **url_params_next)
            
            # copy url param, and update page with last page number
            url_params_last = url_params.copy()
            url_params_last['page'] = pagination.pages
            links['last'] = url_for(endpoint, **url_params_last)

                                    
        # build response
        return {
            'items': items_data,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            '_links': links
        }, 200
    except Exception as e:
        print("shalom")
        return (e)
        return {'error': 'Pagination error occurred'}, 500
