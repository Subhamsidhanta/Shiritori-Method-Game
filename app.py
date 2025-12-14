import os
import random
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Try to import Flask-Migrate, but gracefully handle if not available
try:
    from flask_migrate import Migrate  # type: ignore
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False
    Migrate = None

# Try to import Gemini AI, but gracefully handle if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Fix for Heroku/Render postgres URLs
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shiritori_game.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

# Initialize database
db = SQLAlchemy(app)

# Initialize migration support if available
if MIGRATE_AVAILABLE:
    migrate = Migrate(app, db)
else:
    migrate = None

# Configure Flask app for production
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_ENV') != 'production'
# Ensure proper static file handling in production
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # 1 hour cache for static files

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini AI successfully configured")
    except Exception as e:
        logger.warning(f"Failed to configure Gemini AI: {e}")
        model = None
else:
    if not GENAI_AVAILABLE:
        logger.warning("google-generativeai package not installed. AI features disabled.")
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not found. AI features will use fallback responses.")
    model = None

class GameData:
    """Class to store game-related data and configurations"""
    
    # Predefined topics for random selection
    TOPICS = [
        "fruits", "vegetables", "animals", "colors", "countries", "cities",
        "programming languages", "movies", "books", "sports", "cars", "flowers",
        "musical instruments", "planets", "professions", "food", "drinks",
        "games", "electronics", "clothes", "emotions", "weather", "seasons"
    ]
    
    # Fallback words for different topics when AI is not available
    FALLBACK_WORDS = {
        "fruits": ["apple", "banana", "cherry", "elderberry", "fig", "grape", "honeydew", "ice apple", "elderberry"],
        "animals": ["ant", "bear", "cat", "dog", "elephant", "fox", "giraffe", "horse", "iguana", "jackal"],
        "colors": ["red", "orange", "yellow", "blue", "green", "purple", "pink", "khaki", "indigo", "olive"],
        "countries": ["australia", "brazil", "canada", "denmark", "egypt", "france", "germany", "hungary", "india", "japan"],
        "programming": ["python", "java", "javascript", "kotlin", "lua", "ruby", "swift", "typescript", "erlang", "go"],
        "programming languages": ["python", "java", "javascript", "kotlin", "lua", "ruby", "swift", "typescript", "erlang", "go"],
        "vegetables": ["asparagus", "broccoli", "carrot", "daikon", "eggplant", "fennel", "garlic", "herbs", "iceberg lettuce", "jalapeno"],
        "movies": ["avatar", "batman", "casablanca", "dune", "elf", "frozen", "gladiator", "hulk", "inception", "jaws"],
        "sports": ["archery", "baseball", "cricket", "diving", "equestrian", "football", "golf", "hockey", "ice skating", "judo"],
        "cars": ["audi", "bmw", "chevrolet", "dodge", "ferrari", "ford", "honda", "infiniti", "jaguar", "kia"],
        "default": ["apple", "elephant", "tiger", "rainbow", "ocean", "mountain", "star", "tree", "eagle", "earth"]
    }
    
    # Topic validation keywords for strict checking
    TOPIC_KEYWORDS = {
        "fruits": ["fruit", "berry", "citrus", "tropical", "sweet", "juice", "vitamin"],
        "animals": ["animal", "mammal", "bird", "reptile", "amphibian", "fish", "insect", "wildlife", "pet", "zoo"],
        "colors": ["color", "colour", "shade", "hue", "tint", "pigment", "bright", "dark", "light"],
        "countries": ["country", "nation", "state", "republic", "kingdom", "territory", "continent", "capital"],
        "programming": ["language", "code", "programming", "software", "development", "computer", "syntax", "framework"],
        "programming languages": ["language", "code", "programming", "software", "development", "computer", "syntax", "framework"],
        "vegetables": ["vegetable", "veggie", "plant", "garden", "nutrition", "healthy", "vitamin", "mineral"],
        "movies": ["movie", "film", "cinema", "director", "actor", "actress", "hollywood", "entertainment"],
        "sports": ["sport", "game", "athletic", "competition", "team", "player", "ball", "field", "court"],
        "cars": ["car", "vehicle", "automobile", "motor", "engine", "brand", "model", "transportation"]
    }

# Database Models
class GameScore(db.Model):
    __tablename__ = 'game_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(20), nullable=False, index=True)  # 'number' or 'word'
    score = db.Column(db.Integer, nullable=False)
    
    # Common fields
    time_played = db.Column(db.Integer, nullable=False)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Number game specific fields
    level = db.Column(db.Integer, nullable=True)
    min_range = db.Column(db.Integer, nullable=True)
    max_range = db.Column(db.Integer, nullable=True)
    memory_time = db.Column(db.Integer, nullable=True)
    
    # Word game specific fields
    topic = db.Column(db.String(100), nullable=True)
    words_count = db.Column(db.Integer, nullable=True)
    chain_length = db.Column(db.Integer, nullable=True)
    
    # Player metadata (optional for future features)
    player_id = db.Column(db.String(100), nullable=True)
    player_name = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<GameScore {self.game_type}: {self.score} points>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'score': self.score,
            'timePlayed': self.time_played,
            'date': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'timestamp': self.created_at.isoformat()
        }
        
        if self.game_type == 'number':
            data.update({
                'level': self.level,
                'range': f"{self.min_range}-{self.max_range}" if self.min_range and self.max_range else None,
                'memoryTime': self.memory_time
            })
        elif self.game_type == 'word':
            data.update({
                'topic': self.topic,
                'wordsCount': self.words_count,
                'chainLength': self.chain_length
            })
        
        return data

# Database initialization function
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No Content

# Explicit static file serving for production environments
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files explicitly in production"""
    return send_from_directory('static', filename)

@app.route('/get-random-topic', methods=['POST'])
def get_random_topic():
    """Get a random topic for the word game"""
    try:
        if model and GEMINI_API_KEY and GENAI_AVAILABLE:
            # Use AI to generate a creative topic
            prompt = """Generate a single creative topic for a word game. 
            The topic should be something that has many related words.
            Examples: fruits, animals, programming languages, movie genres, etc.
            Respond with just the topic name, nothing else."""
            
            response = model.generate_content(prompt)
            topic = response.text.strip().lower()
            
            # Validate that it's a reasonable topic
            if len(topic.split()) <= 3 and len(topic) > 2:
                return jsonify({"success": True, "topic": topic})
        
        # Fallback to predefined topics
        topic = random.choice(GameData.TOPICS)
        return jsonify({"success": True, "topic": topic})
        
    except Exception as e:
        logger.error(f"Error generating random topic: {e}")
        topic = random.choice(GameData.TOPICS)
        return jsonify({"success": True, "topic": topic})

@app.route('/get-ai-word', methods=['POST'])
def get_ai_word():
    """Get a word from AI following Shiritori rules"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').lower()
        last_word = data.get('lastWord')
        used_words = data.get('usedWords', [])
        
        # Determine starting character
        start_char = last_word[-1].lower() if last_word else None
        
        if model and GEMINI_API_KEY and GENAI_AVAILABLE:
            # Create AI prompt
            if start_char:
                prompt = f"""You are playing a Shiritori word game about "{topic}".
                Generate a word that:
                1. Starts with the letter "{start_char.upper()}"
                2. Is related to the topic "{topic}" (can be loosely related)
                3. Has not been used: {', '.join(used_words) if used_words else 'none used yet'}
                4. Is a real word
                
                Respond with just the word, nothing else."""
            else:
                prompt = f"""You are starting a Shiritori word game about "{topic}".
                Generate a word that:
                1. Is related to the topic "{topic}" (can be loosely related)
                2. Is a real word
                3. Would be a good starting word for this topic
                
                Respond with just the word, nothing else."""
            
            response = model.generate_content(prompt)
            ai_word = response.text.strip().lower()
            
            # Validate the word
            if (not start_char or ai_word.startswith(start_char)) and \
               ai_word not in used_words and \
               len(ai_word) > 1 and \
               ai_word.isalpha():
                return jsonify({"success": True, "word": ai_word})
        
        # Fallback word generation
        ai_word = generate_fallback_word(topic, start_char, used_words)
        return jsonify({"success": True, "word": ai_word})
        
    except Exception as e:
        logger.error(f"Error generating AI word: {e}")
        ai_word = generate_fallback_word(
            data.get('topic', 'default'),
            data.get('lastWord', '')[-1] if data.get('lastWord') else None,
            data.get('usedWords', [])
        )
        return jsonify({"success": True, "word": ai_word})

def generate_fallback_word(topic: str, start_char: Optional[str], used_words: List[str]) -> str:
    """Generate a fallback word when AI is not available"""
    # Get word list for topic
    topic_key = topic if topic in GameData.FALLBACK_WORDS else 'default'
    word_list = GameData.FALLBACK_WORDS[topic_key].copy()
    
    # Filter words based on starting character and usage
    if start_char:
        word_list = [word for word in word_list if word.startswith(start_char.lower())]
    
    # Remove used words
    word_list = [word for word in word_list if word not in used_words]
    
    # If no words available, generate a simple one
    if not word_list:
        if start_char:
            # Generate a simple word starting with the required character
            simple_words = {
                'a': 'apple', 'b': 'ball', 'c': 'cat', 'd': 'dog', 'e': 'egg',
                'f': 'fish', 'g': 'game', 'h': 'house', 'i': 'ice', 'j': 'jump',
                'k': 'kite', 'l': 'lion', 'm': 'moon', 'n': 'nest', 'o': 'ocean',
                'p': 'pen', 'q': 'queen', 'r': 'red', 's': 'sun', 't': 'tree',
                'u': 'umbrella', 'v': 'van', 'w': 'water', 'x': 'box', 'y': 'yes', 'z': 'zoo'
            }
            return simple_words.get(start_char.lower(), 'end')
        else:
            return random.choice(['apple', 'ball', 'cat', 'dog', 'elephant'])
    
    return random.choice(word_list)

@app.route('/validate-word', methods=['POST'])
def validate_word():
    """Validate if a word is a real English word"""
    try:
        data = request.get_json()
        word = data.get('word', '').lower().strip()
        topic = data.get('topic', '').lower()
        
        # Basic validation
        if not word or not word.isalpha() or len(word) < 2:
            return jsonify({"valid": False, "reason": "Invalid word format"})
        
        if model and GEMINI_API_KEY and GENAI_AVAILABLE:
            # Use AI to validate if it's a real English word
            prompt = f"""Is "{word}" a real English word that exists in the dictionary?

Rules:
- Check if this is a legitimate English word
- Accept common words, proper nouns, and valid English terms
- Reject made-up words, nonsense, or gibberish
- Accept plurals, verb forms, and common variations

Word to check: "{word}"

Respond with only "YES" if it's a real English word, or "NO" if it's not a real word."""
            
            response = model.generate_content(prompt)
            ai_response = response.text.strip().upper()
            is_valid = ai_response == "YES"
            
            logger.info(f"Word validation - Word: '{word}', AI Response: '{ai_response}', Valid: {is_valid}")
            
            return jsonify({
                "valid": is_valid,
                "reason": f"'{word}' is not a recognized English word" if not is_valid else None
            })
        
        # Fallback validation - check against common English words
        is_valid = validate_real_word_fallback(word)
        reason = "Valid English word" if is_valid else f"'{word}' is not a recognized English word"
        return jsonify({"valid": is_valid, "reason": reason})
        
    except Exception as e:
        logger.error(f"Error validating word: {e}")
        # Be lenient on errors - accept the word
        return jsonify({"valid": True})

def validate_real_word_fallback(word: str) -> bool:
    """Fallback validation to check if a word is likely a real English word"""
    word = word.lower().strip()
    
    # Very basic validation - reject obviously fake words
    # Accept most words but reject some obvious patterns
    
    # Reject if too many repeated characters
    if len(set(word)) < len(word) / 3:  # Too many repeated characters
        return False
    
    # Reject if too many consonants in a row
    vowels = set('aeiou')
    consonant_count = 0
    for char in word:
        if char in vowels:
            consonant_count = 0
        else:
            consonant_count += 1
            if consonant_count > 4:  # Too many consonants in a row
                return False
    
    # Check against some common English words and patterns
    common_words = {
        # Common short words
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'his',
        'have', 'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how',
        'their', 'if', 'up', 'out', 'many', 'then', 'them', 'can', 'would',
        'like', 'into', 'him', 'time', 'two', 'more', 'go', 'no', 'way',
        'could', 'my', 'than', 'first', 'been', 'call', 'who', 'oil', 'sit',
        'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made',
        'may', 'part', 'over', 'new', 'sound', 'take', 'only', 'little',
        'work', 'know', 'place', 'year', 'live', 'me', 'back', 'give',
        'most', 'very', 'after', 'thing', 'our', 'just', 'name', 'good',
        'sentence', 'man', 'think', 'say', 'great', 'where', 'help',
        'through', 'much', 'before', 'line', 'right', 'too', 'mean', 'old',
        'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show',
        'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end',
        'why', 'again', 'turn', 'here', 'off', 'went', 'old', 'number',
        'great', 'tell', 'men', 'say', 'small', 'every', 'found', 'still',
        'between', 'mane', 'should', 'home', 'big', 'give', 'air', 'line',
        'set', 'own', 'under', 'read', 'last', 'never', 'us', 'left',
        'end', 'along', 'while', 'might', 'next', 'sound', 'below', 'saw',
        'something', 'thought', 'both', 'few', 'those', 'always', 'looked',
        'show', 'large', 'often', 'together', 'asked', 'house', 'don',
        'world', 'going', 'want', 'school', 'important', 'until', 'form',
        'food', 'keep', 'children', 'feet', 'land', 'side', 'without',
        'boy', 'once', 'animal', 'life', 'enough', 'took', 'four', 'head',
        'above', 'kind', 'began', 'almost', 'live', 'page', 'got', 'earth',
        'need', 'far', 'hand', 'high', 'year', 'mother', 'light', 'country',
        'father', 'let', 'night', 'picture', 'being', 'study', 'second',
        'soon', 'story', 'since', 'white', 'ever', 'paper', 'hard', 'near',
        'sentence', 'better', 'best', 'across', 'during', 'today', 'however',
        'sure', 'knew', 'it', 'try', 'told', 'young', 'sun', 'thing',
        'whole', 'hear', 'example', 'heard', 'several', 'change', 'answer',
        'room', 'sea', 'against', 'top', 'turned', 'learn', 'point',
        'city', 'play', 'toward', 'five', 'himself', 'usually', 'money',
        'seen', 'didn', 'car', 'morning', 'I', 'words', 'family', 'running',
        'red', 'blue', 'green', 'yellow', 'black', 'white', 'orange', 'purple',
        'apple', 'banana', 'cat', 'dog', 'house', 'tree', 'water', 'fire',
        'book', 'chair', 'table', 'computer', 'phone', 'car', 'food', 'love'
    }
    
    # Accept if it's a common word
    if word in common_words:
        return True
    
    # Accept words with common English patterns
    # Most English words are acceptable unless they're obviously nonsense
    return True

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        ai_status = "available" if (model and GEMINI_API_KEY and GENAI_AVAILABLE) else "fallback"
        return jsonify({
            "status": "healthy",
            "ai_status": ai_status,
            "genai_installed": GENAI_AVAILABLE,
            "has_api_key": bool(GEMINI_API_KEY),
            "version": "1.0.0",
            "flask_env": os.getenv('FLASK_ENV', 'development'),
            "port": os.getenv('PORT', 'not set')
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "version": "1.0.0"
        }), 500

# Database Score Management Functions
def save_score_to_db(game_type, score_data):
    """Save score to PostgreSQL database"""
    try:
        # Create new score record
        new_score = GameScore(
            game_type=game_type,
            score=score_data['score'],
            time_played=score_data['timePlayed'],
            player_id=score_data.get('playerId'),
            player_name=score_data.get('playerName')
        )
        
        # Add game-specific fields
        if game_type == 'number':
            new_score.level = score_data.get('level')
            new_score.min_range = score_data.get('minRange')
            new_score.max_range = score_data.get('maxRange')
            new_score.memory_time = score_data.get('memoryTime')
        elif game_type == 'word':
            new_score.topic = score_data.get('topic')
            new_score.words_count = score_data.get('wordsCount')
            new_score.chain_length = score_data.get('chainLength')
        
        # Save to database
        db.session.add(new_score)
        db.session.commit()
        
        logger.info(f"Score saved successfully: {game_type} - {score_data['score']} points")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error saving score: {e}")
        db.session.rollback()
        return False
    except Exception as e:
        logger.error(f"Error saving score to database: {e}")
        db.session.rollback()
        return False

def get_top_scores(game_type, limit=10):
    """Get top scores for a game type from database"""
    try:
        scores = GameScore.query.filter_by(game_type=game_type)\
                              .order_by(GameScore.score.desc())\
                              .limit(limit)\
                              .all()
        
        return [score.to_dict() for score in scores]
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting scores: {e}")
        return []
    except Exception as e:
        logger.error(f"Error getting scores from database: {e}")
        return []

def clear_scores_db(game_type):
    """Clear all scores for a game type from database"""
    try:
        GameScore.query.filter_by(game_type=game_type).delete()
        db.session.commit()
        logger.info(f"Cleared all {game_type} scores from database")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error clearing scores: {e}")
        db.session.rollback()
        return False
    except Exception as e:
        logger.error(f"Error clearing scores from database: {e}")
        db.session.rollback()
        return False

@app.route('/save-score', methods=['POST'])
def save_score():
    """Save a game score to PostgreSQL database"""
    try:
        # Accept JSON; if missing, log raw body for debugging
        data = request.get_json(silent=True)
        if data is None:
            raw_body = request.data.decode('utf-8', errors='ignore')
            logger.warning(f"/save-score received non-JSON body: {raw_body}")
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        
        logger.info(f"/save-score payload: {data}")
        
        game_type = data.get('gameType')  # 'number' or 'word'
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        # Prepare score data
        score_data = {
            'score': data.get('score', 0),
            'timePlayed': data.get('timePlayed', 0),
            'playerId': data.get('playerId'),
            'playerName': data.get('playerName')
        }
        
        # Add game-specific data
        if game_type == 'number':
            score_data.update({
                'level': data.get('level', 1),
                'minRange': data.get('minRange'),
                'maxRange': data.get('maxRange'),
                'memoryTime': data.get('memoryTime')
            })
        elif game_type == 'word':
            score_data.update({
                'topic': data.get('topic'),
                'wordsCount': data.get('wordsCount', 0),
                'chainLength': data.get('chainLength')
            })
        
        # Save to database
        if save_score_to_db(game_type, score_data):
            return jsonify({"success": True, "message": "Score saved successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to save score to database"})
            
    except Exception as e:
        logger.error(f"Error in save_score endpoint: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/get-scores/<game_type>')
def get_scores(game_type):
    """Get top scores for a specific game type from database"""
    try:
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        scores = get_top_scores(game_type, limit=10)
        return jsonify({"success": True, "scores": scores})
            
    except Exception as e:
        logger.error(f"Error getting scores: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/clear-scores/<game_type>', methods=['POST'])
def clear_scores(game_type):
    """Clear all scores for a specific game type in database"""
    try:
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        if clear_scores_db(game_type):
            return jsonify({"success": True, "message": f"All {game_type} scores cleared"})
        else:
            return jsonify({"success": False, "error": "Failed to clear scores"})
            
    except Exception as e:
        logger.error(f"Error clearing scores: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/_debug/request', methods=['POST'])
def debug_request():
    """Diagnostic endpoint to inspect request on Render vs local."""
    try:
        payload = request.get_json(silent=True)
        return jsonify({
            'method': request.method,
            'headers': {k: v for k, v in request.headers.items()},
            'json': payload,
            'raw': request.data.decode('utf-8', errors='ignore'),
            'content_type': request.content_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/_debug/client-log', methods=['POST'])
def client_log():
    """Receive client-side diagnostics (used only temporarily for debugging)."""
    payload = request.get_json(silent=True) or {}
    logger.info(f"CLIENT-DIAG: {payload}")
    return jsonify({"received": True})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    # Use PORT env var (required by Render) or fall back to FLASK_PORT then 5000
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    # Print startup information
    print("🎮 Shiritori Method Game Server Starting...")
    print("=" * 50)
    
    # Database info
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    if 'postgresql' in db_url:
        print("🗄️  Database: PostgreSQL (Production)")
    else:
        print("🗄️  Database: SQLite (Development)")
    
    if GENAI_AVAILABLE and GEMINI_API_KEY and model:
        print("✅ Gemini AI: Enabled")
        print("   - Random topic generation: Available")
        print("   - Smart word validation: Available") 
        print("   - AI opponent: Available")
    elif GENAI_AVAILABLE and not GEMINI_API_KEY:
        print("⚠️  Gemini AI: Disabled (No API key)")
        print("   - Using fallback responses")
        print("   - Limited word validation")
        print("   - To enable AI features:")
        print("     1. Get API key from https://makersuite.google.com/app/apikey")
        print("     2. Set environment variable: GEMINI_API_KEY=your_key_here")
    else:
        print("⚠️  Gemini AI: Disabled (Package not installed)")
        print("   - Using fallback responses")
        print("   - Limited word validation")
        print("   - To enable AI features:")
        print("     1. Install: pip install google-generativeai")
        print("     2. Get API key from https://makersuite.google.com/app/apikey")
        print("     3. Set environment variable: GEMINI_API_KEY=your_key_here")
    
    print("=" * 50)
    print(f"🌐 Game URL: http://{host}:{port}")
    print("📝 Game Features:")
    print("   - Number Memory Game")
    print("   - Shiritori Word Game")
    print("   - Responsive Design")
    print("   - PostgreSQL Score Tracking")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=debug, host=host, port=port)