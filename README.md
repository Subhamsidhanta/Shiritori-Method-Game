# 🎮 Shiritori Method Game

A modern, interactive browser-based game that combines memory training with word games. Features two exciting game modes with beautiful dark theme UI, AI integration, and persistent score tracking.

![Shiritori Method Game](https://img.shields.io/badge/Game-Shiritori%20Method-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![AI](https://img.shields.io/badge/AI-Gemini%20Powered-orange)

## 🌟 Features

### 🧠 Number Memory Mode
- **Customizable Difficulty**: Set your own number range (1-100, 1-1000, etc.)
- **Memory Training**: Configurable display time (1-10 seconds)
- **Progressive Challenge**: Numbers get longer each round
- **15-Second Answer Timer**: Fast-paced memory challenges
- **Score Tracking**: Persistent high scores with detailed statistics

### 📝 Shiritori Word Game Mode
- **Topic-Based Gameplay**: Choose from predefined topics or enter custom ones
- **AI Integration**: Powered by Google's Gemini AI for intelligent gameplay
- **Random Topics**: Let AI pick surprise topics for variety
- **Shiritori Rules**: Each word must start with the last letter of the previous word
- **Sequence Memory**: Arrange word chains to test memory skills
- **Smart Validation**: AI validates words for authenticity and topic relevance
- **15-Second Timer**: Quick-thinking word challenges

### 🎨 Modern Features
- **Beautiful Dark Theme**: Eye-catching gradients and animations
- **Fully Responsive**: Works perfectly on desktop, tablet, and mobile
- **Persistent Scores**: JSON-based score storage with separate leaderboards
- **Real-time Updates**: Live score tracking and notifications
- **Smooth Animations**: Modern CSS effects and transitions
- **Accessibility**: Keyboard navigation and screen reader friendly

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (optional but recommended for full AI features)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/shiritori-method-game.git
   cd shiritori-method-game
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AI features (Optional)**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set environment variable:
     ```bash
     # Windows
     set GEMINI_API_KEY=your_api_key_here
     
     # Mac/Linux
     export GEMINI_API_KEY=your_api_key_here
     ```

4. **Run the game**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

### Using Launcher Scripts

**Windows:**
```bash
./start_game.bat
```

**Mac/Linux:**
```bash
chmod +x start_game.sh
./start_game.sh
```

## 🎯 How to Play

### Number Memory Game
1. Select "Number Memory" mode
2. Configure your preferred settings:
   - **Number Range**: Set minimum and maximum values
   - **Memory Time**: How long numbers are displayed (1-10 seconds)
3. Watch the number sequence carefully during the memory phase
4. Enter the exact sequence when prompted (you have 15 seconds)
5. Each round adds a new number to remember!
6. Score points for each correct sequence

### Word Game (Shiritori Method)
1. Select "Word Game" mode
2. Choose a topic or click "Random Topic" for AI selection
3. AI gives you the first word related to the topic
4. Provide a word that:
   - Starts with the last letter of AI's word
   - Relates to the chosen topic
   - Hasn't been used before
5. Arrange the word sequence correctly when prompted
6. Keep the chain going as long as possible!
7. Score points for each valid word

**Shiritori Rules:**
- Your word must start with the last letter of the previous word
- Words cannot be repeated in the same game
- Words must relate to the chosen topic
- You have 15 seconds to respond

## 🏆 Scoring System

### Number Memory Game
- **1 point** per correct sequence
- **Level tracking** - how many rounds completed
- **Time tracking** - total time played
- **Range difficulty** - stored with each score

### Word Game
- **1 point** per valid word submitted
- **Chain length** - total words in the sequence
- **Topic tracking** - which topic was used
- **Time tracking** - total time played

### Leaderboards
- **Separate scoreboards** for each game mode
- **Top 10 scores** preserved per game type
- **Detailed statistics** including date, difficulty, and performance metrics
- **Persistent storage** using JSON files

## 🛠 Technical Details

### Backend (Python/Flask)
- **Flask 2.3.3** - Modern web framework
- **Google Generative AI** - Gemini API integration
- **JSON Storage** - Persistent score tracking
- **RESTful API** - Clean endpoint design
- **Error Handling** - Comprehensive logging and fallbacks
- **Graceful Degradation** - Works without AI when needed

### Frontend (HTML/CSS/JavaScript)
- **Modern CSS3** - Grid, Flexbox, animations, backdrop filters
- **Vanilla JavaScript** - No frameworks for faster loading
- **Responsive Design** - Mobile-first approach
- **Dark Theme** - Beautiful gradients and visual effects
- **Interactive UI** - Real-time updates and smooth transitions

### AI Integration
- **Smart Word Generation** - Context-aware AI responses
- **Topic Validation** - Ensures words match selected topics
- **Fallback System** - Predefined word lists when AI unavailable
- **Rate Limiting** - Efficient API usage

## 📱 Responsive Design

The game automatically adapts to different screen sizes:
- **Desktop (1200px+)**: Full layout with all features
- **Tablet (768px-1199px)**: Optimized layout for touch interaction
- **Mobile (<768px)**: Compact design with easy touch controls

## 🚀 Deployment

### Deploy to Render

1. **Prepare for deployment**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Create Render service**
   - Go to [Render](https://render.com)
   - Create new "Web Service"
   - Connect your GitHub repository
   - Configure settings:
     - **Name**: shiritori-method-game
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`

3. **Set environment variables**
   ```
   GEMINI_API_KEY=your_api_key_here
   FLASK_ENV=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your game will be available at: `https://your-app-name.onrender.com`

### Deploy to Heroku

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create shiritori-method-game
   ```

3. **Set environment variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key_here
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Deploy to Railway

1. **Connect to Railway**
   - Go to [Railway](https://railway.app)
   - Import from GitHub
   - Select your repository

2. **Configure variables**
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Deploy automatically** - Railway will detect Python and deploy

## 🔧 Configuration

### Environment Variables
```bash
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key

# Flask configuration
FLASK_DEBUG=False                 # Set to True for development
FLASK_HOST=0.0.0.0               # Default host
FLASK_PORT=5000                  # Default port

# Game configuration
DEFAULT_MEMORY_TIME=3            # Default memory time for numbers
DEFAULT_WORD_TIMER=15            # Default word response time
MAX_NUMBER_RANGE=10000           # Maximum allowed number range
```

### Customization Options

**Add new topics** in `app.py`:
```python
TOPICS = [
    "your_custom_topic",
    # ... existing topics
]
```

**Modify fallback words** in `app.py`:
```python
FALLBACK_WORDS = {
    "your_topic": ["word1", "word2", "word3"],
    # ... existing fallback words
}
```

**Adjust game timers** in `static/game.js`:
```javascript
// Word game timer (default: 15 seconds)
game.wordTimeLeft = 15;

// Number game answer timer (default: 15 seconds)
game.answerTimeLeft = 15;
```

## 🔍 API Endpoints

### Game Endpoints
- `GET /` - Main game page
- `POST /get-random-topic` - Get AI-generated random topic
- `POST /get-ai-word` - Get AI word following Shiritori rules
- `POST /validate-word` - Validate if word is real and topic-appropriate

### Score Management
- `POST /save-score` - Save game score
- `GET /get-scores/<game_type>` - Get scores for specific game type
- `POST /clear-scores/<game_type>` - Clear scores for specific game type

### Utility
- `GET /health` - Health check and AI status

## 🐛 Troubleshooting

### Common Issues

**Game doesn't load:**
- Check console for JavaScript errors
- Ensure Python dependencies are installed
- Verify Flask server is running

**AI features not working:**
- Check if `GEMINI_API_KEY` is set correctly
- Verify API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Game will work in fallback mode without AI

**Scores not saving:**
- Check write permissions in application directory
- Verify `game_scores.json` file is created
- Check browser console for API errors

**Main menu not working:**
- Clear browser cache
- Check if all game sections are properly loaded
- Verify JavaScript console for errors

### Development Mode

Run with debug enabled:
```bash
export FLASK_DEBUG=True  # Linux/Mac
set FLASK_DEBUG=True     # Windows
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Test thoroughly before submitting
- Update documentation for new features

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎮 Game Modes Explained

### Number Memory Mode
Based on memory training techniques, this mode:
- Tests short-term memory capacity
- Improves concentration and focus
- Provides customizable difficulty levels
- Tracks progress over time

**Benefits:**
- Enhances working memory
- Improves attention span
- Builds mental agility

### Shiritori Word Game
Based on the traditional Japanese word game:
- Enhances vocabulary
- Improves quick thinking
- Tests topic knowledge
- Combines memory with word skills

**Benefits:**
- Expands vocabulary
- Improves cognitive flexibility
- Enhances topic-based thinking

## � Deployment

### Deploy to Render

This project is configured for easy deployment on [Render](https://render.com/).

#### Option 1: Deploy from GitHub (Recommended)

1. **Fork this repository** to your GitHub account
2. **Sign up/Login** to [Render](https://render.com/)
3. **Create a new Web Service**:
   - Connect your GitHub account
   - Select your forked repository
   - Choose the branch to deploy (usually `main`)
4. **Configure Environment Variables**:
   - Add `GEMINI_API_KEY` with your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Other variables are optional (defaults will be used)
5. **Deploy** - Render will automatically:
   - Install dependencies from `requirements.txt`
   - Start the app using `gunicorn`
   - Provide you with a live URL

#### Option 2: Deploy from Render Dashboard

1. **Upload your code** to Render
2. **Set the following configuration**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Python Version**: 3.11+
3. **Add Environment Variables**:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_ENV=production
   ```
4. **Deploy**

#### Environment Variables for Production

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Optional | Google Gemini AI API key for enhanced features | None (fallback mode) |
| `FLASK_ENV` | No | Flask environment | `production` |
| `FLASK_DEBUG` | No | Enable debug mode | `False` |
| `PORT` | No | Port number (set automatically by Render) | `5000` |

### Deploy to Other Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_api_key_here
git push heroku main
```

#### Railway
```bash
# Install Railway CLI and login
railway login
railway new
railway add --variable GEMINI_API_KEY=your_api_key_here
railway up
```

#### Local Production Testing
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_api_key_here
export FLASK_ENV=production

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

### Deployment Checklist

- [ ] ✅ `gunicorn` added to `requirements.txt`
- [ ] ✅ `render.yaml` configured for Render
- [ ] ✅ `Procfile` created for Heroku compatibility
- [ ] ✅ Environment variables properly configured
- [ ] ✅ Debug mode disabled in production
- [ ] ✅ Health check endpoint available at `/health`
- [ ] ⚠️ API key added to environment variables (required for AI features)

### Post-Deployment

1. **Test your deployment** - Visit your live URL
2. **Configure your API key** - Add it to your platform's environment variables
3. **Monitor logs** - Check for any errors in your platform's dashboard
4. **Set up custom domain** (optional) - Most platforms support custom domains

## �🔮 Future Enhancements

- [ ] **Multiplayer Support** - Real-time games with friends
- [ ] **Voice Recognition** - Speak words instead of typing
- [ ] **Advanced Statistics** - Detailed performance analytics
- [ ] **More Game Modes** - Additional memory challenges
- [ ] **Progressive Web App** - Offline capability
- [ ] **Sound Effects** - Audio feedback and ambience
- [ ] **Achievements System** - Unlockable badges and rewards
- [ ] **Social Features** - Share scores and challenges
- [ ] **Daily Challenges** - Special themed games
- [ ] **Difficulty Levels** - Preset challenge levels

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/shiritori-method-game/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/shiritori-method-game/discussions)
- **Email**: your.email@example.com

---

**Built with ❤️ for memory training and word game enthusiasts!**

**Enjoy playing and training your memory! 🧠✨**