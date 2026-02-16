# Environment Variables Guide

## Local Development (.env file)

Create a `.env` file in the root directory and in `backend/`:

```env
# Required
GOOGLE_API_KEY=your-google-api-key

# Security (change in production!)
JWT_SECRET=your-super-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///./products.db

# Optional - Redis for caching
REDIS_URL=redis://localhost:6379

# Optional - Voice (ElevenLabs)
ELEVEN_LABS_KEY=your-elevenlabs-key
VOICE_ID=your-voice-id
```

## Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Production Environment Variables

When deploying, set these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google AI API key for Gemini |
| `JWT_SECRET` | Yes | Strong random string for JWT signing |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | No | Redis for caching and sessions |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |

## Generating Secrets

```bash
# Generate a secure JWT secret
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Or with Python
python -c "import secrets; print(secrets.token_hex(64))"
```
