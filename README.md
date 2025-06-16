# Digital Twin Telegram Bot - Setup Guide

## Prerequisites

1. **Telegram Bot Token**

   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Save the bot token

2. **Supabase Project**

   - Create account at [supabase.com](https://supabase.com)
   - Create a new project
   - Get your project URL and anon key from Settings > API

3. **OpenAI API Key**
   - Create account at [openai.com](https://openai.com)
   - Generate API key from the dashboard

## Quick Setup

### 1. Clone/Create Project Structure

```bash
mkdir digital-twin-bot
cd digital-twin-bot

# Create the following files:
# - bot.py (main bot code)
# - requirements.txt
# - Dockerfile
# - docker-compose.yml
# - .env
```

### 2. Set Up Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the SQL schema provided to create all tables
4. Optionally, insert some sample data for testing

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env
```

# Digital Twin Bot - Multi-Bot Architecture

🤖 **A Telegram bot system where each digital twin has their own dedicated bot for authentic, isolated conversations.**

## 🎯 **Overview**

This project creates individual Telegram bots for digital twins who share personal stories through natural conversation. Each twin has their own bot identity, personality, and conversation history while sharing a unified database for user profiles and analytics.

### **Key Features**

- 🎭 **Individual Bot Personalities** - Each digital twin has their own dedicated Telegram bot
- 🔒 **Conversation Isolation** - Separate conversation histories per twin
- 🧠 **Smart Story Selection** - AI-powered story matching based on conversation context
- 📚 **Natural Story Progression** - Stories unfold naturally in conversation segments
- 💾 **Persistent Memory** - User relationships build over time with each twin
- 🚀 **Unified Architecture** - Single codebase manages multiple bots efficiently

## 🏗️ **Architecture**

```
┌─────────────────────────────────────┐
│         Multi-Bot Manager           │
├─────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │ Alice   │ │  Bob    │ │ Sarah  │ │
│  │ Bot     │ │ Bot     │ │ Bot    │ │
│  └─────────┘ └─────────┘ └────────┘ │
├─────────────────────────────────────┤
│     PostgreSQL Database             │
│   (Local Dev or Supabase Prod)     │
└─────────────────────────────────────┘
```

### **Twin-Specific Isolation**

- Each bot maintains separate conversation histories
- Story progression is tracked per twin
- User profile is shared (name, interests) but conversations are isolated
- No cross-contamination between twin conversations

## 🚀 **Quick Start**

### **Prerequisites**

1. **Telegram Bot Tokens** - Create separate bots for each twin via @BotFather
2. **OpenAI API Key** - For LLM-powered conversations
3. **Database** - PostgreSQL (local) or Supabase (production)
4. **Docker** - For containerized deployment

### **Development Setup**

1. **Clone and Setup**

   ```bash
   git clone <repository-url>
   cd digital-twin-bot
   ```

2. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Create Telegram Bots**

   ```bash
   # Get setup instructions for your twins
   python scripts/setup-bots.py

   # Test your configuration
   python scripts/test-multi-bots.py
   ```

4. **Start Development Environment**

   ```bash
   make dev-up
   # Or manually: docker-compose -f docker-compose.dev.yml up -d
   ```

5. **Test Your Bots**

   ```bash
   # View logs
   make dev-logs

   # Access database
   make dev-shell
   ```

## 🔧 **Configuration**

### **Bot Configuration Methods**

**Method 1: Individual Environment Variables (Recommended for Development)**

```env
# Alice Chen Bot
BOT_TOKEN_ALICE_CHEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
BOT_USERNAME_ALICE_CHEN=alice_chen_bot

# Bob Martinez Bot
BOT_TOKEN_BOB_MARTINEZ=0987654321:XYZabcDEFghiJKLmnoPQR
BOT_USERNAME_BOB_MARTINEZ=bob_martinez_bot

# Sarah Kim Bot
BOT_TOKEN_SARAH_KIM=5555666677:QWERtyuiASDF
BOT_USERNAME_SARAH_KIM=sarah_kim_bot
```

**Method 2: JSON Configuration (Recommended for Production)**

```env
BOT_CONFIGS={"alice_chen":{"token":"1234567890:ABC...","username":"alice_chen_bot","twin_id":"alice_chen"},"bob_martinez":{"token":"0987654321:XYZ...","username":"bob_martinez_bot","twin_id":"bob_martinez"}}
```

### **Database Configuration**

**Local Development (PostgreSQL)**

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/digital_twin_bot
ENVIRONMENT=development
```

**Production (Supabase)**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_DB_PASSWORD=your_supabase_database_password
ENVIRONMENT=production
```

## 📊 **Database Schema**

The system uses PostgreSQL with twin-specific isolation:

```sql
-- Each twin has separate story progress
user_story_progress (chat_id, story_id, twin_id)

-- Conversation history tracks which twin
conversation_history: [{"twin_id": "alice_chen", "message": "..."}]

-- Sessions are twin-isolated
conversation_sessions (chat_id, twin_id, current_story_id)
```

### **Setup Database**

```bash
# Local development (automatic)
make dev-up

# Production (Supabase)
# 1. Create Supabase project
# 2. Run database/init.sql in SQL Editor
# 3. Run database/seed.sql for sample data
```

## 🎭 **Digital Twins**

The system comes with three sample digital twins:

### **Alice Chen** (@alice_chen_bot)

- **Personality**: Curious, analytical, empathetic, introverted
- **Background**: Software Engineer from Vancouver, loves hiking and photography
- **Stories**: Technical challenges, debugging adventures, learning experiences

### **Bob Martinez** (@bob_martinez_bot)

- **Personality**: Outgoing, creative, optimistic, adventurous
- **Background**: Adventure photographer and travel blogger from California
- **Stories**: Travel adventures, photography expeditions, cultural encounters

### **Sarah Kim** (@sarah_kim_bot)

- **Personality**: Thoughtful, artistic, introspective, wise
- **Background**: Former therapist turned novelist from Seattle
- **Stories**: Personal growth, healing journeys, creative breakthroughs

## 🎯 **User Experience**

### **Natural Conversations**

```
User -> @alice_chen_bot: "I'm debugging a tricky issue at work"
Alice: "Oh interesting! That reminds me of the time I spent 6 hours
        debugging a race condition that only happened in production..."

User -> @bob_martinez_bot: "I love travel photography"
Bob: "Dude! You should hear about my crazy adventure shooting the
     Northern Lights in Iceland during an 80 mph storm..."
```

### **Conversation Commands**

Each bot supports these commands:

- `/start` - Personalized greeting from the twin
- `/about` - Learn about the twin's background
- `/help` - How to chat with this twin
- `/reset` - Clear conversation history with this twin only

## 🚀 **Deployment**

### **Development**

```bash
# Start all services locally
make dev-up

# View logs for all bots
make dev-logs

# Stop development environment
make dev-down
```

### **Production**

```bash
# Configure production environment
cp .env.prod.example .env
# Edit with your production credentials

# Deploy to production
./scripts/deploy-prod.sh

# Or manually
docker-compose -f docker-compose.prod.yml up -d --build
```

### **Cloud Platforms**

**Railway**

```bash
railway init
railway up
# Set environment variables in dashboard
```

**Heroku**

```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN_ALICE_CHEN=...
heroku config:set OPENAI_API_KEY=...
git push heroku main
```

## 🔧 **Development**

### **Project Structure**

```
digital-twin-bot/
├── bot.py                      # Multi-bot entry point
├── src/
│   ├── bot/                    # Bot logic
│   │   ├── digital_twin_bot.py # Individual twin bot
│   │   └── bot_manager.py      # Multi-bot manager
│   ├── core/                   # Business logic
│   │   ├── user_memory.py      # Memory management
│   │   ├── story_matcher.py    # Story selection
│   │   ├── story_manager.py    # Story progression
│   │   └── llm_judge.py        # Conversation AI
│   ├── models/                 # Data models
│   ├── database/               # Database layer
│   └── utils/                  # Utilities
├── database/                   # Schema and seeds
├── scripts/                    # Helper scripts
└── logs/                       # Log files
```

### **Adding New Digital Twins**

1. **Add to Database**

   ```sql
   INSERT INTO digital_twins (twin_id, name, personality_traits, conversational_style, background)
   VALUES ('new_twin', 'New Twin', '["trait1", "trait2"]', '{"formality_level": 0.5}', 'Background...');
   ```

2. **Create Telegram Bot**

   ```bash
   # Message @BotFather
   # /newbot -> "New Twin" -> "new_twin_bot"
   ```

3. **Add Configuration**

   ```env
   BOT_TOKEN_NEW_TWIN=your_new_bot_token
   BOT_USERNAME_NEW_TWIN=new_twin_bot
   ```

4. **Add Stories**
   ```sql
   INSERT INTO stories (story_id, twin_id, title, full_content, themes, conversation_triggers)
   VALUES ('new_story_001', 'new_twin', 'Story Title', 'Story content...', ARRAY['theme1'], ARRAY['trigger1']);
   ```

### **Development Commands**

```bash
make dev-up          # Start development environment
make dev-down        # Stop development environment
make dev-logs        # View bot logs
make dev-shell       # Access database shell
make dev-restart     # Restart bots
make dev-seed        # Add more test data

make prod-up         # Deploy production
make prod-down       # Stop production
make prod-logs       # View production logs

make lint            # Run code linters
make format          # Format code
make test            # Run tests
```

## 🧪 **Testing**

### **Environment Testing**

```bash
# Check environment configuration
python scripts/check-environment.py

# Test database connection
python scripts/test-database.py

# Test multi-bot setup
python scripts/test-multi-bots.py
```

### **Manual Testing**

1. Start development environment: `make dev-up`
2. Find your bots on Telegram (search for usernames)
3. Send `/start` to each bot
4. Have conversations with different twins
5. Verify conversation isolation

## 📈 **Monitoring**

### **Logs**

```bash
# Real-time logs
make dev-logs

# Filter for specific twin
docker-compose -f docker-compose.dev.yml logs | grep "alice_chen"

# Error monitoring
docker-compose logs | grep ERROR
```

### **Database Monitoring**

```bash
# Access database
make dev-shell

# Check active conversations
SELECT twin_id, COUNT(*) FROM conversation_sessions
WHERE session_state = 'active' GROUP BY twin_id;

# User engagement stats
SELECT DATE(created_at) as date, COUNT(*) as new_users
FROM user_memory GROUP BY DATE(created_at) ORDER BY date DESC;
```

## 🔒 **Security**

### **Environment Variables**

- Never commit `.env` files
- Use separate bot tokens for each environment
- Rotate API keys regularly
- Use Supabase RLS policies in production

### **Database Security**

- Use connection pooling
- Enable SSL for production connections
- Implement proper backup strategies
- Monitor for unusual activity

## 🎉 **Features**

### **Intelligent Conversations**

- **LLM Judge** determines when to share stories naturally
- **Context-aware** story selection based on user interests
- **Memory persistence** builds relationships over time
- **Personality consistency** each twin maintains their character

### **Story Management**

- **Segmented storytelling** for natural conversation flow
- **Adaptive content** stories adjust based on conversation context
- **Progress tracking** prevents repetition
- **Emotional intelligence** matches story tone to conversation mood

### **User Experience**

- **No setup required** users just message the bot they want
- **Natural interaction** no special commands needed
- **Persistent relationships** conversations resume where they left off
- **Privacy-focused** each twin's conversations are isolated

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test with: `python scripts/test-multi-bots.py`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

### **Common Issues**

**Bots not responding:**

```bash
# Check logs
make dev-logs

# Verify environment
python scripts/check-environment.py

# Test database
python scripts/test-database.py
```

**Database connection failed:**

```bash
# Check DATABASE_URL or Supabase credentials
# Ensure database is running (for local dev)
# Verify network connectivity
```

**Missing bot configurations:**

```bash
# Run setup helper
python scripts/setup-bots.py

# Check environment variables
python scripts/check-environment.py
```

### **Getting Help**

- Check the logs: `make dev-logs`
- Run diagnostics: `python scripts/test-multi-bots.py`
- Review configuration: `python scripts/check-environment.py`
- Create an issue with logs and configuration details

---

**Built with ❤️ for authentic digital relationships**
ARRAY['debugging', 'work stress', 'problem solving', 'late night coding', 'perseverance']
);

-- Insert story segments for the above story
INSERT INTO story_segments (story_id, segment_order, segment_type, content, transition_hook) VALUES
(
'alice_story_001',
1,
'setup',
'It was 2 AM on a Tuesday, and I was staring at the most confusing bug I had ever encountered. The application would crash randomly, but only in production, never in development.',
'I had already been at this for hours...'
),
(
'alice_story_001',
2,
'conflict',
'I had been debugging for 6 hours straight, surviving on coffee and determination. Every fix I tried just led to more questions. The stack traces were misleading, the logs were cryptic.',
'But then I had a breakthrough...'
),
(
'alice_story_001',
3,
'resolution',
'Finally, I discovered it was a race condition in our async code. When I fixed it and deployed the patch, I felt like I had conquered Mount Everest.',
'That experience changed how I approach debugging...'
),
(
'alice_story_001',
4,
'reflection',
'That bug taught me more about system architecture than any textbook ever could. Now I always think about concurrency and timing when I write async code.',
''
);

````

## Production Deployment

### Cloud Deployment Options

**1. DigitalOcean Droplet**
```bash
# Create a $5/month droplet with Docker pre-installed
# SSH into your droplet
ssh root@your-droplet-ip

# Clone your code
git clone your-repo-url
cd digital-twin-bot

# Set up environment
cp .env.example .env
nano .env  # Add your credentials

# Deploy
docker-compose up -d
````

**2. Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add postgres  # Optional: if you want Railway's postgres
railway deploy
```

**3. Heroku**

```bash
# Install Heroku CLI
heroku create your-bot-name
heroku config:set TELEGRAM_BOT_TOKEN=your-token
heroku config:set SUPABASE_URL=your-url
heroku config:set SUPABASE_ANON_KEY=your-key
heroku config:set OPENAI_API_KEY=your-key

# Deploy
git push heroku main
```

## Monitoring and Maintenance

### View Logs

```bash
# Docker Compose
docker-compose logs -f digital-twin-bot

# Docker
docker logs -f digital-twin-bot

# Filter logs
docker-compose logs -f | grep ERROR
```

### Update the Bot

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Maintenance

```sql
-- Clean old conversation history (run monthly)
UPDATE user_memory
SET conversation_history = (
  SELECT jsonb_agg(elem)
  FROM jsonb_array_elements(conversation_history) elem
  WHERE (elem->>'timestamp')::timestamp > NOW() - INTERVAL '30 days'
)
WHERE jsonb_array_length(conversation_history) > 20;

-- Check bot usage stats
SELECT
  DATE(created_at) as date,
  COUNT(*) as new_users
FROM user_memory
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## Scaling Considerations

### Performance Optimization

1. **Database Indexing**: The schema includes essential indexes
2. **Rate Limiting**: Implement rate limiting for OpenAI API calls
3. **Caching**: Use Redis for frequently accessed data
4. **Connection Pooling**: Configure Supabase connection pooling

### Adding More Digital Twins

```sql
-- Add new twin
INSERT INTO digital_twins (twin_id, name, personality_traits, conversational_style, background) VALUES (
  'bob_martinez',
  'Bob Martinez',
  '["outgoing", "creative", "optimistic", "adventurous"]'::jsonb,
  '{
    "formality_level": 0.2,
    "humor_frequency": 0.8,
    "technical_depth": 0.4,
    "emotional_openness": 0.9,
    "common_phrases": ["Dude!", "That''s awesome!", "You know what I mean?"],
    "vocabulary_complexity": "casual",
    "response_length_preference": "long"
  }'::jsonb,
  'Adventure photographer and travel blogger from California. Always looking for the next great story.'
);

-- Add stories for the new twin
INSERT INTO stories (story_id, twin_id, title, full_content, themes, emotional_tone, conversation_triggers) VALUES (
  'bob_story_001',
  'bob_martinez',
  'The Photo That Changed Everything',
  'I was hiking in Patagonia when I stumbled upon this incredible sunrise over the mountains...',
  ARRAY['travel', 'photography', 'nature', 'inspiration'],
  'inspiring',
  ARRAY['travel', 'photography', 'adventure', 'mountains', 'sunrise']
);
```

## Troubleshooting

### Common Issues

**Bot not responding:**

```bash
# Check if container is running
docker ps

# Check logs for errors
docker-compose logs -f

# Restart the bot
docker-compose restart
```

**Database connection issues:**

```bash
# Test Supabase connection
curl -H "apikey: YOUR_ANON_KEY" "YOUR_SUPABASE_URL/rest/v1/digital_twins"
```

**OpenAI API errors:**

```bash
# Check API key and quota
curl -H "Authorization: Bearer YOUR_OPENAI_KEY" "https://api.openai.com/v1/models"
```

### Environment Variables Debug

```python
# Add this to bot.py for debugging
import os
print("Environment check:")
print(f"Bot token: {'✓' if os.getenv('TELEGRAM_BOT_TOKEN') else '✗'}")
print(f"Supabase URL: {'✓' if os.getenv('SUPABASE_URL') else '✗'}")
print(f"Supabase Key: {'✓' if os.getenv('SUPABASE_ANON_KEY') else '✗'}")
print(f"OpenAI Key: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
```

## Security Best Practices

1. **Environment Variables**: Never commit .env files
2. **API Keys**: Rotate keys regularly
3. **Database**: Use Supabase RLS (Row Level Security) policies
4. **Bot Token**: Keep secure and regenerate if compromised
5. **Logging**: Don't log sensitive user data

## Feature Extensions

### Easy Additions

- **Webhook mode**: Replace polling with webhooks for better performance
- **Admin commands**: Add commands for managing twins and stories
- **Analytics**: Track user engagement and popular stories
- **Multi-language**: Add language detection and translation
- **Voice messages**: Support voice message responses

### Advanced Features

- **Story generation**: Auto-generate stories from prompts
- **Personality learning**: Adapt twin personalities based on user interactions
- **Story branching**: Interactive stories with user choices
- **Memory persistence**: Long-term user relationship memory
- **Group chats**: Multi-user story sessions

This setup provides a solid foundation for your MVP that can easily scale and extend as needed!
