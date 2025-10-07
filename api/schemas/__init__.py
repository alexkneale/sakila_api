# a schema is the structure of a piece of data
# here, we createa a schema describing structure of our Actor model
# the schema will allow us to serailize Actor instances into JSON so that they can be transmitted over HTTP
# as well as to validate any incoming actor data sent by client
# like DTOs in spring

# Marshmallow is an object serializer
from flask_marshmallow import Marshmallow

ma = Marshmallow()
