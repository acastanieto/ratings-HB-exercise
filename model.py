"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import correlation
# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

# Delete this line and put your User/Movie/Ratings model classes here.
class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.movie_score, r.movie_score) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict user's rating of a movie."""

        other_ratings = movie.ratings

        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        similarities.sort(reverse=True)

        similarities = [(sim, r) for sim, r in similarities if sim > 0]

        if not similarities:
            return None

        numerator = sum([r.movie_score * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator/denominator

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Movie(db.Model):
    """Movies in ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_name = db.Column(db.String(64), nullable=True)
    release_date = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        release_date = self.release_date.strftime("%B %d, %Y")
        return "<Movies movie_id=%d movie_name = %s release_date=%s >" % (self.movie_id,self.movie_name, release_date)


class Ratings(db.Model):
    """ Movie ratings"""

    __tablename__ = "ratings"

    ratings_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    movie_score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref=db.backref("ratings", order_by=ratings_id))

    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=ratings_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Ratings ratings_id=%d score=%d user_id=%d movie_id=%d>" % (self.ratings_id, self.movie_score, self.user_id, self.movie_id)




##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
