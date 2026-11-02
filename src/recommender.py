import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for the user, highest score first."""
        prefs = _profile_to_prefs(user)
        return sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable list of the reasons behind a song's score."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + ", ".join(reasons)

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_WEIGHT = 0.5

INT_FIELDS = {"id"}
FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the user_prefs dict used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in INT_FIELDS:
                row[field] = int(row[field])
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT:.1f})")

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT:.1f})")

    if "energy" in user_prefs:
        energy_points = ENERGY_WEIGHT * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += energy_points
        reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{energy_points:.2f})")

    if "likes_acoustic" in user_prefs:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        acoustic_points = ACOUSTIC_WEIGHT * fit
        score += acoustic_points
        reasons.append(f"acoustic fit (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest to lowest, and return the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
