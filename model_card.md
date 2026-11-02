# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

**Goal / task:** VibeMatch suggests the top 5 songs from a small catalog that best fit one listener's taste. It predicts how well each song "fits" a user, based on their favorite genre, favorite mood, how energetic they want the music to be, and whether they like acoustic sound.

**Assumptions about the user:** it assumes the user can describe their taste with one genre, one mood, and one energy level. It also assumes that taste stays the same; it does not know what time of day it is or what the user just listened to.

**Intended use:** classroom exploration. It is meant for learning how content-based recommenders turn data into a ranked list, and for testing how weights and biases change the results.

**Not intended for:** real users or real music apps. It should not be used to decide what music gets promoted, to judge artists, or to make any decision that matters to a real person. The catalog is too small and hand-made, and the rules are too simple.

---

## 3. How the Model Works  

Each song has a genre, a mood, an energy level from 0 to 1, and an acousticness level from 0 to 1. The user says what genre and mood they like, what energy level they want, and (optionally) whether they like acoustic music.

VibeMatch gives every song points:

- **+2 points** if the genre matches.
- **+1 point** if the mood matches.
- **Up to 1.5 points** for energy. The closer the song's energy is to what the user wants, the more points it gets. A perfect match gets all 1.5; a song that is far off gets very few.
- **Up to 0.5 points** for acoustic fit. If the user likes acoustic music, more acoustic songs get more points; if not, more electric/produced songs do.

Then it adds up the points, sorts all songs from highest to lowest, and shows the top 5 with a list of reasons (for example, "genre match (+2.0)").

**Diversity mode (optional):** with `--diverse`, VibeMatch builds the top 5 one song at a time. If a song's artist is already on the list it loses 1 point, and if its genre is already on the list it loses 0.5 points. The reasons list shows the penalty, so it's clear why a song moved down.

**Changes from the starter:** the starter code returned the first few songs with no scoring. I added the full scoring recipe, the reasons list, the acoustic-fit rule, and the sorting step.

---

## 4. Data  

- **Size:** 19 songs. The starter had 10; I added 9 more.
- **Features:** title, artist, genre, mood, energy, tempo (BPM), valence (positivity), danceability, and acousticness. Only genre, mood, energy, and acousticness are used in scoring.
- **Genres:** pop, indie pop, lofi, rock, ambient, jazz, synthwave, hip-hop, classical, country, metal, r&b, edm, folk, reggae, blues.
- **Moods:** happy, chill, intense, relaxed, moody, focused, confident, peaceful, nostalgic, angry, romantic, energetic, melancholic, sad.
- **What I added:** the 9 new songs cover genres and moods the starter was missing, and stretch energy from 0.15 to 0.97.
- **Limits:** most genres have only one song, so a metal or blues fan gets one real match and then filler. There are no lyrics, languages, release years, or popularity info. There is no song that is both sad and high-energy. The songs and numbers are made up, not measured from real audio.

---

## 5. Strengths  

- It works well for users with clear, "normal" taste. Chill Lofi, High-Energy Pop, and Deep Intense Rock all got top picks that matched my intuition (Library Rain, Sunrise City, Storm Runner).
- Energy closeness does a good job separating "study music" from "workout music." The lofi and rock lists had zero songs in common.
- Every recommendation comes with reasons, so it is easy to see *why* a song was picked and to spot when the logic is wrong.
- It still gives sensible results when the genre doesn't exist in the catalog (K-pop): mood and energy take over and return happy, mid-energy songs.

---

## 6. Limitations and Bias 

**Weakness: genre and energy can override what the user actually asked for.** A genre match is worth +2.0 points, which is more than a perfect energy match (+1.5), so a song that shares the user's genre label can beat songs that feel far closer. The clearest case was the "Conflicted" profile (blues, sad, energy 0.9): Rainy Day Blues ranked first even though its energy (0.33) is the opposite of what the user wanted, and every other slot went to loud rock, pop, EDM and metal tracks that match the energy but not the sadness at all. There is no song in the catalog that is both sad and high-energy, and the system has no way to say "nothing fits well," so it confidently returns a mix of two different users' playlists. On top of that, genres and moods only count on an exact string match, so "indie pop" gets nothing from a "pop" fan and a K-pop fan gets no genre points at all. Finally, the energy formula does not guard against bad input: an energy target of 1.5 produced a **negative** energy score (−0.53) for a classical song, which is mathematically invalid for a "closeness" score.

---

## 7. Evaluation  

### Profiles tested

I ran six profiles through `python -m src.main`: three "normal" listeners (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three adversarial ones designed to trick the scoring (Conflicted: sad mood but 0.9 energy; Ghost Genre: K-pop, which is not in the catalog; Out-of-Range Energy: a target of 1.5 on a 0–1 scale).

### What surprised me

- **Gym Hero shows up everywhere.** It appears in the top 5 for four of the six profiles (pop, rock, conflicted, out-of-range). In plain terms: Gym Hero is labeled "pop" and is very high energy (0.93). A "Happy Pop" listener gets +2.0 just because the label says pop, plus most of the energy points because 0.93 is near their 0.8 target. The system never checks that Gym Hero's mood is "intense," not "happy," so it ranks #2 for someone who just wants cheerful pop. For rock and high-energy users it ranks high for the same energy reason.
- **Why Sunrise City ranked #1 for High-Energy Pop:** it is the only song that earns all three: genre match (+2.0), mood match (+1.0), and energy 0.82 vs. 0.80 (+1.47), for a total of 4.47.
- **The out-of-range profile went negative.** The classical song still won, but only because its genre and mood bonuses (+3.0) outweighed a −0.53 energy penalty.
- **The ghost-genre profile still worked reasonably.** With no genre points available, mood and energy took over and returned happy, mid-energy songs, which feels sensible.

### Comparing profiles

- **High-Energy Pop vs. Chill Lofi:** pop's list is all energy 0.75–0.93 and electronic; lofi's list is all energy 0.28–0.42 and acoustic. The only thing that changed was the energy target and genre, and the lists share zero songs, which shows energy closeness really is separating "workout" from "study" music.
- **High-Energy Pop vs. Deep Intense Rock:** both are high energy, so they share Gym Hero and Sunrise City, but rock pulls in Iron Furnace and Pulse Overdrive because they are even louder (0.95–0.97). Makes sense: the rock target (0.92) is higher than pop's (0.8).
- **Chill Lofi vs. Deep Intense Rock:** complete opposites. Lofi rewards acousticness, rock (likes_acoustic = False) rewards produced/electric sound, and energy targets are 0.40 vs. 0.92. Zero overlap, which is exactly what should happen.
- **Deep Intense Rock vs. Conflicted (Sad but 0.9 Energy):** positions 2–5 are almost the same loud songs. This shows that when mood can't be satisfied, energy alone decides, and the "sad" preference is basically ignored after the first slot.
- **High-Energy Pop vs. Ghost Genre (K-pop):** both want "happy," so Rooftop Lights and Sunrise City appear in both. K-pop's lower energy target (0.6) pulls in calmer country, reggae and r&b songs that the pop profile never sees.
- **Chill Lofi vs. Out-of-Range Energy:** both want calm genres (lofi, classical), but the 1.5 energy target drags the classical profile's list toward the loudest songs in the catalog, the opposite of what a "peaceful classical" listener wants. Invalid input produces nonsense instead of an error.

### Experiment: weight shift (genre 2.0 → 1.0, energy 1.5 → 3.0)

Run with `python -m src.main --experiment`. The max possible score changes from 5.0 to 5.5, and every term stays non-negative for valid 0–1 energy targets, so the math is still valid.

| Profile | Baseline top 3 | Experiment top 3 |
|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, **Rooftop Lights**, Gym Hero |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | Midnight Coding, Library Rain, Focus Flow |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Overdrive | same |
| Conflicted | Rainy Day Blues (3.65), Storm Runner (1.48) | Rainy Day Blues (3.29), Storm Runner (**2.97**) |
| Out-of-Range Energy | Moonlit Sonata Redux, Iron Furnace | **Iron Furnace**, Pulse Overdrive (classical drops out) |

**More accurate or just different?** For High-Energy Pop it was **more accurate**: Rooftop Lights (happy, 0.76 energy) moved above Gym Hero (intense), which fits a "happy pop" listener better. For lofi and rock it was **just different**: tiny reshuffles among songs that were already right. For the out-of-range profile it was **worse**: the doubled energy penalty knocked the only classical song out of the top 5. Overall, lowering genre weight reduced the "label beats feel" problem but made the system even more energy-driven.

### Baseline output

```
=== High-Energy Pop ===  {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Sunrise City           | Neon Echo        | pop / happy            | 4.47   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.82 vs target 0.80 (+1.47)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Gym Hero               | Max Pulse        | pop / intense          | 3.30   | genre match (+2.0)                       |
|     |                        |                  |                        |        | energy 0.93 vs target 0.80 (+1.30)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Rooftop Lights         | Indigo Parade    | indie pop / happy      | 2.44   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.76 vs target 0.80 (+1.44)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Concrete Crown         | Verse Theory     | hip-hop / confident    | 1.47   | energy 0.78 vs target 0.80 (+1.47)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Night Drive Loop       | Neon Echo        | synthwave / moody      | 1.42   | energy 0.75 vs target 0.80 (+1.42)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Chill Lofi ===  {'genre': 'lofi', 'mood': 'chill', 'energy': 0.4, 'likes_acoustic': True}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Library Rain           | Paper Lanterns   | lofi / chill           | 4.85   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.35 vs target 0.40 (+1.42)       |
|     |                        |                  |                        |        | acoustic fit (+0.43)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Midnight Coding        | LoRoom           | lofi / chill           | 4.82   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.42 vs target 0.40 (+1.47)       |
|     |                        |                  |                        |        | acoustic fit (+0.35)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Focus Flow             | LoRoom           | lofi / focused         | 3.89   | genre match (+2.0)                       |
|     |                        |                  |                        |        | energy 0.40 vs target 0.40 (+1.50)       |
|     |                        |                  |                        |        | acoustic fit (+0.39)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Spacewalk Thoughts     | Orbit Bloom      | ambient / chill        | 2.78   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.28 vs target 0.40 (+1.32)       |
|     |                        |                  |                        |        | acoustic fit (+0.46)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Coffee Shop Stories    | Slow Stereo      | jazz / relaxed         | 1.90   | energy 0.37 vs target 0.40 (+1.46)       |
|     |                        |                  |                        |        | acoustic fit (+0.45)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Deep Intense Rock ===  {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'likes_acoustic': False}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Storm Runner           | Voltline         | rock / intense         | 4.93   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.91 vs target 0.92 (+1.48)       |
|     |                        |                  |                        |        | acoustic fit (+0.45)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Gym Hero               | Max Pulse        | pop / intense          | 2.96   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.93 vs target 0.92 (+1.48)       |
|     |                        |                  |                        |        | acoustic fit (+0.47)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 1.95   | energy 0.95 vs target 0.92 (+1.46)       |
|     |                        |                  |                        |        | acoustic fit (+0.49)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Iron Furnace           | Blackthorn       | metal / angry          | 1.91   | energy 0.97 vs target 0.92 (+1.43)       |
|     |                        |                  |                        |        | acoustic fit (+0.48)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Sunrise City           | Neon Echo        | pop / happy            | 1.76   | energy 0.82 vs target 0.92 (+1.35)       |
|     |                        |                  |                        |        | acoustic fit (+0.41)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Conflicted (Sad but 0.9 Energy) ===  {'genre': 'blues', 'mood': 'sad', 'energy': 0.9}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Rainy Day Blues        | Old Ellis        | blues / sad            | 3.65   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.33 vs target 0.90 (+0.64)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Storm Runner           | Voltline         | rock / intense         | 1.48   | energy 0.91 vs target 0.90 (+1.48)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Gym Hero               | Max Pulse        | pop / intense          | 1.46   | energy 0.93 vs target 0.90 (+1.46)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 1.43   | energy 0.95 vs target 0.90 (+1.43)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Iron Furnace           | Blackthorn       | metal / angry          | 1.40   | energy 0.97 vs target 0.90 (+1.40)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Ghost Genre (K-pop) ===  {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.6}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Rooftop Lights         | Indigo Parade    | indie pop / happy      | 2.26   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.76 vs target 0.60 (+1.26)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Sunrise City           | Neon Echo        | pop / happy            | 2.17   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.82 vs target 0.60 (+1.17)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Dusty Highway Home     | Wade Callahan    | country / nostalgic    | 1.43   | energy 0.55 vs target 0.60 (+1.43)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Island Breeze          | Sunny Roots      | reggae / relaxed       | 1.38   | energy 0.52 vs target 0.60 (+1.38)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Velvet Hours           | Amara Lane       | r&b / romantic         | 1.35   | energy 0.50 vs target 0.60 (+1.35)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Out-of-Range Energy (1.5) ===  {'genre': 'classical', 'mood': 'peaceful', 'energy': 1.5}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Moonlit Sonata Redux   | Clara Vane       | classical / peaceful   | 2.47   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.15 vs target 1.50 (+-0.53)      |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Iron Furnace           | Blackthorn       | metal / angry          | 0.70   | energy 0.97 vs target 1.50 (+0.70)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 0.67   | energy 0.95 vs target 1.50 (+0.67)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Gym Hero               | Max Pulse        | pop / intense          | 0.65   | energy 0.93 vs target 1.50 (+0.65)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Storm Runner           | Voltline         | rock / intense         | 0.61   | energy 0.91 vs target 1.50 (+0.61)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

### Diversity mode (fairness / filter-bubble fix)

Run with `python -m src.main --diverse`. While building the top 5, a song loses **1.0** point if its artist is already on the list and **0.5** if its genre is already on the list. The penalty shows up in the reasons, so nothing is hidden.

**Why it helps fairness:** without it, one artist or one genre can take over a whole list just because it matches the label, and other artists never get a chance to show up. The penalty doesn't ban repeats; a really strong match can still win. It just makes the system earn a repeat instead of handing it out for free.

**What changed:**

- **High-Energy Pop:** Night Drive Loop (a second Neon Echo song) dropped out and Storm Runner took its spot. Gym Hero's score fell from 3.30 to 2.80 because it's the second pop song, but it still held #2.
- **Chill Lofi:** Spacewalk Thoughts (ambient) moved above Focus Flow, which was the second LoRoom song *and* the third lofi song. The list now has three genres instead of two.
- **Deep Intense Rock:** Sunrise City (a second pop song) was replaced by Concrete Crown (hip-hop).
- **Conflicted, K-pop, Out-of-Range:** no change, because their top 5 already had different artists and genres.

It didn't fix everything. Gym Hero still shows up in four lists, because the penalty only looks at repeats *inside* one list, not across different users.

```
=== High-Energy Pop ===  {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Sunrise City           | Neon Echo        | pop / happy            | 4.47   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.82 vs target 0.80 (+1.47)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Gym Hero               | Max Pulse        | pop / intense          | 2.80   | genre match (+2.0)                       |
|     |                        |                  |                        |        | energy 0.93 vs target 0.80 (+1.30)       |
|     |                        |                  |                        |        | repeat genre penalty (-0.5)              |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Rooftop Lights         | Indigo Parade    | indie pop / happy      | 2.44   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.76 vs target 0.80 (+1.44)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Concrete Crown         | Verse Theory     | hip-hop / confident    | 1.47   | energy 0.78 vs target 0.80 (+1.47)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Storm Runner           | Voltline         | rock / intense         | 1.33   | energy 0.91 vs target 0.80 (+1.33)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Chill Lofi ===  {'genre': 'lofi', 'mood': 'chill', 'energy': 0.4, 'likes_acoustic': True}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Library Rain           | Paper Lanterns   | lofi / chill           | 4.85   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.35 vs target 0.40 (+1.42)       |
|     |                        |                  |                        |        | acoustic fit (+0.43)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Midnight Coding        | LoRoom           | lofi / chill           | 4.32   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.42 vs target 0.40 (+1.47)       |
|     |                        |                  |                        |        | acoustic fit (+0.35)                     |
|     |                        |                  |                        |        | repeat genre penalty (-0.5)              |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Spacewalk Thoughts     | Orbit Bloom      | ambient / chill        | 2.78   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.28 vs target 0.40 (+1.32)       |
|     |                        |                  |                        |        | acoustic fit (+0.46)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Focus Flow             | LoRoom           | lofi / focused         | 2.39   | genre match (+2.0)                       |
|     |                        |                  |                        |        | energy 0.40 vs target 0.40 (+1.50)       |
|     |                        |                  |                        |        | acoustic fit (+0.39)                     |
|     |                        |                  |                        |        | repeat artist penalty (-1.0)             |
|     |                        |                  |                        |        | repeat genre penalty (-0.5)              |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Coffee Shop Stories    | Slow Stereo      | jazz / relaxed         | 1.90   | energy 0.37 vs target 0.40 (+1.46)       |
|     |                        |                  |                        |        | acoustic fit (+0.45)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Deep Intense Rock ===  {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'likes_acoustic': False}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Storm Runner           | Voltline         | rock / intense         | 4.93   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.91 vs target 0.92 (+1.48)       |
|     |                        |                  |                        |        | acoustic fit (+0.45)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Gym Hero               | Max Pulse        | pop / intense          | 2.96   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.93 vs target 0.92 (+1.48)       |
|     |                        |                  |                        |        | acoustic fit (+0.47)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 1.95   | energy 0.95 vs target 0.92 (+1.46)       |
|     |                        |                  |                        |        | acoustic fit (+0.49)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Iron Furnace           | Blackthorn       | metal / angry          | 1.91   | energy 0.97 vs target 0.92 (+1.43)       |
|     |                        |                  |                        |        | acoustic fit (+0.48)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Concrete Crown         | Verse Theory     | hip-hop / confident    | 1.75   | energy 0.78 vs target 0.92 (+1.29)       |
|     |                        |                  |                        |        | acoustic fit (+0.46)                     |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Conflicted (Sad but 0.9 Energy) ===  {'genre': 'blues', 'mood': 'sad', 'energy': 0.9}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Rainy Day Blues        | Old Ellis        | blues / sad            | 3.65   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.33 vs target 0.90 (+0.64)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Storm Runner           | Voltline         | rock / intense         | 1.48   | energy 0.91 vs target 0.90 (+1.48)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Gym Hero               | Max Pulse        | pop / intense          | 1.46   | energy 0.93 vs target 0.90 (+1.46)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 1.43   | energy 0.95 vs target 0.90 (+1.43)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Iron Furnace           | Blackthorn       | metal / angry          | 1.40   | energy 0.97 vs target 0.90 (+1.40)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Ghost Genre (K-pop) ===  {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.6}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Rooftop Lights         | Indigo Parade    | indie pop / happy      | 2.26   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.76 vs target 0.60 (+1.26)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Sunrise City           | Neon Echo        | pop / happy            | 2.17   | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.82 vs target 0.60 (+1.17)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Dusty Highway Home     | Wade Callahan    | country / nostalgic    | 1.43   | energy 0.55 vs target 0.60 (+1.43)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Island Breeze          | Sunny Roots      | reggae / relaxed       | 1.38   | energy 0.52 vs target 0.60 (+1.38)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Velvet Hours           | Amara Lane       | r&b / romantic         | 1.35   | energy 0.50 vs target 0.60 (+1.35)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

```
=== Out-of-Range Energy (1.5) ===  {'genre': 'classical', 'mood': 'peaceful', 'energy': 1.5}
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| #   | Title                  | Artist           | Genre / Mood           | Score  | Reasons                                  |
+=====+========================+==================+========================+========+==========================================+
| 1   | Moonlit Sonata Redux   | Clara Vane       | classical / peaceful   | 2.47   | genre match (+2.0)                       |
|     |                        |                  |                        |        | mood match (+1.0)                        |
|     |                        |                  |                        |        | energy 0.15 vs target 1.50 (+-0.53)      |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 2   | Iron Furnace           | Blackthorn       | metal / angry          | 0.70   | energy 0.97 vs target 1.50 (+0.70)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 3   | Pulse Overdrive        | Kilowatt         | edm / energetic        | 0.67   | energy 0.95 vs target 1.50 (+0.67)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 4   | Gym Hero               | Max Pulse        | pop / intense          | 0.65   | energy 0.93 vs target 1.50 (+0.65)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
| 5   | Storm Runner           | Voltline         | rock / intense         | 0.61   | energy 0.91 vs target 1.50 (+0.61)       |
+-----+------------------------+------------------+------------------------+--------+------------------------------------------+
```

---

## 8. Future Work  

1. **Fuzzy genre and mood matching.** Give partial credit for related labels ("indie pop" is close to "pop", "relaxed" is close to "chill") instead of all-or-nothing.
2. **Validate input and add a "nothing fits" signal.** Reject or clamp energy targets outside 0 to 1 (this would fix the negative score I found), and warn the user when even the top song has a low score.
3. **Stronger diversity.** I added an artist/genre repeat penalty (`--diverse`), but it only works inside one list. Next I'd try something that also rewards songs that rarely get recommended, so the same few songs (like Gym Hero) don't show up for everyone.

---

## 9. Personal Reflection  

My biggest learning moment was the sad but high-energy profile. I knew it would struggle, but I didn't expect it to fail so confidently. It gave me one slow blues song and then four loud workout songs, each with a score and a list of reasons that looked totally legit. That's when I realized the reasons only explain what the math did. They don't tell you if the recommendation is actually any good.

Using AI sped things up a lot. It helped me add songs to the dataset, write the scoring and sorting code, clean up the terminal output, and come up with edge cases I wouldn't have thought of, like an energy target of 1.5. But I still had to check its work. It broke `main.py` with a syntax error at one point, the starter import had to be fixed before `python -m src.main` would even run, and I had to look at the math to notice that out-of-range energy gives a negative score. I also had to decide for myself what counted as a bug to fix versus a weakness to write up.

What surprised me most is how real it feels. For my lofi profile, the top picks honestly looked like a playlist I'd make for studying at night, and the system has no idea what any of the songs sound like. It's just adding up points. It makes me look at the "made for you" stuff on real apps a little differently now.

If I kept going, I'd add partial credit for similar genres and moods (indie pop should count a little for pop), something that pushes the same few songs (like Gym Hero) out of every list, since my diversity penalty only fixes repeats inside one list, and maybe a basic "people who liked this also liked" layer to see how collaborative filtering changes things.
