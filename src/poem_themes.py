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

# Comprehensive object-to-Q-code mappings for concrete element extraction
OBJECT_MAPPINGS = {
    # Natural objects
    "tree": {"q_codes": ["Q10884"], "keywords": ["tree", "trees", "oak", "pine", "maple", "birch", "willow"]},
    "trees": {"q_codes": ["Q10884"], "keywords": ["tree", "trees", "oak", "pine", "maple", "birch", "willow"]},
    "forest": {"q_codes": ["Q4421"], "keywords": ["forest", "wood", "woods", "grove", "thicket"]},
    "flower": {"q_codes": ["Q11427"], "keywords": ["flower", "flowers", "bloom", "blossom", "petal"]},
    "flowers": {"q_codes": ["Q11427"], "keywords": ["flower", "flowers", "bloom", "blossom", "petal"]},
    "rose": {"q_codes": ["Q11427"], "keywords": ["rose", "roses"]},
    "roses": {"q_codes": ["Q11427"], "keywords": ["rose", "roses"]},
    "ocean": {"q_codes": ["Q9430"], "keywords": ["ocean", "oceans", "sea", "seas"]},
    "sea": {"q_codes": ["Q9430"], "keywords": ["ocean", "oceans", "sea", "seas"]},
    "water": {"q_codes": ["Q283"], "keywords": ["water", "lake", "river", "stream", "pond"]},
    "lake": {"q_codes": ["Q23397"], "keywords": ["lake", "lakes", "pond", "ponds"]},
    "river": {"q_codes": ["Q4022"], "keywords": ["river", "rivers", "stream", "streams", "brook"]},
    "mountain": {"q_codes": ["Q8502"], "keywords": ["mountain", "mountains", "hill", "hills", "peak", "peaks"]},
    "mountains": {"q_codes": ["Q8502"], "keywords": ["mountain", "mountains", "hill", "hills", "peak", "peaks"]},
    "sky": {"q_codes": ["Q526"], "keywords": ["sky", "skies", "heaven", "heavens"]},
    "cloud": {"q_codes": ["Q12539"], "keywords": ["cloud", "clouds", "cloudy"]},
    "clouds": {"q_codes": ["Q12539"], "keywords": ["cloud", "clouds", "cloudy"]},
    "star": {"q_codes": ["Q523"], "keywords": ["star", "stars", "starry"]},
    "stars": {"q_codes": ["Q523"], "keywords": ["star", "stars", "starry"]},
    "moon": {"q_codes": ["Q405"], "keywords": ["moon", "lunar", "moonlight"]},
    "sun": {"q_codes": ["Q525"], "keywords": ["sun", "sunny", "sunlight", "solar"]},
    "wind": {"q_codes": ["Q498"], "keywords": ["wind", "windy", "breeze", "breezy"]},
    "rain": {"q_codes": ["Q1165"], "keywords": ["rain", "rainy", "rainfall", "drizzle"]},
    "snow": {"q_codes": ["Q12133"], "keywords": ["snow", "snowy", "snowfall", "white"]},
    "fire": {"q_codes": ["Q221"], "keywords": ["fire", "flame", "flames", "burning"]},
    "earth": {"q_codes": ["Q2"], "keywords": ["earth", "ground", "soil", "land"]},
    "stone": {"q_codes": ["Q22731"], "keywords": ["stone", "stones", "rock", "rocks"]},
    "stones": {"q_codes": ["Q22731"], "keywords": ["stone", "stones", "rock", "rocks"]},
    "rock": {"q_codes": ["Q22731"], "keywords": ["stone", "stones", "rock", "rocks"]},
    "rocks": {"q_codes": ["Q22731"], "keywords": ["stone", "stones", "rock", "rocks"]},
    
    # Man-made objects
    "house": {"q_codes": ["Q3947"], "keywords": ["house", "houses", "home", "homes", "dwelling"]},
    "houses": {"q_codes": ["Q3947"], "keywords": ["house", "houses", "home", "homes", "dwelling"]},
    "building": {"q_codes": ["Q41176"], "keywords": ["building", "buildings", "structure", "structures"]},
    "buildings": {"q_codes": ["Q41176"], "keywords": ["building", "buildings", "structure", "structures"]},
    "church": {"q_codes": ["Q16970"], "keywords": ["church", "churches", "cathedral", "chapel"]},
    "churches": {"q_codes": ["Q16970"], "keywords": ["church", "churches", "cathedral", "chapel"]},
    "castle": {"q_codes": ["Q23413"], "keywords": ["castle", "castles", "fortress", "palace"]},
    "castles": {"q_codes": ["Q23413"], "keywords": ["castle", "castles", "fortress", "palace"]},
    "bridge": {"q_codes": ["Q12280"], "keywords": ["bridge", "bridges", "span"]},
    "bridges": {"q_codes": ["Q12280"], "keywords": ["bridge", "bridges", "span"]},
    "road": {"q_codes": ["Q34442"], "keywords": ["road", "roads", "street", "streets", "path", "paths"]},
    "roads": {"q_codes": ["Q34442"], "keywords": ["road", "roads", "street", "streets", "path", "paths"]},
    "street": {"q_codes": ["Q34442"], "keywords": ["road", "roads", "street", "streets", "path", "paths"]},
    "streets": {"q_codes": ["Q34442"], "keywords": ["road", "roads", "street", "streets", "path", "paths"]},
    "door": {"q_codes": ["Q11446"], "keywords": ["door", "doors", "gate", "gates"]},
    "doors": {"q_codes": ["Q11446"], "keywords": ["door", "doors", "gate", "gates"]},
    "window": {"q_codes": ["Q101095"], "keywords": ["window", "windows", "glass"]},
    "windows": {"q_codes": ["Q101095"], "keywords": ["window", "windows", "glass"]},
    "wall": {"q_codes": ["Q12323"], "keywords": ["wall", "walls", "barrier"]},
    "walls": {"q_codes": ["Q12323"], "keywords": ["wall", "walls", "barrier"]},
    "roof": {"q_codes": ["Q12323"], "keywords": ["roof", "roofs", "ceiling"]},
    "roofs": {"q_codes": ["Q12323"], "keywords": ["roof", "roofs", "ceiling"]},
    "tower": {"q_codes": ["Q12516"], "keywords": ["tower", "towers", "spire", "spires"]},
    "towers": {"q_codes": ["Q12516"], "keywords": ["tower", "towers", "spire", "spires"]},
    "ship": {"q_codes": ["Q11446"], "keywords": ["ship", "ships", "boat", "boats", "vessel"]},
    "ships": {"q_codes": ["Q11446"], "keywords": ["ship", "ships", "boat", "boats", "vessel"]},
    "boat": {"q_codes": ["Q11446"], "keywords": ["ship", "ships", "boat", "boats", "vessel"]},
    "boats": {"q_codes": ["Q11446"], "keywords": ["ship", "ships", "boat", "boats", "vessel"]},
    "car": {"q_codes": ["Q1420"], "keywords": ["car", "cars", "automobile", "vehicle"]},
    "cars": {"q_codes": ["Q1420"], "keywords": ["car", "cars", "automobile", "vehicle"]},
    "train": {"q_codes": ["Q198"], "keywords": ["train", "trains", "locomotive", "railway"]},
    "trains": {"q_codes": ["Q198"], "keywords": ["train", "trains", "locomotive", "railway"]},
    "book": {"q_codes": ["Q571"], "keywords": ["book", "books", "volume", "tome"]},
    "books": {"q_codes": ["Q571"], "keywords": ["book", "books", "volume", "tome"]},
    "table": {"q_codes": ["Q11446"], "keywords": ["table", "tables", "desk", "surface"]},
    "tables": {"q_codes": ["Q11446"], "keywords": ["table", "tables", "desk", "surface"]},
    "chair": {"q_codes": ["Q11446"], "keywords": ["chair", "chairs", "seat", "seats"]},
    "chairs": {"q_codes": ["Q11446"], "keywords": ["chair", "chairs", "seat", "seats"]},
    "bed": {"q_codes": ["Q11446"], "keywords": ["bed", "beds", "sleeping", "rest"]},
    "beds": {"q_codes": ["Q11446"], "keywords": ["bed", "beds", "sleeping", "rest"]},
    "sword": {"q_codes": ["Q11446"], "keywords": ["sword", "swords", "blade", "blades"]},
    "swords": {"q_codes": ["Q11446"], "keywords": ["sword", "swords", "blade", "blades"]},
    "gun": {"q_codes": ["Q11446"], "keywords": ["gun", "guns", "weapon", "weapons"]},
    "guns": {"q_codes": ["Q11446"], "keywords": ["gun", "guns", "weapon", "weapons"]},
    "weapon": {"q_codes": ["Q11446"], "keywords": ["gun", "guns", "weapon", "weapons"]},
    "weapons": {"q_codes": ["Q11446"], "keywords": ["gun", "guns", "weapon", "weapons"]},
    "tool": {"q_codes": ["Q11446"], "keywords": ["tool", "tools", "implement", "implements"]},
    "tools": {"q_codes": ["Q11446"], "keywords": ["tool", "tools", "implement", "implements"]},
    "machine": {"q_codes": ["Q11446"], "keywords": ["machine", "machines", "device", "devices"]},
    "machines": {"q_codes": ["Q11446"], "keywords": ["machine", "machines", "device", "devices"]},
    "engine": {"q_codes": ["Q11446"], "keywords": ["engine", "engines", "motor", "motors"]},
    "engines": {"q_codes": ["Q11446"], "keywords": ["engine", "engines", "motor", "motors"]},
    
    # Living beings
    "man": {"q_codes": ["Q8441"], "keywords": ["man", "men", "male", "males", "gentleman"]},
    "men": {"q_codes": ["Q8441"], "keywords": ["man", "men", "male", "males", "gentleman"]},
    "woman": {"q_codes": ["Q467"], "keywords": ["woman", "women", "female", "females", "lady"]},
    "women": {"q_codes": ["Q467"], "keywords": ["woman", "women", "female", "females", "lady"]},
    "child": {"q_codes": ["Q7569"], "keywords": ["child", "children", "kid", "kids", "youth"]},
    "children": {"q_codes": ["Q7569"], "keywords": ["child", "children", "kid", "kids", "youth"]},
    "boy": {"q_codes": ["Q7569"], "keywords": ["boy", "boys", "male child"]},
    "boys": {"q_codes": ["Q7569"], "keywords": ["boy", "boys", "male child"]},
    "girl": {"q_codes": ["Q7569"], "keywords": ["girl", "girls", "female child"]},
    "girls": {"q_codes": ["Q7569"], "keywords": ["girl", "girls", "female child"]},
    "person": {"q_codes": ["Q5"], "keywords": ["person", "people", "human", "humans", "individual"]},
    "people": {"q_codes": ["Q5"], "keywords": ["person", "people", "human", "humans", "individual"]},
    "human": {"q_codes": ["Q5"], "keywords": ["person", "people", "human", "humans", "individual"]},
    "humans": {"q_codes": ["Q5"], "keywords": ["person", "people", "human", "humans", "individual"]},
    "soldier": {"q_codes": ["Q499"], "keywords": ["soldier", "soldiers", "warrior", "warriors"]},
    "soldiers": {"q_codes": ["Q499"], "keywords": ["soldier", "soldiers", "warrior", "warriors"]},
    "king": {"q_codes": ["Q304"], "keywords": ["king", "kings", "monarch", "monarchs", "ruler"]},
    "kings": {"q_codes": ["Q304"], "keywords": ["king", "kings", "monarch", "monarchs", "ruler"]},
    "queen": {"q_codes": ["Q304"], "keywords": ["queen", "queens", "monarch", "monarchs", "ruler"]},
    "queens": {"q_codes": ["Q304"], "keywords": ["queen", "queens", "monarch", "monarchs", "ruler"]},
    "prince": {"q_codes": ["Q304"], "keywords": ["prince", "princes", "royal", "royalty"]},
    "princes": {"q_codes": ["Q304"], "keywords": ["prince", "princes", "royal", "royalty"]},
    "princess": {"q_codes": ["Q304"], "keywords": ["princess", "princesses", "royal", "royalty"]},
    "princesses": {"q_codes": ["Q304"], "keywords": ["princess", "princesses", "royal", "royalty"]},
    
    # Animals
    "dog": {"q_codes": ["Q144"], "keywords": ["dog", "dogs", "puppy", "puppies", "canine"]},
    "dogs": {"q_codes": ["Q144"], "keywords": ["dog", "dogs", "puppy", "puppies", "canine"]},
    "cat": {"q_codes": ["Q146"], "keywords": ["cat", "cats", "kitten", "kittens", "feline"]},
    "cats": {"q_codes": ["Q146"], "keywords": ["cat", "cats", "kitten", "kittens", "feline"]},
    "horse": {"q_codes": ["Q726"], "keywords": ["horse", "horses", "stallion", "mare", "pony"]},
    "horses": {"q_codes": ["Q726"], "keywords": ["horse", "horses", "stallion", "mare", "pony"]},
    "cow": {"q_codes": ["Q252"], "keywords": ["cow", "cows", "cattle", "bull", "bulls"]},
    "cows": {"q_codes": ["Q252"], "keywords": ["cow", "cows", "cattle", "bull", "bulls"]},
    "sheep": {"q_codes": ["Q736"], "keywords": ["sheep", "lamb", "lambs", "ewe", "ram"]},
    "lamb": {"q_codes": ["Q736"], "keywords": ["sheep", "lamb", "lambs", "ewe", "ram"]},
    "lambs": {"q_codes": ["Q736"], "keywords": ["sheep", "lamb", "lambs", "ewe", "ram"]},
    "wolf": {"q_codes": ["Q737"], "keywords": ["wolf", "wolves", "pack", "alpha"]},
    "wolves": {"q_codes": ["Q737"], "keywords": ["wolf", "wolves", "pack", "alpha"]},
    "lion": {"q_codes": ["Q140"], "keywords": ["lion", "lions", "king of beasts"]},
    "lions": {"q_codes": ["Q140"], "keywords": ["lion", "lions", "king of beasts"]},
    "bird": {"q_codes": ["Q5113"], "keywords": ["bird", "birds", "avian", "flying"]},
    "birds": {"q_codes": ["Q5113"], "keywords": ["bird", "birds", "avian", "flying"]},
    "eagle": {"q_codes": ["Q5113"], "keywords": ["eagle", "eagles", "bird of prey"]},
    "eagles": {"q_codes": ["Q5113"], "keywords": ["eagle", "eagles", "bird of prey"]},
    "swan": {"q_codes": ["Q5113"], "keywords": ["swan", "swans", "elegant bird"]},
    "swans": {"q_codes": ["Q5113"], "keywords": ["swan", "swans", "elegant bird"]},
    "butterfly": {"q_codes": ["Q5113"], "keywords": ["butterfly", "butterflies", "winged insect"]},
    "butterflies": {"q_codes": ["Q5113"], "keywords": ["butterfly", "butterflies", "winged insect"]},
    "fish": {"q_codes": ["Q152"], "keywords": ["fish", "fishes", "aquatic", "swimming"]},
    "fishes": {"q_codes": ["Q152"], "keywords": ["fish", "fishes", "aquatic", "swimming"]},
    "animal": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    "animals": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    "beast": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    "beasts": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    "creature": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    "creatures": {"q_codes": ["Q729"], "keywords": ["animal", "animals", "creature", "creatures", "beast"]},
    
    # Settings
    "garden": {"q_codes": ["Q1107656"], "keywords": ["garden", "gardens", "yard", "yards", "plot"]},
    "gardens": {"q_codes": ["Q1107656"], "keywords": ["garden", "gardens", "yard", "yards", "plot"]},
    "field": {"q_codes": ["Q23397"], "keywords": ["field", "fields", "meadow", "meadows", "pasture"]},
    "fields": {"q_codes": ["Q23397"], "keywords": ["field", "fields", "meadow", "meadows", "pasture"]},
    "meadow": {"q_codes": ["Q23397"], "keywords": ["field", "fields", "meadow", "meadows", "pasture"]},
    "meadows": {"q_codes": ["Q23397"], "keywords": ["field", "fields", "meadow", "meadows", "pasture"]},
    "valley": {"q_codes": ["Q23397"], "keywords": ["valley", "valleys", "dale", "dales", "hollow"]},
    "valleys": {"q_codes": ["Q23397"], "keywords": ["valley", "valleys", "dale", "dales", "hollow"]},
    "desert": {"q_codes": ["Q23397"], "keywords": ["desert", "deserts", "sandy", "arid"]},
    "deserts": {"q_codes": ["Q23397"], "keywords": ["desert", "deserts", "sandy", "arid"]},
    "city": {"q_codes": ["Q515"], "keywords": ["city", "cities", "urban", "metropolis"]},
    "cities": {"q_codes": ["Q515"], "keywords": ["city", "cities", "urban", "metropolis"]},
    "town": {"q_codes": ["Q515"], "keywords": ["town", "towns", "settlement", "settlements"]},
    "towns": {"q_codes": ["Q515"], "keywords": ["town", "towns", "settlement", "settlements"]},
    "village": {"q_codes": ["Q515"], "keywords": ["village", "villages", "hamlet", "hamlets"]},
    "villages": {"q_codes": ["Q515"], "keywords": ["village", "villages", "hamlet", "hamlets"]},
    "home": {"q_codes": ["Q3947"], "keywords": ["home", "homes", "house", "houses", "dwelling"]},
    "homes": {"q_codes": ["Q3947"], "keywords": ["home", "homes", "house", "houses", "dwelling"]},
    "room": {"q_codes": ["Q11446"], "keywords": ["room", "rooms", "chamber", "chambers", "space"]},
    "rooms": {"q_codes": ["Q11446"], "keywords": ["room", "rooms", "chamber", "chambers", "space"]},
    "kitchen": {"q_codes": ["Q11446"], "keywords": ["kitchen", "kitchens", "cooking", "food"]},
    "kitchens": {"q_codes": ["Q11446"], "keywords": ["kitchen", "kitchens", "cooking", "food"]},
    "bedroom": {"q_codes": ["Q11446"], "keywords": ["bedroom", "bedrooms", "sleeping", "rest"]},
    "bedrooms": {"q_codes": ["Q11446"], "keywords": ["bedroom", "bedrooms", "sleeping", "rest"]},
    "parlor": {"q_codes": ["Q11446"], "keywords": ["parlor", "parlors", "sitting room", "living room"]},
    "parlors": {"q_codes": ["Q11446"], "keywords": ["parlor", "parlors", "sitting room", "living room"]},
    "hall": {"q_codes": ["Q11446"], "keywords": ["hall", "halls", "corridor", "corridors", "passage"]},
    "halls": {"q_codes": ["Q11446"], "keywords": ["hall", "halls", "corridor", "corridors", "passage"]},
    "palace": {"q_codes": ["Q23413"], "keywords": ["palace", "palaces", "castle", "castles", "royal"]},
    "palaces": {"q_codes": ["Q23413"], "keywords": ["palace", "palaces", "castle", "castles", "royal"]},
    "temple": {"q_codes": ["Q16970"], "keywords": ["temple", "temples", "shrine", "shrines", "sacred"]},
    "temples": {"q_codes": ["Q16970"], "keywords": ["temple", "temples", "shrine", "shrines", "sacred"]},
    "school": {"q_codes": ["Q11446"], "keywords": ["school", "schools", "education", "learning"]},
    "schools": {"q_codes": ["Q11446"], "keywords": ["school", "schools", "education", "learning"]},
    "hospital": {"q_codes": ["Q11446"], "keywords": ["hospital", "hospitals", "medical", "health"]},
    "hospitals": {"q_codes": ["Q11446"], "keywords": ["hospital", "hospitals", "medical", "health"]},
    "prison": {"q_codes": ["Q11446"], "keywords": ["prison", "prisons", "jail", "jails", "confinement"]},
    "prisons": {"q_codes": ["Q11446"], "keywords": ["prison", "prisons", "jail", "jails", "confinement"]},
    "dungeon": {"q_codes": ["Q11446"], "keywords": ["dungeon", "dungeons", "cell", "cells", "underground"]},
    "dungeons": {"q_codes": ["Q11446"], "keywords": ["dungeon", "dungeons", "cell", "cells", "underground"]},
    "cemetery": {"q_codes": ["Q3961"], "keywords": ["cemetery", "cemeteries", "graveyard", "graveyards", "burial"]},
    "cemeteries": {"q_codes": ["Q3961"], "keywords": ["cemetery", "cemeteries", "graveyard", "graveyards", "burial"]},
    "grave": {"q_codes": ["Q3961"], "keywords": ["grave", "graves", "tomb", "tombs", "burial"]},
    "graves": {"q_codes": ["Q3961"], "keywords": ["grave", "graves", "tomb", "tombs", "burial"]},
    "tomb": {"q_codes": ["Q3961"], "keywords": ["grave", "graves", "tomb", "tombs", "burial"]},
    "tombs": {"q_codes": ["Q3961"], "keywords": ["grave", "graves", "tomb", "tombs", "burial"]},
    
    # Birthday and celebration concrete nouns
    "friend": {"q_codes": ["Q5", "Q17297777"], "keywords": ["friend", "friends", "companion", "companions", "buddy", "buddies"]},
    "friends": {"q_codes": ["Q5", "Q17297777"], "keywords": ["friend", "friends", "companion", "companions", "buddy", "buddies"]},
    "wish": {"q_codes": ["Q2385804", "Q8274"], "keywords": ["wish", "wishes", "hope", "hopes", "desire", "desires"]},
    "wishes": {"q_codes": ["Q2385804", "Q8274"], "keywords": ["wish", "wishes", "hope", "hopes", "desire", "desires"]},
    "pleasure": {"q_codes": ["Q2385804", "Q8274", "Q1068639"], "keywords": ["pleasure", "joy", "happiness", "delight", "enjoyment"]},
    "birthday": {"q_codes": ["Q2811", "Q2385804"], "keywords": ["birthday", "birthdays", "anniversary", "celebration", "party"]},
    "birthdays": {"q_codes": ["Q2811", "Q2385804"], "keywords": ["birthday", "birthdays", "anniversary", "celebration", "party"]},
    "celebration": {"q_codes": ["Q2385804", "Q8274"], "keywords": ["celebration", "celebrations", "festivity", "festivities", "party", "parties"]},
    "celebrations": {"q_codes": ["Q2385804", "Q8274"], "keywords": ["celebration", "celebrations", "festivity", "festivities", "party", "parties"]},
    "joy": {"q_codes": ["Q8274", "Q1068639"], "keywords": ["joy", "happiness", "pleasure", "delight", "cheer", "merriment"]},
    "happiness": {"q_codes": ["Q8274", "Q1068639"], "keywords": ["joy", "happiness", "pleasure", "delight", "cheer", "merriment"]},
    "health": {"q_codes": ["Q5", "Q2385804"], "keywords": ["health", "wellness", "vitality", "strength", "vigor"]},
    "youth": {"q_codes": ["Q7569", "Q2385804"], "keywords": ["youth", "young", "younger", "fresh", "vital"]}
}

# Conflict mappings for enhanced matching
CONFLICT_MAPPINGS = {
    "peaceful": {
        "hard_exclude": ["Q198", "Q18811", "Q124490"],  # war, battle, violence
        "soft_avoid": ["Q4", "Q183"]  # death, night
    },
    "serene": {
        "hard_exclude": ["Q198", "Q18811", "Q124490"],  # war, battle, violence
        "soft_avoid": ["Q4", "Q183"]  # death, night
    },
    "joyful": {
        "hard_exclude": ["Q4", "Q203", "Q2912397"],  # death, mourning, memorial
        "soft_avoid": ["Q183", "Q198"]  # night, war
    },
    "celebratory": {
        "hard_exclude": ["Q4", "Q203", "Q2912397"],  # death, mourning, memorial
        "soft_avoid": ["Q183", "Q198"]  # night, war
    },
    "intimate": {
        "hard_exclude": [],  # No hard exclusions
        "soft_avoid": ["Q191163"]  # vast landscapes
    },
    "bright": {
        "hard_exclude": [],  # No hard exclusions
        "soft_avoid": ["Q183", "Q111"]  # darkness
    },
    "light": {
        "hard_exclude": [],  # No hard exclusions
        "soft_avoid": ["Q183", "Q111"]  # darkness
    },
    "melancholic": {
        "hard_exclude": ["Q2385804", "Q8274"],  # celebration, dance
        "soft_avoid": ["Q111", "Q525"]  # day, sun
    },
    "contemplative": {
        "hard_exclude": ["Q198", "Q18811"],  # war, battle
        "soft_avoid": ["Q2385804", "Q8274"]  # celebration, dance
    }
}
