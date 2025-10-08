import os
import random
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

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

# Score Management Routes
# Use environment variable for scores file location, default to local file
SCORES_FILE = os.getenv('SCORES_FILE', 'game_scores.json')
# Ensure scores directory exists
scores_dir = os.path.dirname(os.path.abspath(SCORES_FILE))
if not os.path.exists(scores_dir):
    try:
        os.makedirs(scores_dir)
    except Exception as e:
        logger.warning(f"Could not create scores directory: {e}")

def load_scores():
    """Load scores from JSON file"""
    try:
        if os.path.exists(SCORES_FILE) and os.path.getsize(SCORES_FILE) > 0:
            with open(SCORES_FILE, 'r') as f:
                data = json.load(f)
                # Ensure required keys exist
                if 'number_game' not in data:
                    data['number_game'] = []
                if 'word_game' not in data:
                    data['word_game'] = []
                return data
        return {'number_game': [], 'word_game': []}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Score file corrupted or inaccessible, starting fresh: {e}")
        return {'number_game': [], 'word_game': []}
    except Exception as e:
        logger.error(f"Unexpected error loading scores: {e}")
        return {'number_game': [], 'word_game': []}

def save_scores(scores):
    """Save scores to JSON file"""
    try:
        # Create temporary file first
        temp_file = SCORES_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(scores, f, indent=2)
        # Atomic rename
        if os.path.exists(SCORES_FILE):
            os.remove(SCORES_FILE)
        os.rename(temp_file, SCORES_FILE)
        return True
    except OSError as e:
        logger.warning(f"Could not save scores to file (common on read-only filesystems): {e}")
        # On Render or similar platforms, the filesystem is ephemeral
        # Scores will be lost on restart, but the game will continue to work
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving scores: {e}")
        return False

@app.route('/save-score', methods=['POST'])
def save_score():
    """Save a game score"""
    try:
        # Accept JSON; if missing, log raw body for debugging (Render issues)
        data = request.get_json(silent=True)
        if data is None:
            raw_body = request.data.decode('utf-8', errors='ignore')
            logger.warning(f"/save-score received non-JSON body: {raw_body}")
            return jsonify({"success": False, "error": "Invalid JSON payload"}), 400
        logger.info(f"/save-score payload: {data}")
        game_type = data.get('gameType')  # 'number' or 'word'
        score = data.get('score', 0)
        level = data.get('level', 1)
        words_count = data.get('wordsCount', 0)
        time_played = data.get('timePlayed', 0)
        # Optional enriched metadata (may be absent in older clients)
        range_desc = data.get('range')  # e.g. "1-100"
        memory_time = data.get('memoryTime')
        topic = data.get('topic')
        chain_length = data.get('chainLength')
        
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        # Load existing scores
        scores = load_scores()
        
        # Create score entry
        score_entry = {
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'timestamp': datetime.now().isoformat(),
            'timePlayed': time_played
        }
        
        if game_type == 'number':
            score_entry['level'] = level
            if range_desc:
                score_entry['range'] = range_desc
            if memory_time is not None:
                score_entry['memoryTime'] = memory_time
            scores['number_game'].append(score_entry)
            # Keep only top 10 scores
            scores['number_game'] = sorted(scores['number_game'], 
                                         key=lambda x: x['score'], reverse=True)[:10]
        else:  # word game
            score_entry['wordsCount'] = words_count
            if topic:
                score_entry['topic'] = topic
            if chain_length is not None:
                score_entry['chainLength'] = chain_length
            scores['word_game'].append(score_entry)
            # Keep only top 10 scores
            scores['word_game'] = sorted(scores['word_game'], 
                                       key=lambda x: x['score'], reverse=True)[:10]
        
        # Save scores
        if save_scores(scores):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to save score"})
            
    except Exception as e:
        logger.error(f"Error saving score: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/get-scores/<game_type>')
def get_scores(game_type):
    """Get scores for a specific game type"""
    try:
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        scores = load_scores()
        game_key = f'{game_type}_game'
        
        if game_key in scores:
            return jsonify({"success": True, "scores": scores[game_key]})
        else:
            return jsonify({"success": True, "scores": []})
            
    except Exception as e:
        logger.error(f"Error getting scores: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/clear-scores/<game_type>', methods=['POST'])
def clear_scores(game_type):
    """Clear scores for a specific game type"""
    try:
        if game_type not in ['number', 'word']:
            return jsonify({"success": False, "error": "Invalid game type"})
        
        scores = load_scores()
        game_key = f'{game_type}_game'
        scores[game_key] = []
        
        if save_scores(scores):
            return jsonify({"success": True})
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
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    # Use PORT env var (required by Render) or fall back to FLASK_PORT then 5000
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    # Print startup information
    print("🎮 Shiritori Method Game Server Starting...")
    print("=" * 50)
    
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
    print("   - Score Tracking")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=debug, host=host, port=port)