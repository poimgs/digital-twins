# Digital Twin Bot - Production Deployment Guide

## Prerequisites

1. **Supabase Project Setup**

   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Go to Settings > Database and note down your database password
   - Run the database schema from `database/init.sql` in the SQL Editor
   - Run the seed data from `database/seed.sql`

2. **Environment Configuration**

   ```bash
   # Copy production environment template
   cp .env.prod.example .env

   # Edit with your actual credentials
   nano .env
   ```

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Make deploy script executable
chmod +x scripts/deploy-prod.sh

# Deploy to production
./scripts/deploy-prod.sh
```

### Option 2: Manual Docker Commands

```bash
# Build and run production container
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Option 3: Cloud Platforms

**Railway:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Heroku:**

```bash
# Create Heroku app
heroku create your-bot-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_DB_PASSWORD=your_db_password
heroku config:set OPENAI_API_KEY=your_openai_key

# Deploy
git push heroku main
```

**DigitalOcean Apps:**

1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically on push

## Database Configuration

### Getting Supabase Database Password

1. Go to your Supabase project dashboard
2. Navigate to Settings > Database
3. Under "Connection info", find your database password
4. Use this password in your `SUPABASE_DB_PASSWORD` environment variable

### Connection String Format

The bot automatically constructs the PostgreSQL connection string:

```
postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f digital-twin-bot

# Check specific time range
docker-compose -f docker-compose.prod.yml logs --since=1h digital-twin-bot
```

### Updates

```bash
# Update to latest code
git pull origin main

# Rebuild and redeploy
docker-compose -f docker-compose.prod.yml up -d --build
```

### Backup Considerations

- **Database**: Supabase automatically handles backups
- **Logs**: Set up log rotation if needed
- **Configuration**: Keep environment files secure and backed up

## Security Best Practices

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database Access**: Use connection pooling and proper SSL
3. **API Keys**: Rotate keys regularly
4. **Network Security**: Use private networks when possible
5. **Monitoring**: Set up alerts for errors and downtime

## Troubleshooting

**Common Issues:**

1. **Database Connection Failed**

   - Verify `SUPABASE_DB_PASSWORD` is correct
   - Check Supabase project is active
   - Ensure SSL connections are enabled

2. **Bot Not Responding**

   - Verify `TELEGRAM_BOT_TOKEN` is valid
   - Check OpenAI API key and quota
   - Review logs for specific errors

3. **Memory Issues**
   - Adjust container memory limits if needed
   - Monitor conversation history size
   - Consider implementing data cleanup

**Log Analysis:**

```bash
# Filter for errors
docker-compose -f docker-compose.prod.yml logs | grep ERROR

# Monitor real-time
docker-compose -f docker-compose.prod.yml logs -f | grep -E "(ERROR|WARNING)"
```
