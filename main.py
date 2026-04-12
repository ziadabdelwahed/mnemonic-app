import secrets
import hashlib
import hmac
import json
import logging
import sqlite3
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time
import struct
import binascii

# ============================================================================
# Logging Configuration
# ============================================================================
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================================================================
# Wordlist Module
# ============================================================================

class WordlistManager:
    """Manages wordlist loading, validation, and O(1) lookups."""

    WORDLIST = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
        "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
        "action", "actor", "actress", "actual", "adapt", "add", "addict", "address", "adjust", "admit",
        "adult", "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
        "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert",
        "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter",
        "always", "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient", "anger",
        "angle", "angry", "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique",
        "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april", "arch", "arctic",
        "area", "arena", "argue", "arm", "armed", "armor", "army", "around", "arrange", "arrest",
        "arrive", "arrow", "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset",
        "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
        "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake",
        "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor", "bacon", "badge",
        "bag", "balance", "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain",
        "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become",
        "beef", "before", "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit",
        "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike", "bind", "biology",
        "bird", "birth", "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless",
        "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body",
        "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring", "borrow", "boss",
        "bottom", "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave", "bread",
        "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze",
        "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb",
        "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus", "business", "busy",
        "butter", "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake", "call",
        "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas",
        "canyon", "capable", "capital", "captain", "car", "carbon", "card", "cargo", "carpet", "carry",
        "cart", "case", "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category",
        "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement", "census", "century",
        "cereal", "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge", "chase",
        "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken", "chief", "child",
        "chimney", "choice", "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle",
        "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay", "clean", "clerk",
        "clever", "click", "client", "cliff", "climb", "clinic", "clip", "clock", "clog", "close",
        "cloth", "cloud", "clown", "club", "clump", "cluster", "clutch", "coach", "coast", "coconut",
        "code", "coffee", "coil", "coin", "collect", "color", "column", "combine", "come", "comfort",
        "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect", "consider", "control",
        "convince", "cook", "cool", "copper", "copy", "coral", "core", "corn", "correct", "cost",
        "cotton", "couch", "country", "couple", "course", "cousin", "cover", "coyote", "crack", "cradle",
        "craft", "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek",
        "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd", "crucial",
        "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal", "cube", "culture", "cup",
        "cupboard", "curious", "current", "curtain", "curve", "cushion", "custom", "cute", "cycle", "dad",
        "damage", "damp", "dance", "danger", "daring", "dash", "daughter", "dawn", "day", "deal",
        "debate", "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer", "defense",
        "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial", "dentist", "deny",
        "depart", "depend", "deposit", "depth", "deputy", "derive", "describe", "desert", "design", "desk",
        "despair", "destroy", "detail", "detect", "develop", "device", "devote", "diagram", "dial", "diamond",
        "diary", "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur",
        "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder", "display", "distance",
        "divert", "divide", "divorce", "dizzy", "doctor", "document", "dog", "doll", "dolphin", "domain",
        "donate", "donkey", "donor", "door", "dose", "double", "dove", "draft", "dragon", "drama",
        "drastic", "draw", "dream", "dress", "drift", "drill", "drink", "drip", "drive", "drop",
        "drum", "dry", "duck", "dumb", "dune", "during", "dust", "dutch", "duty", "dwarf",
        "dynamic", "eager", "eagle", "early", "earn", "earth", "easily", "east", "easy", "echo",
        "ecology", "economy", "edge", "edit", "educate", "effort", "egg", "eight", "either", "elbow",
        "elder", "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark", "embody",
        "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable", "enact", "end", "endless",
        "endorse", "enemy", "energy", "enforce", "engage", "engine", "enhance", "enjoy", "enlist", "enough",
        "enrich", "enroll", "ensure", "enter", "entire", "entry", "envelope", "episode", "equal", "equip",
        "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay", "essence", "estate",
        "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example", "excess", "exchange",
        "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit", "exile", "exist", "exit",
        "exotic", "expand", "expect", "expire", "explain", "expose", "express", "extend", "extra", "eye",
        "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall", "false", "fame",
        "family", "famous", "fan", "fancy", "fantasy", "farm", "fashion", "fat", "fatal", "father",
        "fatigue", "fault", "favorite", "feature", "february", "federal", "fee", "feed", "feel", "female",
        "fence", "festival", "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file",
        "film", "filter", "final", "find", "fine", "finger", "finish", "fire", "firm", "first",
        "fiscal", "fish", "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor",
        "flee", "flight", "flip", "float", "flock", "floor", "flower", "fluid", "flush", "fly",
        "foam", "focus", "fog", "foil", "fold", "follow", "food", "foot", "force", "forest",
        "forget", "fork", "fortune", "forum", "forward", "fossil", "foster", "found", "fox", "fragile",
        "frame", "frequent", "fresh", "friend", "fringe", "frog", "front", "frost", "frown", "frozen",
        "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy",
        "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas", "gasp",
        "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine", "gesture",
        "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl", "give", "glad", "glance",
        "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory", "glove", "glow", "glue",
        "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown",
        "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great", "green", "grid",
        "grief", "grit", "grocery", "group", "grow", "grunt", "guard", "guess", "guide", "guilt",
        "guitar", "gun", "gym", "habit", "hair", "half", "hammer", "hamster", "hand", "happy",
        "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk", "hazard", "head", "health",
        "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen", "hero", "hidden",
        "high", "hill", "hint", "hip", "hire", "history", "hobby", "hockey", "hold", "hole",
        "holiday", "hollow", "home", "honey", "hood", "hope", "horn", "horror", "horse", "hospital",
        "host", "hotel", "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred",
        "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea",
        "identify", "idle", "ignore", "ill", "illegal", "illness", "image", "imitate", "immense", "immune",
        "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase", "325ndex", "indicate",
        "indoor", "industry", "infant", "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury",
        "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside", "inspire", "install",
        "intact", "interest", "into", "invest", "invite", "involve", "iron", "island", "isolate", "issue",
        "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans", "jelly", "jewel",
        "job", "join", "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior",
        "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick", "kid", "kidney",
        "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife",
        "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language",
        "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit",
        "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal",
        "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson", "letter", "level",
        "liar", "liberty", "library", "license", "life", "lift", "light", "like", "limb", "limit",
        "link", "lion", "liquid", "list", "little", "live", "lizard", "load", "loan", "lobster",
        "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud", "lounge", "love",
        "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics", "machine", "mad",
        "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal", "man", "manage",
        "mandate", "mango", "mansion", "manual", "maple", "marble", "march", "margin", "marine", "market",
        "marriage", "mask", "mass", "master", "match", "material", "math", "matrix", "matter", "maximum",
        "maze", "meadow", "mean", "measure", "meat", "mechanic", "medal", "media", "melody", "melt",
        "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry", "mesh", "message",
        "metal", "method", "middle", "midnight", "milk", "million", "mimic", "mind", "minimum", "minor",
        "minute", "miracle", "mirror", "misery", "miss", "mistake", "mix", "mixed", "mixture", "mobile",
        "model", "modify", "mom", "moment", "monitor", "monkey", "monster", "month", "moon", "moral",
        "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move", "movie",
        "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual",
        "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty", "nation", "nature",
        "near", "neck", "need", "negative", "neglect", "neither", "nephew", "nerve", "nest", "net",
        "network", "neutral", "never", "news", "next", "nice", "night", "noble", "noise", "nominee",
        "noodle", "normal", "north", "nose", "notable", "note", "nothing", "notice", "novel", "now",
        "nuclear", "number", "nurse", "nut", "oak", "obey", "object", "oblige", "obscure", "observe",
        "obtain", "obvious", "occur", "ocean", "october", "odor", "off", "offer", "office", "often",
        "oil", "okay", "old", "olive", "olympic", "omit", "once", "one", "onion", "online",
        "only", "open", "opera", "opinion", "oppose", "option", "orange", "orbit", "orchard", "order",
        "ordinary", "organ", "orient", "original", "orphan", "ostrich", "other", "outdoor", "outer", "output",
        "outside", "oval", "oven", "over", "own", "owner", "oxygen", "oyster", "ozone", "pact",
        "paddle", "page", "pair", "palace", "palm", "panda", "panel", "panic", "panther", "paper",
        "parade", "parent", "park", "parrot", "party", "pass", "patch", "path", "patient", "patrol",
        "pattern", "pause", "pave", "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen",
        "penalty", "pencil", "people", "pepper", "perfect", "permit", "person", "pet", "phone", "photo",
        "phrase", "physical", "piano", "picnic", "picture", "piece", "pig", "pigeon", "pill", "pilot",
        "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place", "planet", "plastic", "plate",
        "play", "please", "pledge", "pluck", "plug", "plunge", "poem", "poet", "point", "polar",
        "pole", "police", "pond", "pony", "pool", "popular", "portion", "position", "possible", "post",
        "potato", "pottery", "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare",
        "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority", "prison", "private",
        "prize", "problem", "process", "produce", "profit", "program", "project", "promote", "proof", "property",
        "prosper", "protect", "proud", "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin",
        "punch", "pupil", "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle",
        "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit",
        "raccoon", "race", "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp",
        "ranch", "random", "range", "rapid", "rare", "rate", "rather", "raven", "raw", "razor",
        "ready", "real", "reason", "rebel", "rebuild", "recall", "receive", "recipe", "record", "recycle",
        "reduce", "reflect", "reform", "refuse", "region", "regret", "regular", "reject", "relax", "release",
        "relief", "rely", "remain", "remember", "remind", "remove", "render", "renew", "rent", "reopen",
        "repair", "repeat", "replace", "report", "require", "rescue", "resemble", "resist", "resource", "response",
        "result", "retire", "retreat", "return", "reunion", "reveal", "review", "reward", "rhythm", "rib",
        "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right", "rigid", "ring", "riot",
        "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot", "robust", "rocket",
        "romance", "roof", "rookie", "room", "rose", "rotate", "rough", "round", "route", "royal",
        "rubber", "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle", "sadness",
        "safe", "sail", "salad", "salmon", "salon", "salt", "salute", "same", "sample", "sand",
        "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scale", "scan", "scare", "scatter",
        "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script",
        "scrub", "sea", "search", "season", "seat", "second", "secret", "section", "security", "seed",
        "seek", "segment", "select", "sell", "seminar", "senior", "sense", "sentence", "series", "service",
        "session", "settle", "setup", "seven", "shadow", "shaft", "shallow", "share", "shed", "shell",
        "sheriff", "shield", "shift", "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop",
        "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling", "sick", "side",
        "siege", "sight", "sign", "silent", "silk", "silly", "silver", "similar", "simple", "since",
        "sing", "siren", "sister", "situate", "six", "size", "skate", "sketch", "ski", "skill",
        "skin", "skirt", "skull", "slab", "slam", "sleep", "slender", "slice", "slide", "slight",
        "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke", "smooth",
        "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soda",
        "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon", "sorry",
        "sort", "soul", "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn",
        "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike", "spin",
        "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray", "spread", "spring",
        "spy", "square", "squeeze", "squirrel", "stable", "stadium", "staff", "stage", "stairs", "stamp",
        "stand", "start", "state", "stay", "steak", "steel", "stem", "step", "stereo", "stick",
        "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy", "street",
        "strike", "strong", "struggle", "student", "stuff", "stumble", "style", "subject", "submit", "subway",
        "success", "such", "sudden", "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny",
        "sunset", "super", "supply", "supreme", "sure", "surface", "surge", "surprise", "surround", "survey",
        "suspect", "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweet", "swift", "swim",
        "swing", "switch", "sword", "symbol", "symptom", "syrup", "system", "table", "tackle", "tag",
        "tail", "talent", "talk", "tank", "tape", "target", "task", "taste", "tattoo", "taxi",
        "teach", "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test", "text",
        "thank", "that", "theme", "then", "theory", "there", "they", "thing", "this", "thought",
        "three", "thrive", "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt", "timber",
        "time", "tiny", "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler",
        "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool",
        "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist",
        "toward", "tower", "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer",
        "trap", "trash", "travel", "tray", "treat", "tree", "trend", "trial", "tribe", "trick",
        "trigger", "trim", "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust",
        "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle",
        "twelve", "twenty", "twice", "twin", "twist", "two", "type", "typical", "ugly", "umbrella",
        "unable", "unaware", "uncle", "uncover", "under", "undo", "unfair", "unfold", "unhappy", "uniform",
        "unique", "unit", "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade",
        "uphold", "upon", "upper", "upset", "urban", "urge", "usage", "use", "used", "useful",
        "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid", "valley", "valve", "van",
        "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture", "venue",
        "verb", "verify", "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious", "victory",
        "video", "view", "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual",
        "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage",
        "wagon", "wait", "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash",
        "wasp", "waste", "water", "wave", "way", "wealth", "weapon", "wear", "weasel", "weather",
        "web", "wedding", "weekend", "weird", "welcome", "west", "wet", "whale", "what", "wheat",
        "wheel", "when", "where", "whip", "whisper", "wide", "width", "wife", "wild", "will",
        "win", "window", "wine", "wing", "wink", "winner", "winter", "wire", "wisdom", "wise",
        "wish", "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world",
        "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year",
        "yellow", "you", "young", "youth", "zebra", "zero", "zone", "zoo"
    ]

    WORD_TO_INDEX: Dict[str, int] = {}

    @classmethod
    def _validate_wordlist(cls):
        if len(cls.WORDLIST) != 2048:
            raise RuntimeError(f"Invalid wordlist length: {len(cls.WORDLIST)}. Expected 2048.")
        if len(set(cls.WORDLIST)) != len(cls.WORDLIST):
            raise RuntimeError("Wordlist contains duplicate entries.")
        cls.WORD_TO_INDEX = {word: idx for idx, word in enumerate(cls.WORDLIST)}
        logger.info(f"Wordlist validated: {len(cls.WORDLIST)} words loaded.")

    @classmethod
    def get_index(cls, word: str) -> int:
        if word not in cls.WORD_TO_INDEX:
            raise ValueError(f"Word '{word}' not in wordlist")
        return cls.WORD_TO_INDEX[word]

    @classmethod
    def get_word(cls, index: int) -> str:
        if index < 0 or index >= len(cls.WORDLIST):
            raise ValueError(f"Index {index} out of range [0, {len(cls.WORDLIST)-1}]")
        return cls.WORDLIST[index]

    @classmethod
    def contains(cls, word: str) -> bool:
        return word in cls.WORD_TO_INDEX

WordlistManager._validate_wordlist()

# ============================================================================
# Core Cryptographic Engine
# ============================================================================

@dataclass
class MnemonicResult:
    mnemonic: str
    entropy_hex: str
    entropy_bytes: bytes
    word_count: int
    entropy_bits: int
    checksum_bits: int
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            'mnemonic': self.mnemonic,
            'entropy_hex': self.entropy_hex,
            'word_count': self.word_count,
            'entropy_bits': self.entropy_bits,
            'checksum_bits': self.checksum_bits,
            'timestamp': self.timestamp
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

class MnemonicEngine:
    VALID_BITS = (128, 160, 192, 224, 256)
    WORD_COUNTS = {128: 12, 160: 15, 192: 18, 224: 21, 256: 24}

    @classmethod
    def entropy_to_mnemonic(cls, entropy: bytes) -> str:
        entropy_bits = len(entropy) * 8
        if entropy_bits not in cls.VALID_BITS:
            raise ValueError(f"Entropy must be 128-256 bits in 32-bit increments, got {entropy_bits}")

        entropy_hash = hashlib.sha256(entropy).digest()
        hash_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)
        checksum_bits = hash_bits[:entropy_bits // 32]

        entropy_int = int.from_bytes(entropy, 'big')
        entropy_bin = bin(entropy_int)[2:].zfill(entropy_bits)
        full_bin = entropy_bin + checksum_bits

        words = []
        for i in range(0, len(full_bin), 11):
            chunk = full_bin[i:i+11]
            if len(chunk) == 11:
                idx = int(chunk, 2)
                words.append(WordlistManager.get_word(idx))

        return ' '.join(words)

    @classmethod
    def mnemonic_to_entropy(cls, mnemonic: str) -> bytes:
        words = mnemonic.strip().split()
        word_count = len(words)

        if word_count not in cls.WORD_COUNTS.values():
            raise ValueError(f"Invalid mnemonic length: {word_count} words. Expected 12,15,18,21,24.")

        indices = [WordlistManager.get_index(w) for w in words]
        bits = ''.join(format(idx, '011b') for idx in indices)

        entropy_bits = (word_count * 11) * 32 // 33
        entropy_bin = bits[:entropy_bits]
        checksum_bin = bits[entropy_bits:]

        entropy_bytes = (entropy_bits + 7) // 8
        entropy_int = int(entropy_bin, 2)
        entropy = entropy_int.to_bytes(entropy_bytes, 'big')

        entropy_hash = hashlib.sha256(entropy).digest()
        hash_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)
        expected_checksum = hash_bits[:entropy_bits // 32]

        if checksum_bin != expected_checksum:
            raise ValueError("Invalid checksum - mnemonic may be corrupted or contains a typo")

        return entropy

    @classmethod
    def generate(cls, entropy_bits: int = 256) -> MnemonicResult:
        if entropy_bits not in cls.VALID_BITS:
            raise ValueError(f"Entropy bits must be one of {cls.VALID_BITS}")

        entropy_bytes = entropy_bits // 8
        entropy = secrets.token_bytes(entropy_bytes)
        mnemonic = cls.entropy_to_mnemonic(entropy)

        return MnemonicResult(
            mnemonic=mnemonic,
            entropy_hex=entropy.hex(),
            entropy_bytes=entropy,
            word_count=len(mnemonic.split()),
            entropy_bits=entropy_bits,
            checksum_bits=entropy_bits // 32
        )

    @classmethod
    def validate(cls, mnemonic: str) -> Tuple[bool, Optional[str]]:
        try:
            cls.mnemonic_to_entropy(mnemonic)
            return True, None
        except ValueError as e:
            return False, str(e)

# ============================================================================
# BIP-32 Hierarchical Deterministic Wallet Module
# ============================================================================

class HDWallet:
    """
    Implements BIP-32 Hierarchical Deterministic Wallets.
    Generates Master Seed, Master Extended Keys, and derives child keys
    according to the exact derivation paths used by wallet software.
    """
    
    # Curve order for secp256k1
    SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    @staticmethod
    def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
        """
        BIP-39: Convert mnemonic to seed using PBKDF2.
        This is the master seed from which all keys are derived.
        """
        mnemonic_bytes = mnemonic.encode('utf-8')
        passphrase_bytes = ("mnemonic" + passphrase).encode('utf-8')
        seed = hashlib.pbkdf2_hmac('sha512', mnemonic_bytes, passphrase_bytes, 2048, 64)
        return seed
    
    @staticmethod
    def hmac_sha512(key: bytes, data: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha512).digest()
    
    @classmethod
    def master_key_from_seed(cls, seed: bytes) -> Dict[str, Union[bytes, str, int]]:
        """
        BIP-32: Generate master extended private key (xprv) from seed.
        Returns chain code and master private key components.
        """
        if len(seed) < 16:
            raise ValueError("Seed must be at least 128 bits")
        if len(seed) > 64:
            raise ValueError("Seed must be at most 512 bits")
        
        hmac_result = cls.hmac_sha512(b"Bitcoin seed", seed)
        master_private_key = hmac_result[:32]
        master_chain_code = hmac_result[32:]
        
        # Validate master private key is less than secp256k1 order
        priv_int = int.from_bytes(master_private_key, 'big')
        if priv_int == 0 or priv_int >= cls.SECP256K1_ORDER:
            raise ValueError("Invalid master private key - out of range")
        
        return {
            'private_key': master_private_key,
            'chain_code': master_chain_code,
            'depth': 0,
            'parent_fingerprint': b'\x00\x00\x00\x00',
            'child_index': 0
        }
    
    @classmethod
    def derive_child_private_key(cls, parent_privkey: bytes, parent_chaincode: bytes, index: int, hardened: bool = False) -> Dict[str, Union[bytes, int]]:
        """
        Derive a child extended private key from parent.
        - If hardened: index >= 0x80000000 (2^31)
        - If non-hardened: index < 0x80000000
        """
        if hardened:
            child_index = index + 0x80000000
        else:
            child_index = index
        
        # Serialize parent private key for HMAC
        if hardened:
            # Hardened: use 0x00 || parent_privkey || index
            data = b'\x00' + parent_privkey + struct.pack('>I', child_index)
        else:
            # Non-hardened: use parent_public_key || index
            parent_pubkey = cls._private_to_public(parent_privkey)
            data = parent_pubkey + struct.pack('>I', child_index)
        
        hmac_result = cls.hmac_sha512(parent_chaincode, data)
        left_32 = hmac_result[:32]
        right_32 = hmac_result[32:]
        
        # Child private key = (left_32 + parent_privkey) % n
        left_int = int.from_bytes(left_32, 'big')
        parent_int = int.from_bytes(parent_privkey, 'big')
        child_int = (left_int + parent_int) % cls.SECP256K1_ORDER
        
        if left_int >= cls.SECP256K1_ORDER or child_int == 0:
            raise ValueError("Invalid child key - try next index")
        
        child_privkey = child_int.to_bytes(32, 'big')
        
        return {
            'private_key': child_privkey,
            'chain_code': right_32,
            'child_index': child_index,
            'hardened': hardened
        }
    
    @staticmethod
    def _private_to_public(private_key: bytes) -> bytes:
        """
        Convert private key to compressed public key (33 bytes) using secp256k1.
        Implementation uses elliptic curve multiplication without external libs.
        """
        # secp256k1 parameters
        p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        
        def point_add(p1, p2):
            if p1 is None:
                return p2
            if p2 is None:
                return p1
            x1, y1 = p1
            x2, y2 = p2
            if x1 == x2 and y1 != y2:
                return None
            if x1 == x2:
                m = (3 * x1 * x1 * pow(2 * y1, -1, p)) % p
            else:
                m = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
            x3 = (m * m - x1 - x2) % p
            y3 = (m * (x1 - x3) - y1) % p
            return (x3, y3)
        
        def point_mul(k, point):
            result = None
            addend = point
            while k:
                if k & 1:
                    result = point_add(result, addend)
                addend = point_add(addend, addend)
                k >>= 1
            return result
        
        k = int.from_bytes(private_key, 'big')
        if k == 0 or k >= cls.SECP256K1_ORDER:
            raise ValueError("Invalid private key")
        
        pub_x, pub_y = point_mul(k, (Gx, Gy))
        
        # Compressed public key format: 0x02 if y even, 0x03 if y odd
        prefix = b'\x02' if pub_y % 2 == 0 else b'\x03'
        return prefix + pub_x.to_bytes(32, 'big')
    
    @classmethod
    def derive_path(cls, master_seed: bytes, path: str) -> Dict[str, Union[bytes, str]]:
        """
        Derive a private key following a BIP-32 derivation path.
        Example paths:
        - BIP-44: m/44'/0'/0'/0/0
        - BIP-49: m/49'/0'/0'/0/0
        - BIP-84: m/84'/0'/0'/0/0
        
        Returns the final derived private key and its metadata.
        """
        master = cls.master_key_from_seed(master_seed)
        current_privkey = master['private_key']
        current_chaincode = master['chain_code']
        
        # Remove 'm/' prefix if present
        if path.startswith('m/'):
            path = path[2:]
        
        components = path.split('/')
        for comp in components:
            if not comp:
                continue
            
            hardened = comp.endswith("'")
            if hardened:
                index = int(comp[:-1])
            else:
                index = int(comp)
            
            derived = cls.derive_child_private_key(
                current_privkey, 
                current_chaincode, 
                index, 
                hardened
            )
            current_privkey = derived['private_key']
            current_chaincode = derived['chain_code']
        
        return {
            'private_key': current_privkey,
            'private_key_hex': current_privkey.hex(),
            'chain_code': current_chaincode,
            'path': path,
            'public_key': cls._private_to_public(current_privkey),
            'public_key_hex': cls._private_to_public(current_privkey).hex()
        }

# ============================================================================
# Enhanced Wallet Service with Derivation Support
# ============================================================================

@dataclass
class WalletAccount:
    """Represents a single account derived from master seed."""
    index: int
    path: str
    private_key_hex: str
    public_key_hex: str
    address_legacy: str   # P2PKH (1...)
    address_segwit: str   # P2SH-P2WPKH (3...)
    address_native_segwit: str  # Bech32 (bc1...)

@dataclass
class HierarchicalWallet:
    """
    Complete HD wallet structure matching wallet software output order.
    Contains master seed, mnemonic, and derived accounts in sequence.
    """
    mnemonic: str
    passphrase: str
    seed_hex: str
    master_private_key_hex: str
    master_public_key_hex: str
    master_fingerprint: str
    accounts: List[WalletAccount]
    derivation_scheme: str  # BIP44, BIP49, BIP84
    coin_type: int  # 0 for Bitcoin, 60 for Ethereum, etc.
    created_at: float

class AdvancedWalletService:
    """
    Service that generates mnemonics AND derives HD wallet accounts
    in exact sequential order matching wallet software (Electrum, Mycelium, Ledger).
    """
    
    # Standard derivation schemes
    BIP44_PURPOSE = 44   # Legacy addresses starting with 1
    BIP49_PURPOSE = 49   # SegWit addresses starting with 3
    BIP84_PURPOSE = 84   # Native SegWit addresses starting with bc1
    
    def __init__(self, coin_type: int = 0, account_count: int = 20):
        """
        coin_type: 0 for Bitcoin, 60 for Ethereum, 2 for Litecoin, etc.
        account_count: Number of accounts to derive (typically 20 for gap limit)
        """
        self.coin_type = coin_type
        self.account_count = account_count
    
    def _derive_addresses(self, private_key: bytes) -> Dict[str, str]:
        """
        Derive all three address formats from a private key.
        Returns P2PKH (Legacy), P2SH-SegWit, and Bech32 addresses.
        """
        # Simplified address generation - in production you'd use full Base58/Bech32 encoding
        pubkey = HDWallet._private_to_public(private_key)
        pubkey_hash = hashlib.new('ripemd160', hashlib.sha256(pubkey).digest()).digest()
        
        # Legacy (P2PKH) - starts with 1
        legacy_prefix = b'\x00' + pubkey_hash
        legacy_checksum = hashlib.sha256(hashlib.sha256(legacy_prefix).digest()).digest()[:4]
        address_legacy = "1" + binascii.b2a_base64(legacy_prefix + legacy_checksum).decode()[:34]
        
        # SegWit (P2SH-P2WPKH) - starts with 3
        witness_program = b'\x00\x14' + pubkey_hash
        witness_hash = hashlib.new('ripemd160', hashlib.sha256(witness_program).digest()).digest()
        segwit_prefix = b'\x05' + witness_hash
        segwit_checksum = hashlib.sha256(hashlib.sha256(segwit_prefix).digest()).digest()[:4]
        address_segwit = "3" + binascii.b2a_base64(segwit_prefix + segwit_checksum).decode()[:34]
        
        # Native SegWit (Bech32) - starts with bc1
        address_native = "bc1" + binascii.b2a_base64(witness_program).decode()[:38]
        
        return {
            'legacy': address_legacy.replace('=', '').replace('\n', ''),
            'segwit': address_segwit.replace('=', '').replace('\n', ''),
            'native_segwit': address_native.replace('=', '').replace('\n', '')
        }
    
    def generate_wallet(self, entropy_bits: int = 256, passphrase: str = "", scheme: str = "BIP84") -> HierarchicalWallet:
        """
        Generate a complete hierarchical wallet with derived accounts in order.
        
        Order matches wallet software:
        1. Generate mnemonic
        2. Generate master seed (PBKDF2)
        3. Derive master keys
        4. Derive receiving addresses (external chain, index 0..N)
        5. Derive change addresses (internal chain, index 0..N) - optional
        """
        # Step 1: Generate mnemonic and master seed
        result = MnemonicEngine.generate(entropy_bits)
        mnemonic = result.mnemonic
        master_seed = HDWallet.mnemonic_to_seed(mnemonic, passphrase)
        
        # Step 2: Derive master keys
        master = HDWallet.master_key_from_seed(master_seed)
        master_privkey = master['private_key']
        master_pubkey = HDWallet._private_to_public(master_privkey)
        
        # Calculate master fingerprint (first 4 bytes of RIPEMD160 of SHA256 of public key)
        fingerprint = hashlib.new('ripemd160', hashlib.sha256(master_pubkey).digest()).digest()[:4]
        
        # Step 3: Determine derivation purpose based on scheme
        if scheme == "BIP44":
            purpose = self.BIP44_PURPOSE
        elif scheme == "BIP49":
            purpose = self.BIP49_PURPOSE
        else:  # BIP84 default
            purpose = self.BIP84_PURPOSE
        
        # Step 4: Derive accounts in sequence (matching wallet software order)
        accounts = []
        base_path = f"m/{purpose}'/{self.coin_type}'/0'"
        
        # Derive receiving addresses (external chain, index 0)
        for i in range(self.account_count):
            path = f"{base_path}/0/{i}"
            derived = HDWallet.derive_path(master_seed, path)
            addresses = self._derive_addresses(derived['private_key'])
            
            accounts.append(WalletAccount(
                index=i,
                path=path,
                private_key_hex=derived['private_key_hex'],
                public_key_hex=derived['public_key_hex'],
                address_legacy=addresses['legacy'],
                address_segwit=addresses['segwit'],
                address_native_segwit=addresses['native_segwit']
            ))
        
        return HierarchicalWallet(
            mnemonic=mnemonic,
            passphrase=passphrase,
            seed_hex=master_seed.hex(),
            master_private_key_hex=master_privkey.hex(),
            master_public_key_hex=master_pubkey.hex(),
            master_fingerprint=fingerprint.hex(),
            accounts=accounts,
            derivation_scheme=scheme,
            coin_type=self.coin_type,
            created_at=time.time()
        )
    
    def generate_batch_wallets(self, count: int, entropy_bits: int = 256, scheme: str = "BIP84") -> List[HierarchicalWallet]:
        """Generate multiple wallets in parallel."""
        with ProcessPoolExecutor(max_workers=min(mp.cpu_count(), count)) as executor:
            futures = [executor.submit(self.generate_wallet, entropy_bits, "", scheme) for _ in range(count)]
            return [f.result() for f in futures]

# ============================================================================
# CLI Module with HD Wallet Support
# ============================================================================

def cli():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='UCAR BIP-39 Mnemonic + BIP-32 HD Wallet Generator - Wallet Order Compatible',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--generate', '-g', action='store_true', help='Generate new mnemonic')
    parser.add_argument('--wallet', '-w', action='store_true', help='Generate full HD wallet with accounts (matching wallet order)')
    parser.add_argument('--scheme', choices=['BIP44', 'BIP49', 'BIP84'], default='BIP84', 
                       help='Derivation scheme: BIP44 (Legacy 1...), BIP49 (SegWit 3...), BIP84 (Native bc1...)')
    parser.add_argument('--bits', '-b', type=int, default=256, choices=[128, 160, 192, 224, 256],
                       help='Entropy bits (default: 256 -> 24 words)')
    parser.add_argument('--accounts', '-a', type=int, default=20, help='Number of accounts to derive (default: 20)')
    parser.add_argument('--coin-type', '-c', type=int, default=0, help='Coin type (0=BTC, 60=ETH, 2=LTC, etc.)')
    parser.add_argument('--passphrase', '-p', type=str, default="", help='BIP-39 passphrase (optional)')
    parser.add_argument('--validate', '-v', type=str, help='Validate mnemonic phrase')
    parser.add_argument('--batch', '-B', type=int, help='Batch generate N wallets')
    parser.add_argument('--json', '-j', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.validate:
        is_valid, error = MnemonicEngine.validate(args.validate)
        result = {'valid': is_valid, 'error': error, 'word_count': len(args.validate.split())}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Valid: {is_valid}")
            if error:
                print(f"Error: {error}")
        return
    
    service = AdvancedWalletService(coin_type=args.coin_type, account_count=args.accounts)
    
    if args.batch:
        wallets = service.generate_batch_wallets(args.batch, args.bits, args.scheme)
        if args.json:
            output = []
            for w in wallets:
                output.append({
                    'mnemonic': w.mnemonic,
                    'seed_hex': w.seed_hex,
                    'master_fingerprint': w.master_fingerprint,
                    'account_count': len(w.accounts)
                })
            print(json.dumps(output, indent=2))
        else:
            for i, w in enumerate(wallets, 1):
                print(f"\n=== Wallet {i} ===")
                print(f"Mnemonic: {w.mnemonic}")
                print(f"Master Fingerprint: {w.master_fingerprint}")
                print(f"First Address ({args.scheme}): {w.accounts[0].address_native_segwit if args.scheme == 'BIP84' else w.accounts[0].address_segwit if args.scheme == 'BIP49' else w.accounts[0].address_legacy}")
        return
    
    if args.wallet:
        wallet = service.generate_wallet(args.bits, args.passphrase, args.scheme)
        
        if args.json:
            output = {
                'mnemonic': wallet.mnemonic,
                'passphrase': wallet.passphrase if wallet.passphrase else None,
                'seed_hex': wallet.seed_hex,
                'master_private_key': wallet.master_private_key_hex,
                'master_public_key': wallet.master_public_key_hex,
                'master_fingerprint': wallet.master_fingerprint,
                'derivation_scheme': wallet.derivation_scheme,
                'coin_type': wallet.coin_type,
                'accounts': []
            }
            
            for acc in wallet.accounts:
                output['accounts'].append({
                    'index': acc.index,
                    'path': acc.path,
                    'private_key': acc.private_key_hex,
                    'public_key': acc.public_key_hex,
                    'address_legacy': acc.address_legacy,
                    'address_segwit': acc.address_segwit,
                    'address_native_segwit': acc.address_native_segwit
                })
            
            print(json.dumps(output, indent=2))
        else:
            print("=" * 70)
            print(f"BIP-39 Mnemonic ({len(wallet.mnemonic.split())} words):")
            print(wallet.mnemonic)
            print("\n" + "=" * 70)
            print(f"BIP-32 Master Seed (Hex):")
            print(wallet.seed_hex)
            print(f"\nMaster Fingerprint: {wallet.master_fingerprint}")
            print(f"Derivation Scheme: {wallet.derivation_scheme}")
            print("\n" + "=" * 70)
            print(f"Derived Accounts (matching wallet software order - {args.scheme}):")
            print("-" * 70)
            
            for acc in wallet.accounts:
                if args.scheme == 'BIP44':
                    addr = acc.address_legacy
                elif args.scheme == 'BIP49':
                    addr = acc.address_segwit
                else:
                    addr = acc.address_native_segwit
                
                print(f"Account #{acc.index}: {acc.path}")
                print(f"  Address: {addr}")
                print(f"  Private Key: {acc.private_key_hex}")
                print()
        return
    
    if args.generate:
        result = MnemonicEngine.generate(args.bits)
        if args.json:
            print(result.to_json())
        else:
            print(f"Mnemonic ({result.word_count} words): {result.mnemonic}")
            print(f"Entropy (hex): {result.entropy_hex}")
        return
    
    # Default: generate simple mnemonic
    result = MnemonicEngine.generate(256)
    print(result.mnemonic)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("UCAR HD Wallet Generator - Wallet Order Compatible Mode Initializing")
    
    # Test HD derivation
    test_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    test_seed = HDWallet.mnemonic_to_seed(test_mnemonic)
    test_path = "m/84'/0'/0'/0/0"
    derived = HDWallet.derive_path(test_seed, test_path)
    
    logger.info(f"Test derivation successful. Path: {test_path}")
    logger.info(f"Derived private key: {derived['private_key_hex'][:16]}...")
    
    cli()
