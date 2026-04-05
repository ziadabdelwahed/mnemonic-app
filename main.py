import secrets
import hashlib
import json
import logging
import sqlite3
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
from functools import lru_cache

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
        "impact", "impose", "improve", "impulse", "inch", "include", "income", "increase", "index", "indicate",
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

    # O(1) lookup dictionary - performance optimization
    WORD_TO_INDEX: Dict[str, int] = {}

    @classmethod
    def _validate_wordlist(cls):
        """Runtime validation - ensures wordlist integrity."""
        if len(cls.WORDLIST) != 2048:
            raise RuntimeError(f"Invalid wordlist length: {len(cls.WORDLIST)}. Expected 2048.")

        # Check for duplicates
        if len(set(cls.WORDLIST)) != len(cls.WORDLIST):
            raise RuntimeError("Wordlist contains duplicate entries.")

        # Build reverse mapping
        cls.WORD_TO_INDEX = {word: idx for idx, word in enumerate(cls.WORDLIST)}

        logger.info(f"Wordlist validated: {len(cls.WORDLIST)} words loaded.")

    @classmethod
    def get_index(cls, word: str) -> int:
        """O(1) word to index lookup."""
        if word not in cls.WORD_TO_INDEX:
            raise ValueError(f"Word '{word}' not in wordlist")
        return cls.WORD_TO_INDEX[word]

    @classmethod
    def get_word(cls, index: int) -> str:
        """O(1) index to word lookup."""
        if index < 0 or index >= len(cls.WORDLIST):
            raise ValueError(f"Index {index} out of range [0, {len(cls.WORDLIST)-1}]")
        return cls.WORDLIST[index]

    @classmethod
    def contains(cls, word: str) -> bool:
        """Check if word exists in wordlist."""
        return word in cls.WORD_TO_INDEX


# Initialize wordlist on module load
WordlistManager._validate_wordlist()


# ============================================================================
# Core Cryptographic Engine
# ============================================================================

@dataclass
class MnemonicResult:
    """Structured result for mnemonic operations."""
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
        """Convert to JSON-serializable dictionary."""
        return {
            'mnemonic': self.mnemonic,
            'entropy_hex': self.entropy_hex,
            'word_count': self.word_count,
            'entropy_bits': self.entropy_bits,
            'checksum_bits': self.checksum_bits,
            'timestamp': self.timestamp
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class MnemonicEngine:
    """Core cryptographic engine for mnemonic operations."""

    VALID_BITS = (128, 160, 192, 224, 256)
    WORD_COUNTS = {128: 12, 160: 15, 192: 18, 224: 21, 256: 24}

    @classmethod
    def entropy_to_mnemonic(cls, entropy: bytes) -> str:
        """Convert entropy bytes to mnemonic phrase."""
        entropy_bits = len(entropy) * 8
        if entropy_bits not in cls.VALID_BITS:
            raise ValueError(f"Entropy must be 128-256 bits in 32-bit increments, got {entropy_bits}")

        # Calculate checksum (first entropy_bits/32 bits of SHA256)
        entropy_hash = hashlib.sha256(entropy).digest()
        hash_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)
        checksum_bits = hash_bits[:entropy_bits // 32]

        # Combine entropy + checksum
        entropy_int = int.from_bytes(entropy, 'big')
        entropy_bin = bin(entropy_int)[2:].zfill(entropy_bits)
        full_bin = entropy_bin + checksum_bits

        # Split into 11-bit chunks and map to words using O(1) lookup
        words = []
        for i in range(0, len(full_bin), 11):
            chunk = full_bin[i:i+11]
            if len(chunk) == 11:
                idx = int(chunk, 2)
                words.append(WordlistManager.get_word(idx))

        return ' '.join(words)

    @classmethod
    def mnemonic_to_entropy(cls, mnemonic: str) -> bytes:
        """Convert mnemonic phrase back to entropy bytes."""
        words = mnemonic.strip().split()
        word_count = len(words)

        # Validate word count
        if word_count not in cls.WORD_COUNTS.values():
            raise ValueError(f"Invalid mnemonic length: {word_count} words. Expected 12,15,18,21,24.")

        # Convert words to indices using O(1) dictionary lookup
        indices = [WordlistManager.get_index(w) for w in words]

        # Convert indices to binary string
        bits = ''.join(format(idx, '011b') for idx in indices)

        # Extract entropy bits and checksum
        entropy_bits = (word_count * 11) * 32 // 33
        entropy_bin = bits[:entropy_bits]
        checksum_bin = bits[entropy_bits:]

        # Convert entropy binary to bytes
        entropy_bytes = (entropy_bits + 7) // 8
        entropy_int = int(entropy_bin, 2)
        entropy = entropy_int.to_bytes(entropy_bytes, 'big')

        # Verify checksum
        entropy_hash = hashlib.sha256(entropy).digest()
        hash_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)
        expected_checksum = hash_bits[:entropy_bits // 32]

        if checksum_bin != expected_checksum:
            raise ValueError("Invalid checksum - mnemonic may be corrupted or contains a typo")

        return entropy

    @classmethod
    def generate(cls, entropy_bits: int = 256) -> MnemonicResult:
        """Generate a cryptographically secure mnemonic."""
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
        """Validate a mnemonic phrase. Returns (is_valid, error_message)."""
        try:
            cls.mnemonic_to_entropy(mnemonic)
            return True, None
        except ValueError as e:
            return False, str(e)

    @classmethod
    def from_entropy_hex(cls, entropy_hex: str) -> MnemonicResult:
        """Create mnemonic from hex entropy string."""
        entropy = bytes.fromhex(entropy_hex)
        bits = len(entropy) * 8
        if bits not in cls.VALID_BITS:
            raise ValueError(f"Entropy length {bits} bits not supported")

        mnemonic = cls.entropy_to_mnemonic(entropy)

        return MnemonicResult(
            mnemonic=mnemonic,
            entropy_hex=entropy_hex,
            entropy_bytes=entropy,
            word_count=len(mnemonic.split()),
            entropy_bits=bits,
            checksum_bits=bits // 32
        )

    @classmethod
    def to_entropy_hex(cls, mnemonic: str) -> str:
        """Extract entropy hex from mnemonic."""
        entropy = cls.mnemonic_to_entropy(mnemonic)
        return entropy.hex()


# ============================================================================
# Uniqueness Tracker (Optional - for strict non-repetition)
# ============================================================================

class UniquenessTracker:
    """Tracks generated mnemonics to prevent duplicates."""

    def __init__(self, db_path: str = "mnemonic_tracker.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for tracking."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS generated_mnemonics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mnemonic_hash TEXT UNIQUE NOT NULL,
                    entropy_hex TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_hash ON generated_mnemonics(mnemonic_hash)')

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _compute_hash(self, mnemonic: str) -> str:
        """Compute SHA-256 hash of mnemonic."""
        return hashlib.sha256(mnemonic.encode()).hexdigest()

    def is_duplicate(self, mnemonic: str) -> bool:
        """Check if mnemonic has been generated before."""
        mnemonic_hash = self._compute_hash(mnemonic)
        with self._get_connection() as conn:
            result = conn.execute(
                "SELECT 1 FROM generated_mnemonics WHERE mnemonic_hash = ?",
                (mnemonic_hash,)
            ).fetchone()
            return result is not None

    def record(self, mnemonic: str, entropy_hex: str):
        """Record a generated mnemonic."""
        mnemonic_hash = self._compute_hash(mnemonic)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO generated_mnemonics (mnemonic_hash, entropy_hex, created_at) VALUES (?, ?, ?)",
                (mnemonic_hash, entropy_hex, time.time())
            )

    def get_stats(self) -> dict:
        """Get tracking statistics."""
        with self._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) as count FROM generated_mnemonics").fetchone()['count']
            earliest = conn.execute("SELECT MIN(created_at) as earliest FROM generated_mnemonics").fetchone()['earliest']
            latest = conn.execute("SELECT MAX(created_at) as latest FROM generated_mnemonics").fetchone()['latest']

            return {
                'total_generated': count,
                'earliest_timestamp': earliest,
                'latest_timestamp': latest
            }


# ============================================================================
# Production Service Layer
# ============================================================================

class MnemonicService:
    """High-level service with optional uniqueness enforcement and logging."""

    def __init__(self, enforce_uniqueness: bool = False, tracker_db_path: str = "mnemonic_tracker.db"):
        self.enforce_uniqueness = enforce_uniqueness
        self.tracker = UniquenessTracker(tracker_db_path) if enforce_uniqueness else None
        self.stats = {'total_generations': 0, 'duplicates_rejected': 0}

    def generate(self, entropy_bits: int = 256, retry_on_duplicate: bool = True, max_retries: int = 5) -> MnemonicResult:
        """Generate a mnemonic with optional uniqueness enforcement."""
        self.stats['total_generations'] += 1

        for attempt in range(max_retries):
            result = MnemonicEngine.generate(entropy_bits)

            if not self.enforce_uniqueness:
                return result

            if not self.tracker.is_duplicate(result.mnemonic):
                self.tracker.record(result.mnemonic, result.entropy_hex)
                return result
            else:
                self.stats['duplicates_rejected'] += 1
                logger.warning(f"Duplicate mnemonic detected (attempt {attempt+1}/{max_retries})")
                if not retry_on_duplicate:
                    raise RuntimeError("Duplicate mnemonic generated and retry disabled")

        raise RuntimeError(f"Failed to generate unique mnemonic after {max_retries} attempts")

    def validate(self, mnemonic: str) -> dict:
        """Validate mnemonic with detailed response."""
        is_valid, error = MnemonicEngine.validate(mnemonic)
        return {
            'valid': is_valid,
            'error': error,
            'word_count': len(mnemonic.split()) if mnemonic else 0
        }

    def from_entropy(self, entropy_hex: str) -> MnemonicResult:
        """Create mnemonic from hex entropy."""
        return MnemonicEngine.from_entropy_hex(entropy_hex)

    def to_entropy(self, mnemonic: str) -> str:
        """Convert mnemonic to entropy hex."""
        return MnemonicEngine.to_entropy_hex(mnemonic)

    def batch_generate(self, count: int, entropy_bits: int = 256, parallel: bool = True) -> List[MnemonicResult]:
        """Generate multiple mnemonics in parallel."""
        logger.info(f"Batch generating {count} mnemonics with {entropy_bits}-bit entropy")

        if parallel and count > 1:
            with ProcessPoolExecutor(max_workers=min(mp.cpu_count(), count)) as executor:
                futures = [executor.submit(self.generate, entropy_bits, True, 5) for _ in range(count)]
                results = [f.result() for f in futures]
        else:
            results = [self.generate(entropy_bits) for _ in range(count)]

        logger.info(f"Batch generation complete: {len(results)} mnemonics generated")
        return results

    def get_stats(self) -> dict:
        """Get service statistics."""
        stats = self.stats.copy()
        if self.tracker:
            stats['tracker'] = self.tracker.get_stats()
        return stats


# ============================================================================
# CLI Module
# ============================================================================

def cli():
    """Command-line interface with structured output."""
    import argparse

    parser = argparse.ArgumentParser(
        description='UCAR Cryptographic Mnemonic Generator - Production Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--generate', '-g', action='store_true', help='Generate new mnemonic')
    parser.add_argument('--bits', '-b', type=int, default=256, choices=[128, 160, 192, 224, 256],
                        help='Entropy bits (default: 256 -> 24 words)')
    parser.add_argument('--from-entropy', '-e', type=str, help='Generate mnemonic from hex entropy')
    parser.add_argument('--from-mnemonic', '-m', type=str, help='Convert mnemonic to entropy hex')
    parser.add_argument('--validate', '-v', type=str, help='Validate mnemonic phrase')
    parser.add_argument('--batch', '-B', type=int, help='Batch generate N mnemonics')
    parser.add_argument('--unique', '-u', action='store_true', help='Enforce uniqueness (track duplicates)')
    parser.add_argument('--json', '-j', action='store_true', help='Output in JSON format')
    parser.add_argument('--stats', '-s', action='store_true', help='Show service statistics')

    args = parser.parse_args()

    service = MnemonicService(enforce_uniqueness=args.unique)

    # Handle stats request
    if args.stats:
        if args.json:
            print(json.dumps(service.get_stats(), indent=2))
        else:
            print("=== Service Statistics ===")
            for key, value in service.get_stats().items():
                print(f"{key}: {value}")
        return

    # Handle batch generation
    if args.batch:
        results = service.batch_generate(args.batch, args.bits, parallel=True)
        if args.json:
            output = [r.to_dict() for r in results]
            print(json.dumps(output, indent=2))
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r.mnemonic}")
                print(f"   Hex: {r.entropy_hex}\n")
        return

    # Handle generation
    if args.generate:
        result = service.generate(args.bits)
        if args.json:
            print(result.to_json())
        else:
            print(f"Mnemonic ({result.word_count} words): {result.mnemonic}")
            print(f"Entropy (hex): {result.entropy_hex}")
        return

    # Handle from entropy
    if args.from_entropy:
        result = service.from_entropy(args.from_entropy)
        if args.json:
            print(result.to_json())
        else:
            print(f"Mnemonic: {result.mnemonic}")
        return

    # Handle from mnemonic
    if args.from_mnemonic:
        entropy_hex = service.to_entropy(args.from_mnemonic)
        if args.json:
            print(json.dumps({'entropy_hex': entropy_hex}, indent=2))
        else:
            print(f"Entropy (hex): {entropy_hex}")
        return

    # Handle validation
    if args.validate:
        result = service.validate(args.validate)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Valid: {result['valid']}")
            if result['error']:
                print(f"Error: {result['error']}")
            print(f"Word count: {result['word_count']}")
        return

    # Default: generate single mnemonic
    result = service.generate(256)
    print(result.mnemonic)


# ============================================================================
# API Layer (FastAPI optional - requires pip install fastapi uvicorn)
# ============================================================================

def create_api_app():
    """Create FastAPI application (requires FastAPI to be installed)."""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn

        app = FastAPI(title="UCAR Mnemonic API", version="2.0.0")
        service = MnemonicService(enforce_uniqueness=False)

        class GenerateRequest(BaseModel):
            bits: int = 256

        class GenerateResponse(BaseModel):
            mnemonic: str
            entropy_hex: str
            word_count: int
            entropy_bits: int

        class ValidateRequest(BaseModel):
            mnemonic: str

        class ValidateResponse(BaseModel):
            valid: bool
            error: str = None
            word_count: int

        @app.post("/generate", response_model=GenerateResponse)
        async def generate(request: GenerateRequest):
            result = service.generate(request.bits)
            return result.to_dict()

        @app.post("/validate", response_model=ValidateResponse)
        async def validate(request: ValidateRequest):
            return service.validate(request.mnemonic)

        @app.post("/from-entropy")
        async def from_entropy(entropy_hex: str):
            result = service.from_entropy(entropy_hex)
            return result.to_dict()

        @app.post("/to-entropy")
        async def to_entropy(mnemonic: str):
            return {"entropy_hex": service.to_entropy(mnemonic)}

        @app.get("/stats")
        async def stats():
            return service.get_stats()

        return app

    except ImportError:
        logger.warning("FastAPI not installed. API layer unavailable.")
        return None


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Self-test on startup
    logger.info("UCAR Mnemonic Generator - Production Edition Initializing")

    # Quick validation test
    test_entropy = secrets.token_bytes(32)
    test_mnemonic = MnemonicEngine.entropy_to_mnemonic(test_entropy)
    recovered = MnemonicEngine.mnemonic_to_entropy(test_mnemonic)

    assert test_entropy == recovered, "Round-trip conversion failed"
    assert len(test_mnemonic.split()) == 24, f"Expected 24 words, got {len(test_mnemonic.split())}"

    logger.info("Self-test passed. System ready.")
    logger.info(f"Test mnemonic: {test_mnemonic}")

    if __name__ == "__main__":
        result = MnemonicEngine.generate(128)  # 12 كلمة

    words = result.mnemonic.split()

    for i, word in enumerate(words, 1):
        print(f"{i}- {word}")