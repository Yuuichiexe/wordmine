from wordmine import app 
import pyrogram

pyro = pyrogram.__version__

challenger_data = {}

fallback_words = {
    4: [
    "play", "word", "game", "chat", "abet", "bark", "card", "dart", "earn", "fade", 
    "gaze", "hail", "idea", "jade", "keen", "lamb", "mild", "nest", "oath", "pace", 
    "quiz", "rage", "salt", "tame", "undo", "vast", "wade", "xray", "yarn", "zeal", 
    "afar", "bend", "clad", "dine", "emit", "flee", "glim", "hush", "inch", "jolt", 
    "knot", "lure", "moth", "numb", "omit", "pond", "quip", "rift", "sage", "tide", 
    "apex", "bane", "cove", "dusk", "ebb", "fawn", "gale", "hymn", "isle", "jest", 
    "kale", "loom", "mire", "nook", "ogle", "pith", "quay", "rove", "sear", "trek", 
    "veto", "wane", "yoke", "zest", "alms", "brim", "cusp", "dolt", "fret", "grit", 
    "hewn", "idle", "knob", "limp", "mend", "nape", "oust", "pry", "raze", "sift", 
    "taut", "vial", "writ", "zany", "akin", "blot", "chop", "damp", "envy", "flap", 
    "gush", "haze", "inky", "krill", "lisp", "moat", "nope", "opal", "pact", "quip", 
    "rant", "scum", "twit", "urge", "vain", "whiz", "xyst", "yelp", "zinc", "arch", 
    "blur", "crux", "deft", "fizz", "glow", "harp", "itch", "judo", "keto", "lame", 
    "muse", "nude", "oxen", "peck", "skim", "toil", "vice", "wiry", "yolk", "zaps", 
    "axis", "boil", "curl", "dare", "etch", "flaw", "glum", "honk", "irks", "jamb", 
    "keel", "lurk", "mock", "nigh", "ooze", "poke", "roar", "spit", "tarp", "unto", 
    "wage"
]

    5: ["guess", "brain", "smart", "think"],
    6: ["random", "puzzle", "letter", "breeze"],
    7: ["amazing", "thought", "journey", "fantasy"]
}


print(f"PYRGOGRAM VERSION :- {pyro}")
print("FALLBACK WORDS LOADED✅")
print("CHALLENGER DATA LOADED✅")
