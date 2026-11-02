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


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5, diverse: bool = False) -> None:
    """Print a ranked, explained table of recommendations for one profile."""
    results = recommender.recommend_songs(user_prefs, songs, k=k, diverse=diverse)
    widths = [3, 22, 16, 22, 6, 40]
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def row(cells):
        return "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"

    print(f"\n=== {name} ===  {user_prefs}")
    print(border)
    print(row(["#", "Title", "Artist", "Genre / Mood", "Score", "Reasons"]))
    print(border.replace("-", "="))
    for rank, (song, score, explanation) in enumerate(results, start=1):
        reasons = explanation.split(", ")
        first = [rank, song["title"], song["artist"], f"{song['genre']} / {song['mood']}", f"{score:.2f}", reasons[0]]
        print(row(first))
        for reason in reasons[1:]:
            print(row(["", "", "", "", "", reason]))
        print(border)


def main() -> None:
    if "--experiment" in sys.argv:
        # Weight shift experiment: double energy, halve genre
        recommender.GENRE_WEIGHT = 1.0
        recommender.ENERGY_WEIGHT = 3.0
        print("EXPERIMENT: genre weight 1.0, energy weight 3.0")
    diverse = "--diverse" in sys.argv
    if diverse:
        print("DIVERSITY MODE: -1.0 for a repeat artist, -0.5 for a repeat genre")
    songs = recommender.load_songs("data/songs.csv")
    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs, diverse=diverse)
    print()


if __name__ == "__main__":
    main()
