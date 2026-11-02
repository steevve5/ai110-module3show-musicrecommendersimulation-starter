"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys

try:
    from . import recommender
except ImportError:
    import recommender


PROFILES = {
    # Default starter profile
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    # Late-night study listener who wants calm, acoustic-leaning tracks
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.40, "likes_acoustic": True},
    # Loud, aggressive, electric
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    # Adversarial: conflicting prefs (sad mood but very high energy)
    "Conflicted (Sad but 0.9 Energy)": {"genre": "blues", "mood": "sad", "energy": 0.9},
    # Adversarial: genre that does not exist in the catalog
    "Ghost Genre (K-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.6},
    # Adversarial: energy outside the 0-1 scale
    "Out-of-Range Energy (1.5)": {"genre": "classical", "mood": "peaceful", "energy": 1.5},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a ranked, explained list of recommendations for one profile."""
    print(f"\n=== {name} ===  {user_prefs}")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommender.recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")


def main() -> None:
    if "--experiment" in sys.argv:
        # Weight shift experiment: double energy, halve genre
        recommender.GENRE_WEIGHT = 1.0
        recommender.ENERGY_WEIGHT = 3.0
        print("EXPERIMENT: genre weight 1.0, energy weight 3.0")
    songs = recommender.load_songs("data/songs.csv")
    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs)
    print()


if __name__ == "__main__":
    main()
