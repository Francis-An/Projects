#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cmath import nan
import imp
import json
from pickletools import read_uint1
from pydoc import describe
from textwrap import fill
from unittest import result
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import desc,func
from datetime import date, datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)



# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False, unique=True)
    city = db.Column(db.String(),nullable=False)
    state = db.Column(db.String(),nullable=False)
    address = db.Column(db.String(),nullable=False)
    phone = db.Column(db.String(), nullable=False,unique=True)
    image_link = db.Column(db.String(),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate -- done
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_talent = db.Column(db.String(),nullable=True)
    seeking_description = db.Column(db.Text,nullable=True)
    upcoming_shows_count = db.Column(db.Integer, default=2)
    past_shows_count = db.Column(db.Integer, default=4)
    shows = db.relationship('Show',backref='venue',lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(),nullable=False)
    state = db.Column(db.String(),nullable=False)
    phone = db.Column(db.String(), nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(),nullable=False)
    seeking_venue = db.Column(db.String(),nullable=True)
    seeking_description = db.Column(db.Text,nullable=True)
    upcoming_shows_count = db.Column(db.Integer, default=1)
    past_shows_count = db.Column(db.Integer, default=3)
    shows = db.relationship('Show',backref='artist',lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # The 10 recent venues in the data base
  recent_venues = db.session.query(Venue).order_by(desc(Venue.id)).limit(10).all()
  
  # The 10 recent artists in the data base
  recent_artists = db.session.query(Artist).order_by(desc(Artist.id)).limit(10).all()
  
  return render_template('pages/home.html', venues=recent_venues,artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  try:
    # I declared a variable called data which is an array to contained an oject
    # which also has three attribute city,state, and venues
    # The venues is also an array 
    data = []
    
    venues_data = db.session.query(Venue.state,Venue.city).group_by(Venue.state,Venue.city).all()

    for venue in venues_data:

      # I declared a veriable called venues_container which is an array to 
      # contain the venues information in the form of object
      venues_container = []
      data.append({
        'city' : venue[0],
        'state' : venue[1],
        'venues' : venues_container
      })

      venues_information = db.session.query(Venue.id,Venue.state,
      Venue.city,Venue.name,Venue.upcoming_shows_count
      ).filter_by(state = venue[0], city=venue[1]).all()
      
      for venue in venues_information:
        venues_container.append({
          'id' : venue[0],
          'name' : venue[3],
          'num_upcoming_shows': venue[4]
        })
    db.session.commit()
  except:
    db.session.rollback()
    flash("Error has ocurred when getting data")
  finally:
    db.session.close()

# data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    search_input = request.form['search_term']
    search_result = Venue.query.filter( 
      Venue.state.ilike('%{}%'.format(search_input)) |
    Venue.city.ilike('%{}%'.format(search_input))).all()

    response={
      "count": len(search_result),
      "data": []
    }
    for venue in search_result:
      response['data'].append({
        'id' : venue.id,
        'name' : venue.name,
        'city' : venue.city,
        'state' : venue.state,
        'num_upcoming_shows': venue.upcoming_shows_count,
      })

  except:
    db.session.rollback()
    flash("There is error in your search input!")
  finally:
    db.session.close()

# response={
#     "count": 1,
#     "data": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }

    
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  active_venue = Venue.query.get(venue_id)
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
    Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id
  ).filter(Show.start_time > datetime.now()).all()
  data1={
    "id": active_venue.id,
    "name": active_venue.name,
    "genres": active_venue.genres,
    "address": active_venue.address,
    "city": active_venue.city,
    "state": active_venue.state,
    "phone": active_venue.phone,
    "website_link": active_venue.website_link,
    "facebook_link": active_venue.facebook_link,
    "seeking_talent": active_venue.seeking_talent,
    "seeking_description": active_venue.seeking_description,
    "image_link": active_venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  for past_show in past_shows:
    data1['past_shows'].append({
      'artist_id' : past_show.artist_id,
      'artist_name' : past_show.artist.name,
      'artist_image_link' : past_show.artist.image_link,
      'start_time' : str(past_show.start_time)
    })
  
  for upcoming_show in upcoming_shows:
    data1['upcoming_shows'].append({
      'artist_id' : upcoming_show.artist_id,
      'artist_name' : upcoming_show.artist.name,
      'artist_image_link' : upcoming_show.artist.image_link,
      'start_time' : str(upcoming_show.start_time)
    })



# data1={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#     "past_shows": [{
#       "artist_id": 4,
#       "artist_name": "Guns N Petals",
#       "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 2,
#     "name": "The Dueling Pianos Bar",
#     "genres": ["Classical", "R&B", "Hip-Hop"],
#     "address": "335 Delancey Street",
#     "city": "New York",
#     "state": "NY",
#     "phone": "914-003-1132",
#     "website": "https://www.theduelingpianos.com",
#     "facebook_link": "https://www.facebook.com/theduelingpianos",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
#     "past_shows": [],
#     "upcoming_shows": [],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 3,
#     "name": "Park Square Live Music & Coffee",
#     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
#     "address": "34 Whiskey Moore Ave",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "415-000-1234",
#     "website": "https://www.parksquarelivemusicandcoffee.com",
#     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#     "past_shows": [{
#       "artist_id": 5,
#       "artist_name": "Matt Quevedo",
#       "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [{
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 1,
#   }


  data = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  input_phone = request.form.get('phone')
  input_name = request.form.get('name')
  
  name_in_db = Venue.query.filter_by(name = input_name).first()
  phone_in_db = Venue.query.filter_by(phone = input_phone).first()
  if name_in_db or phone_in_db:
    if name_in_db:
      flash('{} It alread exit'.format(input_name))
    elif phone_in_db:
      flash('{} It alread exit'.format(input_phone))
    return redirect(url_for('create_venue_submission'))
  else:
    create_venue = Venue(
          name = input_name,
          city = request.form.get('city'),
          state = request.form.get('state'),
          phone = input_phone,
          address = request.form.get('address'),
          genres = request.form.getlist('genres'),
          image_link = request.form.get('image_link'),
          facebook_link = request.form.get('facebook_link'),
          website_link = request.form.get('website_link'),
          seeking_talent = request.form.get('seeking_talent'),
          seeking_description = request.form.get('seeking_description'),
        )
  
    try:
      db.session.add(create_venue)
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
      db.session.rollback()
      flash('Venue ' + request.form['name'] + ' was unsuccessfully!')
      return redirect(url_for('create_venue_submission'))
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    deleted_artist = Venue.query.get(venue_id)
    
    db.session.delete(deleted_artist)
    db.session.commit()
    flash("Venue has successfully been deleted")
  except:
    db.session.rollback()
    flash("Venue has fail to delete")
  finally:
    db.session.close()
    
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id,Artist.name).all()
  data = []
  
  for artist in artists:
    data.append({
      'id': artist[0],
      'name' : artist[1]
    })


# data=[{
#     "id": 4,
#     "name": "Guns N Petals",
#   }, {
#     "id": 5,
#     "name": "Matt Quevedo",
#   }, {
#     "id": 6,
#     "name": "The Wild Sax Band",
#   }]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_input = request.form['search_term']
  search_result = Artist.query.filter(
    Artist.state.ilike('%{}%'.format(search_input)) |
     Artist.city.ilike('%{}%'.format(search_input))).all()

  response={
    "count": len(search_result),
    "data": []
  }
  for artist in search_result:
    response['data'].append({
      'id' : artist.id,
      'name' : artist.name,
      'num_upcoming_shows': artist.upcoming_shows_count,
    })

# response={
#     "count": 1,
#     "data": [{
#       "id": 4,
#       "name": "Guns N Petals",
#       "num_upcoming_shows": 0,
#     }]
#   }



  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  active_artist = Artist.query.get(artist_id)
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id
  ).filter(Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id
  ).filter(Show.start_time > datetime.now()).all()

  data={
    "id": active_artist.id ,
    "name": active_artist.name,
    "city": active_artist.city , 
    "state": active_artist.state ,
    "genres": active_artist.genres,
    "phone": active_artist.phone ,
    "website_link" : active_artist.website_link,
    "facebook_link": active_artist.facebook_link,
    "seeking_venue": active_artist.seeking_venue,
    "seeking_description": active_artist.seeking_description,
    "image_link": active_artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  for upcoming_show in upcoming_shows:
    data['upcoming_shows'].append({
      'venue_id' : upcoming_show.venue_id,
      'venue_name' : upcoming_show.venue.name,
      'venue_image_link' : upcoming_show.venue.image_link,
      'start_time' : str(upcoming_show.start_time)
    })

  for past_show in past_shows:
    data['past_shows'].append({
      'venue_id' : past_show.venue_id,
      'venue_name' : past_show.venue.name,
      'venue_image_link' : past_show.venue.image_link,
      'start_time' : str(past_show.start_time)
    })


  #   data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  
  
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)
 

@app.route('/artists/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
  try:
    
    deleted_artist = Artist.query.get(artist_id)
    
    db.session.delete(deleted_artist)
    db.session.commit()
    flash('Artist {} has been deleted successfully'.format(deleted_artist.name))
  except:
    db.session.rollback()
    flash('Delation of the Artist {} has fail!'.format(deleted_artist.name))
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  active_artist = Artist.query.get(artist_id)
  artist={
    "id": active_artist.id,
    "name": active_artist.name,
    "genres": active_artist.genres,
    "city": active_artist.city,
    "state": active_artist.state,
    "phone": active_artist.phone,
    "website": active_artist.website_link,
    "facebook_link": active_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": active_artist.seeking_description,
    "image_link": active_artist.image_link
  }


#  artist={
#     "id": 4,
#     "name": "Guns N Petals",
#     "genres": ["Rock n Roll"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "326-123-5000",
#     "website": "https://www.gunsnpetalsband.com",
#     "facebook_link": "https://www.facebook.com/GunsNPetals",
#     "seeking_venue": True,
#     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
#   }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', )
    artist.state = request.form.get('state', )
    artist.phone = request.form.get('phone', )
    artist.genres = request.form.getlist('genres', )
    artist.image_link = request.form.get('image_link', )
    artist.facebook_link = request.form.get('facebook_link', )
    artist.website_link = request.form.get('website_link', )
    artist.seeking_venue = request.form.get('seeking_venue', )
    artist.seeking_description = request.form.get('seeking_description')
    
    db.session.commit()
    flash("Artist {} is has been updated successfully".format(artist.name))
  except:
    db.session.rollback()
    flash("Artist {} updation has fail".format(artist.name))
  finally:
    db.session.close()


# venue={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
#   }


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  active_venue = Venue.query.get(venue_id)
  form = VenueForm()
  venue={
    "id": active_venue.id,
    "name": active_venue.name,
    "genres": active_venue.genres,
    "address": active_venue.address,
    "city": active_venue.city,
    "state": active_venue.state,
    "phone": active_venue.phone,
    "website": active_venue.website_link,
    "facebook_link": active_venue.facebook_link,
    "seeking_talent": active_venue.seeking_talent,
    "seeking_description": active_venue.seeking_description,
    "image_link": active_venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    active_venue = Venue.query.get(venue_id)

    active_venue.name = request.form.get('name', '')
    active_venue.city = request.form.get('city', )
    active_venue.state = request.form.get('state', )
    active_venue.phone = request.form.get('phone', )
    active_venue.address = request.form.get('address', )
    active_venue.genres = request.form.getlist('genres', )
    active_venue.image_link = request.form.get('image_link', )
    active_venue.facebook_link = request.form.get('facebook_link', )
    active_venue.website_link = request.form.get('website_link', )
    active_venue.seeking_talent = request.form.get('seeking_talent', )
    active_venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash("Venue {} has been updated successfully".format(active_venue.name))
  except:
    db.session.rollback()
    flash("Venue {} updation has fail!".format(active_venue.name))
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  input_phone = request.form.get('phone', )
  phone_in_db = Artist.query.filter_by(phone = input_phone).first()
  if phone_in_db:
    flash('{} already exits!'.format(input_phone))
    return redirect(url_for('create_artist_submission'))
  else:
    try:
      register_artist = Artist(
        name = request.form.get('name', ''),
        city = request.form.get('city', ),
        state = request.form.get('state', ),
        phone = input_phone,
        genres = request.form.getlist('genres', ),
        image_link = request.form.get('image_link', ),
        facebook_link = request.form.get('facebook_link', ),
        website_link = request.form.get('website_link', ),
        seeking_venue = request.form.get('seeking_venue', ),
        seeking_description = request.form.get('seeking_description', ),
      )

      db.session.add(register_artist)
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('Artist ' + request.form['name'] + ' registration fail!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      'venue_id' : show.venue_id,
      'venue_name' : show.venue.name,
      'artist_id' : show.artist_id,
      'artist_name' : show.artist.name,
      'artist_image_link' : show.artist.image_link, 
      'start_time' : str(show.start_time)
    })

  
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # input_venue_id = request.form.get('venue_id')
  # Venue_availablity = Venue.query.filter_by(venue_id = input_venue_id).first()
  # if Venue.seeking_talent == False:

  try:
    new_show = Show(
      start_time = request.form.get('start_time'),
      venue_id = request.form.get('venue_id'),
      artist_id = request.form.get('artist_id')
    )
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Ooooh! something went wrong, the show creation fail!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return redirect(url_for('shows'))
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
