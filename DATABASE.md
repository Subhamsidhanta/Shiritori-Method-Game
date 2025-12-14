# Database Setup for Shiritori Method Game

## Overview
This project now uses PostgreSQL database for persistent score storage, replacing the previous file-based system that was causing issues on Render's ephemeral filesystem.

## Database Schema

### GameScore Table
The main table storing all game scores:

```sql
CREATE TABLE game_scores (
    id SERIAL PRIMARY KEY,
    game_type VARCHAR(20) NOT NULL,           -- 'number' or 'word'
    score INTEGER NOT NULL,
    time_played INTEGER NOT NULL,             -- seconds
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Number game specific fields
    level INTEGER,
    min_range INTEGER,
    max_range INTEGER,
    memory_time INTEGER,
    
    -- Word game specific fields
    topic VARCHAR(100),
    words_count INTEGER,
    chain_length INTEGER,
    
    -- Player metadata (for future features)
    player_id VARCHAR(100),
    player_name VARCHAR(50)
);

CREATE INDEX idx_game_scores_type ON game_scores(game_type);
CREATE INDEX idx_game_scores_score ON game_scores(score DESC);
```

## Local Development Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database:**
   ```bash
   python init_db.py
   ```
   This creates SQLite database locally for development.

3. **Run the Application:**
   ```bash
   python app.py
   ```

## Production Deployment (Render)

### Automatic Setup
The `render.yaml` file is configured to:
1. Create a PostgreSQL database named `shiritori-game-db`
2. Install dependencies
3. Run database initialization during build
4. Set up the DATABASE_URL environment variable

### Manual Database Setup (if needed)
If automatic setup fails, you can manually create the database on Render:

1. **Create Database Service:**
   - Go to Render Dashboard
   - Create new PostgreSQL database
   - Name: `shiritori-game-db`
   - Database: `shiritori_game`
   - User: `shiritori_user`

2. **Get Connection String:**
   - Copy the database connection string
   - Add it as `DATABASE_URL` environment variable in your web service

3. **Initialize Tables:**
   The application will automatically create tables on first run.

## Environment Variables

### Required for Production:
- `DATABASE_URL`: PostgreSQL connection string (auto-set by Render)
- `FLASK_ENV`: Set to `production`

### Optional:
- `GEMINI_API_KEY`: For AI features
- `FLASK_DEBUG`: Set to `false` for production

## Database Operations

### Save Score
```python
# Number game score
save_score_to_db('number', {
    'score': 150,
    'timePlayed': 120,
    'level': 5,
    'minRange': 1,
    'maxRange': 100,
    'memoryTime': 3
})

# Word game score
save_score_to_db('word', {
    'score': 200,
    'timePlayed': 180,
    'topic': 'animals',
    'wordsCount': 12,
    'chainLength': 8
})
```

### Get Top Scores
```python
# Get top 10 number game scores
scores = get_top_scores('number', limit=10)

# Get top 10 word game scores
scores = get_top_scores('word', limit=10)
```

### Clear Scores
```python
# Clear all number game scores
clear_scores_db('number')

# Clear all word game scores
clear_scores_db('word')
```

## API Endpoints

### POST /save-score
Save a new game score to database.

**Request Body:**
```json
{
    "gameType": "number",
    "score": 150,
    "timePlayed": 120,
    "level": 5,
    "minRange": 1,
    "maxRange": 100,
    "memoryTime": 3
}
```

### GET /get-scores/<game_type>
Get top scores for a game type.

**Response:**
```json
{
    "success": true,
    "scores": [
        {
            "id": 1,
            "score": 150,
            "timePlayed": 120,
            "date": "2025-10-14 15:30",
            "level": 5,
            "range": "1-100",
            "memoryTime": 3
        }
    ]
}
```

### POST /clear-scores/<game_type>
Clear all scores for a game type.

## Benefits of PostgreSQL Implementation

1. **Persistent Storage**: Scores survive application restarts
2. **Scalability**: Can handle multiple concurrent users
3. **Data Integrity**: ACID compliance ensures data consistency
4. **Performance**: Indexed queries for fast score retrieval
5. **Reliability**: Automatic backups on managed PostgreSQL services
6. **Future-Proof**: Easy to add features like user authentication, leaderboards, etc.

## Troubleshooting

### Database Connection Issues
- Check DATABASE_URL environment variable
- Verify PostgreSQL service is running
- Check network connectivity

### Migration Issues
- Run `python init_db.py` manually
- Check database user permissions
- Verify table creation logs

### Performance Issues
- Monitor database connections
- Check for missing indexes
- Review query performance