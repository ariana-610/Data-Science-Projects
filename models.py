from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Association table for many-to-many relationship between artists and genres
artist_genres = Table(
    'artist_genres',
    Base.metadata,
    Column('artist_id', Integer, ForeignKey('artists.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

class Artist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    californian = Column(Boolean, nullable=False, default=False)

    # Relationship to genres through the association table
    genres = relationship('Genre', secondary=artist_genres, back_populates='artists')

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)

    # Relationship to artists through the association table
    artists = relationship('Artist', secondary=artist_genres, back_populates='genres')

class Location(Base):
    __tablename__ = 'locations'

    entity_id = Column(String, primary_key=True)
    californian = Column(Boolean, nullable=False, default=False)

# Database setup
def init_db():
    engine = create_engine('sqlite:///music.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
