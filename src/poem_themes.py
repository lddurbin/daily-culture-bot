#!/usr/bin/env python3
"""
Poem Theme Mappings for Daily Culture Bot

This module contains theme and emotion mappings used for poem analysis
and artwork matching. These mappings connect poem themes and emotions
to Wikidata Q-codes for complementary artwork selection.
"""

# Theme keywords and their corresponding Wikidata Q-codes
THEME_MAPPINGS = {
    "nature": {
        "keywords": [
            "nature", "natural", "wild", "wilderness", "forest", "wood", "woods",
            "tree", "trees", "leaf", "leaves", "green", "earth", "ground", "land",
            "countryside", "country", "rural", "pastoral", "meadow", "field", "fields"
        ],
        "q_codes": ["Q7860", "Q23397", "Q1640824"]  # nature, landscape, floral painting
    },
    "flowers": {
        "keywords": [
            "flower", "flowers", "bloom", "blooms", "blossom", "blossoms", "petal", "petals",
            "rose", "roses", "daffodil", "daffodils", "lily", "lilies", "tulip", "tulips",
            "garden", "gardens", "floral", "botanical", "spring", "springtime"
        ],
        "q_codes": ["Q506", "Q1640824", "Q16538"]  # flower, floral painting, romantic
    },
    "water": {
        "keywords": [
            "water", "sea", "ocean", "lake", "river", "stream", "brook", "pond", "pool",
            "wave", "waves", "tide", "tides", "rain", "rainy", "storm", "storms",
            "sail", "sailing", "boat", "boats", "ship", "ships", "fishing", "fisherman"
        ],
        "q_codes": ["Q283", "Q16970", "Q131681", "Q18811"]  # water, sea, seascape, battle
    },
    "love": {
        "keywords": [
            "love", "loved", "loving", "beloved", "heart", "hearts", "romance", "romantic",
            "kiss", "kisses", "embrace", "embraces", "passion", "passionate", "desire",
            "affection", "tender", "sweet", "dear", "darling", "lover", "lovers"
        ],
        "q_codes": ["Q316", "Q16538", "Q506"]  # love, romantic, flower
    },
    "death": {
        "keywords": [
            "death", "die", "dies", "died", "dying", "dead", "grave", "graves", "burial",
            "funeral", "mourning", "grief", "sorrow", "sad", "sadness", "tears", "weep",
            "weeping", "memorial", "remembrance", "ghost", "ghosts", "spirit", "spirits",
            "dust", "ashes", "epitaph", "tomb", "cemetery"
        ],
        "q_codes": ["Q4", "Q198", "Q18811"]  # death, war, battle
    },
    "war": {
        "keywords": [
            "war", "wars", "warfare", "battle", "battles", "fight", "fighting", "soldier",
            "soldiers", "army", "armies", "weapon", "weapons", "sword", "swords", "gun",
            "guns", "bomb", "bombs", "conflict", "conflicts", "struggle", "struggles"
        ],
        "q_codes": ["Q198", "Q18811", "Q4"]  # war, battle, death
    },
    "night": {
        "keywords": [
            "night", "nights", "dark", "darkness", "midnight", "evening", "evenings",
            "dusk", "twilight", "moon", "moonlight", "stars", "starry", "sleep", "sleeping",
            "dream", "dreams", "dreaming", "shadow", "shadows", "black"
        ],
        "q_codes": ["Q183", "Q111", "Q12133"]  # night, darkness, sleep
    },
    "day": {
        "keywords": [
            "day", "days", "morning", "mornings", "dawn", "sunrise", "sun", "sunny",
            "bright", "light", "lightness", "daylight", "noon", "afternoon", "golden",
            "yellow", "warm", "warmth", "clear", "blue", "sky", "skies"
        ],
        "q_codes": ["Q111", "Q525", "Q12133"]  # day, sun, light
    },
    "city": {
        "keywords": [
            "city", "cities", "urban", "town", "towns", "street", "streets", "road", "roads",
            "building", "buildings", "house", "houses", "home", "homes", "window", "windows",
            "door", "doors", "wall", "walls", "roof", "roofs", "crowd", "crowds", "people"
        ],
        "q_codes": ["Q515", "Q395", "Q18811"]  # city, building, battle
    },
    "animals": {
        "keywords": [
            "animal", "animals", "bird", "birds", "dog", "dogs", "cat", "cats", "horse",
            "horses", "cow", "cows", "sheep", "lamb", "lambs", "wolf", "wolves", "lion",
            "lions", "eagle", "eagles", "swan", "swans", "butterfly", "butterflies"
        ],
        "q_codes": ["Q729", "Q5113", "Q1640824"]  # animal, bird, floral painting
    },
    "seasons": {
        "keywords": [
            "spring", "summer", "autumn", "fall", "winter", "season", "seasons", "year",
            "years", "time", "times", "change", "changes", "new", "old", "young", "age"
        ],
        "q_codes": ["Q395", "Q12133", "Q23397"]  # building, light, landscape
    }
}

# Emotion-aware mappings for better artwork matching
EMOTION_MAPPINGS = {
    "grief": {
        "q_codes": ["Q4", "Q203", "Q2912397", "Q3305213"],  # death, mourning, memorial, painting
        "genres": ["Q134307", "Q2839016"],  # portrait, religious painting
        "keywords": ["mourning", "memorial", "sorrow", "loss", "burial", "pietà", "funeral", "grave"]
    },
    "melancholy": {
        "q_codes": ["Q183", "Q8886", "Q35127"],  # night, loneliness, solitude
        "genres": ["Q191163", "Q40446"],  # landscape, nocturne
        "keywords": ["solitary", "twilight", "contemplative", "pensive", "sad", "blue", "lonely"]
    },
    "joy": {
        "q_codes": ["Q2385804", "Q8274", "Q1068639"],  # celebration, dance, festival
        "genres": ["Q16875712", "Q1640824"],  # genre painting, floral painting
        "keywords": ["celebration", "dance", "festive", "bright", "colorful", "happy", "merry"]
    },
    "peace": {
        "q_codes": ["Q23397", "Q35127", "Q483130"],  # landscape, solitude, pastoral
        "genres": ["Q191163", "Q1640824"],  # landscape, still life
        "keywords": ["pastoral", "serene", "calm", "quiet", "peaceful", "tranquil", "gentle"]
    },
    "love": {
        "q_codes": ["Q316", "Q16538", "Q506"],  # love, romantic, flower
        "genres": ["Q134307", "Q1640824"],  # portrait, floral painting
        "keywords": ["romance", "passion", "tender", "sweet", "beloved", "heart", "kiss"]
    },
    "hope": {
        "q_codes": ["Q111", "Q525", "Q12133"],  # day, sun, light
        "genres": ["Q191163", "Q1640824"],  # landscape, floral painting
        "keywords": ["dawn", "morning", "bright", "promise", "future", "renewal", "spring"]
    },
    "despair": {
        "q_codes": ["Q183", "Q4", "Q8886"],  # night, death, loneliness
        "genres": ["Q191163", "Q134307"],  # landscape, portrait
        "keywords": ["dark", "hopeless", "empty", "void", "end", "nothing", "lost"]
    },
    "nostalgia": {
        "q_codes": ["Q23397", "Q35127", "Q395"],  # landscape, solitude, building
        "genres": ["Q191163", "Q134307"],  # landscape, portrait
        "keywords": ["memory", "past", "old", "remember", "childhood", "home", "familiar"]
    }
}
