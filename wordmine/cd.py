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
],

    5: [
    "guess", "brain", "smart", "think", "apple", "bread", "charm", "doubt", "eager", "flame",
    "globe", "heart", "image", "joker", "knock", "lemon", "mango", "nerve", "ocean", "peace",
    "queen", "rider", "storm", "table", "urban", "vivid", "wrist", "xenon", "yield", "zebra",
    "angel", "blaze", "craft", "dream", "elite", "fancy", "grape", "haste", "ivory", "jolly",
    "kneel", "lunar", "march", "novel", "onion", "power", "quiet", "raven", "scope", "trust",
    "amber", "beach", "candy", "daisy", "eagle", "frost", "glide", "inlet", "jumpy", "koala",
    "latch", "mercy", "noble", "orbit", "plush", "quirk", "rusty", "spine", "trick", "unity",
    "vowel", "whale", "xylem", "youth", "zesty", "adobe", "bloom", "cabin", "dwell", "exile",
    "fiery", "gloom", "hover", "ideal", "knead", "lyric", "mirth", "nudge", "olive", "piano",
    "quilt", "risky", "shiny", "torch", "udder", "vigor", "woven", "zonal", "asset", "brisk",
    "chill", "dealt", "ethos", "flock", "grasp", "input", "knave", "latch", "mirth", "noble",
    "optic", "plume", "quest", "risky", "scout", "tulip", "unite", "verge", "whisk", "xerox",
    "yacht", "zoned", "amaze", "bison", "crisp", "drape", "eject", "flora", "glint", "imply",
    "jumbo", "knoll", "lupin", "meaty", "nifty", "onset", "pouch", "roost", "swift", "tempo",
    "undue", "vixen", "waist", "abbot", "brace", "choke", "deter", "eclat", "fraud", "gleam",
    "hinge", "icily", "joust", "knees", "leash", "mince", "nerdy", "ounce", "proud", "rover",
    "slant", "ulcer", "wager", "yells", "zonal", "alarm", "blunt", "creek", "drown", "exert",
    "flint", "gravy", "hasty", "irony", "joint", "knack", "lymph", "mount", "nymph", "overt",
    "quash", "ranch", "spore", "tacit", "uncut", "wrath", "yeast"
],

    6: ["random", "puzzle", "letter", "breeze"],
    7: ["amazing", "thought", "journey", "fantasy"]
}


print(f"PYRGOGRAM VERSION :- {pyro}")
print("FALLBACK WORDS LOADED✅")
print("CHALLENGER DATA LOADED✅")
