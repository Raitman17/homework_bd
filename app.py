from flask import Flask, request
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

credentials = {
        'host': getenv('PG_HOST'),
        'port': int(getenv('PG_PORT')),
        'dbname': getenv('PG_DBNAME'),
        'user': getenv('PG_USER'),
        'password': getenv('PG_PASSWORD'),
    }

connection = psycopg2.connect(
    host = getenv('PG_HOST'),
	port = int(getenv('PG_PORT')),
	dbname = getenv('PG_DBNAME'),
	user = getenv('PG_USER'),
	password = getenv('PG_PASSWORD'),
    cursor_factory=RealDictCursor)
connection.autocommit = True


@app.route("/")
def homepage():
    return 'Hello world!'


@app.get('/hotels')
def get_actors():
    query = """
	with services_title as(
	select
		h.id,
		coalesce(jsonb_agg(
			s.title)
			filter (where s.id is not null), '[]') as services
		from hotel.hotels h
		left join hotel.hotel_service hs on h.id = hs.hotel_id
		left join hotel.services s on s.id = hs.service_id
		group by h.id
	),
	room_all as (
	select 
		h.id,
		coalesce(json_agg(json_build_object(
			'number', r.number, 'floor', r.floor, 'class', r.class))
			filter (where r.id is not null), '[]') as rooms 
		from hotel.hotels h
		left join hotel.room r on r.hotel_id  = h.id
		group by h.id
	)
	select
    	h.name,
		h.address,
		h.rating,
		s.services,
		r.rooms
		from hotel.hotels h
		left join services_title s on h.id = s.id
		left join room_all r on r.id = h.id
"""

    with connection.cursor() as cursor:
        cursor = connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

    return result


@app.post('/hotels/create')
def create_hotel():
    body = request.json

    name = body['name']
    address = body['address']
    rating = body['rating']

    query = SQL("""
	insert into hotel.hotels(name, address, rating) 
	values ({name}, {address}, {rating})
	returning id;
	""").format(
        name=Literal(name),
        address=Literal(address),
        rating=Literal(rating))

    with connection.cursor() as cursor:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

    return result


@app.post('/hotels/update')
def update_hotel():
    body = request.json

    id = body['id']
    name = body['name']
    address = body['address']
    rating = body['rating']

    query = SQL("""
update hotel.hotels
set
  name = {name},
  address = {address},
  rating = {rating}
where id = {id}
returning id;
""").format(
        id=Literal(id),
        name=Literal(name),
        address=Literal(address),
        rating=Literal(rating))

    with connection.cursor() as cursor:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

    if not result:
        return '', 404

    return result


@app.delete('/hotels/delete')
def delete_hotel():
    try:
        body = request.json

        id = body['id']

        deleteActorReferencesQuery = SQL("delete from hotel.hotel_service where hotel_id = {hotel_id};").format(
            hotel_id=Literal(id))

        deleteActorQuery = SQL("""
    delete from hotel.hotels
    where id = {id}
    returning id;
    """).format(id=Literal(id))

        with connection.cursor() as cursor:
            cursor = connection.cursor()
            cursor.execute(deleteActorReferencesQuery)
            cursor.execute(deleteActorQuery)
            result = cursor.fetchall()

        if len(result) == 0:
            return '', 404

        return '', 204
    except:
        return '', 400
    

@app.get('/hotels/find_by_name')
def get_film_by_name():
    name = request.args.get('name')

    query = SQL("""
select *
from hotel.hotels
where name ilike {name}
""").format(name=Literal('%' + name + '%'))

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return result


@app.get('/hotels/find_by_rating')
def get_film_by_rating():
    rating = request.args.get('rating')

    query = SQL("""
select *
from hotel.hotels
where rating = {rating}
""").format(rating=Literal(rating))

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return result