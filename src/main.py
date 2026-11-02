"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


PROFILES = {
    # Default starter profile
    "Pop / Happy": {"genre": "pop", "mood": "happy", "energy": 0.8},
    # Late-night study listener who wants calm, acoustic-leaning tracks
    "Lofi / Chill": {"genre": "lofi", "mood": "chill", "energy": 0.40, "likes_acoustic": True},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a ranked, explained list of recommendations for one profile."""
    print(f"\n=== {name} ===  {user_prefs}")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs)
    print()


if __name__ == "__main__":
    main()
