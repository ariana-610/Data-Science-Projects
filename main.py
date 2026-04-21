import os
import sys

from dotenv import load_dotenv
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
)
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import wptools

from models import Artist, Genre, Location, init_db
from seed import seed_database

FORMATION_LOCATION = "P740"
PLACE_OF_BIRTH = "P19"
ADMINISTRATIVE_REGION = "P131"
CALIFORNIA = "Q99"

# Load environment variables from .env file
load_dotenv()


class ArtistSearchWorker(QThread):
    finished = pyqtSignal(object)  # Signal to emit the result

    def __init__(self, app, artist_name):
        super().__init__()
        self.app = app
        self.artist_name = artist_name

    def run(self):
        # Search for the artist in our database with exact match
        artist = (
            self.app.session.query(Artist)
            .filter(Artist.name.ilike(self.artist_name))
            .first()
        )

        if not artist:
            # Try to find and add the artist from Spotify
            artist = self.app.add_artist_from_spotify(self.artist_name)

        self.finished.emit(artist)


class MusicRecommenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("California Music Recommender")
        self.setMinimumSize(400, 300)

        # Initialize database session
        self.session = init_db()

        # Initialize Spotify client
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
            )
        )

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add widgets
        self.title_label = QLabel("Enter an artist name:")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("e.g., The Beatles")
        self.artist_input.returnPressed.connect(self.search_artist)
        layout.addWidget(self.artist_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_artist)
        layout.addWidget(self.search_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        # Seed the database with sample data
        seed_database(self.session)

        # Disable search button while searching
        self.search_button.setEnabled(True)
        self.artist_input.setEnabled(True)

    def add_artist_from_spotify(self, artist_name):
        # Search for artist on Spotify
        results = self.spotify.search(q=artist_name, type="artist", limit=1)
        if not results["artists"]["items"]:
            return None

        spotify_artist = results["artists"]["items"][0]

        # Get detailed artist info
        artist_details = self.spotify.artist(spotify_artist["id"])
        artist_name = artist_details["name"]

        # Create new artist in database
        artist = Artist(
            name=artist_name, californian=self.californian_artist(artist_name)
        )
        self.session.add(artist)

        # Add genres
        for genre_name in artist_details["genres"]:
            # Check if genre exists, create if it doesn't
            genre = self.session.query(Genre).filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                self.session.add(genre)

            artist.genres.append(genre)

        self.session.commit()
        return artist

    def californian_artist(self, artist_name):
        try:
            page = wptools.page(artist_name)
            page.wanted_labels([FORMATION_LOCATION, PLACE_OF_BIRTH])
            page.get_wikidata()
            location_ids = (
                page.data["claims"].get(FORMATION_LOCATION, False)
                or page.data["claims"].get(PLACE_OF_BIRTH, False)
                or page.data["claims"].get(ADMINISTRATIVE_REGION, False)
            )
            if not location_ids:
                return False
            return self.californian_location(location_ids[0])

        except:
            return False

    def californian_location(self, location_id):
        if location_id == CALIFORNIA:
            return True

        db_location = (
            self.session.query(Location).filter_by(entity_id=location_id).first()
        )
        if db_location:
            return db_location.californian

        location = wptools.page(wikibase=location_id)
        location.wanted_labels([ADMINISTRATIVE_REGION])
        location.get_wikidata()
        region_ids = location.data["claims"].get(ADMINISTRATIVE_REGION, False)

        if not region_ids:
            self.session.add(Location(entity_id=location_id, californian=False))
            self.session.commit()
            return False

        region_id = region_ids[0]

        if region_id == CALIFORNIA:
            self.session.add(Location(entity_id=location_id, californian=True))
            self.session.commit()
            return True
        else:
            result = self.californian_location(region_id)
            self.session.add(Location(entity_id=location_id, californian=result))
            self.session.commit()
            return result

    def search_artist(self):
        artist_name = self.artist_input.text().strip()
        if not artist_name:
            QMessageBox.warning(self, "Error", "Please enter an artist name")
            return

        # Disable input while searching
        self.search_button.setEnabled(False)
        self.artist_input.setEnabled(False)
        self.result_label.setText("Researching...")

        # Create and start worker thread
        self.worker = ArtistSearchWorker(self, artist_name)
        self.worker.finished.connect(self.handle_search_result)
        self.worker.start()

    def handle_search_result(self, artist):
        # Re-enable input
        self.search_button.setEnabled(True)
        self.artist_input.setEnabled(True)

        if not artist:
            self.result_label.setText(
                f"Artist '{self.artist_input.text().strip()}' not found in Spotify.\n"
                "Please try a different artist name."
            )
            return

        if artist.californian:
            self.result_label.setText(
                f"Congratulations! {artist.name} is a Californian artist!"
            )
        else:
            # Find Californian artists with matching genres
            matching_artists = []
            for genre in artist.genres:
                for cal_artist in genre.artists:
                    if cal_artist.californian and cal_artist.id != artist.id:
                        matching_artists.append(cal_artist.name)

            if matching_artists:
                result = f"Since {artist.name} is not from California, here are some similar Californian artists:\n\n"
                result += "\n".join(f"• {name}" for name in set(matching_artists))
                self.result_label.setText(result)
            else:
                self.result_label.setText(
                    f"No Californian artists found with similar genres to {artist.name}"
                )


def main():
    app = QApplication(sys.argv)
    window = MusicRecommenderApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
