# Swasth Backend

FastAPI backend for Indian-region meal planning, recipes, grocery lists, and prakriti assessment.
- Single endpoint for meal plans (single or family via members array).
- Structured outputs (JSON Schemas) + optional Redis caching.
- Different OpenAI models per purpose (config/model_map.yml).

## Quick start
```bash
pip install -e .[redis]
cp .env.example .env
# put your OPENAI_API_KEY in .env

uvicorn app.app:create_app --factory --reload
