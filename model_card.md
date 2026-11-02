# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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
------------------------------------------------------------
1. Sunrise City by Neon Echo  [pop/happy]
   Score: 4.47
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 3.30
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
3. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 2.44
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
4. Concrete Crown by Verse Theory  [hip-hop/confident]
   Score: 1.47
     - energy 0.78 vs target 0.80 (+1.47)
5. Night Drive Loop by Neon Echo  [synthwave/moody]
   Score: 1.42
     - energy 0.75 vs target 0.80 (+1.42)
```

```
=== Chill Lofi ===  {'genre': 'lofi', 'mood': 'chill', 'energy': 0.4, 'likes_acoustic': True}
------------------------------------------------------------
1. Library Rain by Paper Lanterns  [lofi/chill]
   Score: 4.85
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.40 (+1.42)
     - acoustic fit (+0.43)
2. Midnight Coding by LoRoom  [lofi/chill]
   Score: 4.82
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.40 (+1.47)
     - acoustic fit (+0.35)
3. Focus Flow by LoRoom  [lofi/focused]
   Score: 3.89
     - genre match (+2.0)
     - energy 0.40 vs target 0.40 (+1.50)
     - acoustic fit (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  [ambient/chill]
   Score: 2.78
     - mood match (+1.0)
     - energy 0.28 vs target 0.40 (+1.32)
     - acoustic fit (+0.46)
5. Coffee Shop Stories by Slow Stereo  [jazz/relaxed]
   Score: 1.90
     - energy 0.37 vs target 0.40 (+1.46)
     - acoustic fit (+0.45)
```

```
=== Deep Intense Rock ===  {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'likes_acoustic': False}
------------------------------------------------------------
1. Storm Runner by Voltline  [rock/intense]
   Score: 4.93
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.92 (+1.48)
     - acoustic fit (+0.45)
2. Gym Hero by Max Pulse  [pop/intense]
   Score: 2.96
     - mood match (+1.0)
     - energy 0.93 vs target 0.92 (+1.48)
     - acoustic fit (+0.47)
3. Pulse Overdrive by Kilowatt  [edm/energetic]
   Score: 1.95
     - energy 0.95 vs target 0.92 (+1.46)
     - acoustic fit (+0.49)
4. Iron Furnace by Blackthorn  [metal/angry]
   Score: 1.91
     - energy 0.97 vs target 0.92 (+1.43)
     - acoustic fit (+0.48)
5. Sunrise City by Neon Echo  [pop/happy]
   Score: 1.76
     - energy 0.82 vs target 0.92 (+1.35)
     - acoustic fit (+0.41)
```

```
=== Conflicted (Sad but 0.9 Energy) ===  {'genre': 'blues', 'mood': 'sad', 'energy': 0.9}
------------------------------------------------------------
1. Rainy Day Blues by Old Ellis  [blues/sad]
   Score: 3.65
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.33 vs target 0.90 (+0.64)
2. Storm Runner by Voltline  [rock/intense]
   Score: 1.48
     - energy 0.91 vs target 0.90 (+1.48)
3. Gym Hero by Max Pulse  [pop/intense]
   Score: 1.46
     - energy 0.93 vs target 0.90 (+1.46)
4. Pulse Overdrive by Kilowatt  [edm/energetic]
   Score: 1.43
     - energy 0.95 vs target 0.90 (+1.43)
5. Iron Furnace by Blackthorn  [metal/angry]
   Score: 1.40
     - energy 0.97 vs target 0.90 (+1.40)
```

```
=== Ghost Genre (K-pop) ===  {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.6}
------------------------------------------------------------
1. Rooftop Lights by Indigo Parade  [indie pop/happy]
   Score: 2.26
     - mood match (+1.0)
     - energy 0.76 vs target 0.60 (+1.26)
2. Sunrise City by Neon Echo  [pop/happy]
   Score: 2.17
     - mood match (+1.0)
     - energy 0.82 vs target 0.60 (+1.17)
3. Dusty Highway Home by Wade Callahan  [country/nostalgic]
   Score: 1.43
     - energy 0.55 vs target 0.60 (+1.43)
4. Island Breeze by Sunny Roots  [reggae/relaxed]
   Score: 1.38
     - energy 0.52 vs target 0.60 (+1.38)
5. Velvet Hours by Amara Lane  [r&b/romantic]
   Score: 1.35
     - energy 0.50 vs target 0.60 (+1.35)
```

```
=== Out-of-Range Energy (1.5) ===  {'genre': 'classical', 'mood': 'peaceful', 'energy': 1.5}
------------------------------------------------------------
1. Moonlit Sonata Redux by Clara Vane  [classical/peaceful]
   Score: 2.47
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.15 vs target 1.50 (+-0.53)
2. Iron Furnace by Blackthorn  [metal/angry]
   Score: 0.70
     - energy 0.97 vs target 1.50 (+0.70)
3. Pulse Overdrive by Kilowatt  [edm/energetic]
   Score: 0.67
     - energy 0.95 vs target 1.50 (+0.67)
4. Gym Hero by Max Pulse  [pop/intense]
   Score: 0.65
     - energy 0.93 vs target 1.50 (+0.65)
5. Storm Runner by Voltline  [rock/intense]
   Score: 0.61
     - energy 0.91 vs target 1.50 (+0.61)
```

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
