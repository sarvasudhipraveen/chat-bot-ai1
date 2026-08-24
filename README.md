# AI Chatbot - Vercel Deploy Ready

Upload these files/folders to GitHub root:

- api/index.py
- app.py
- requirements.txt
- runtime.txt
- vercel.json
- README.md

In Vercel Environment Variables add:

GROQ_API_KEY = your_real_groq_api_key

Then redeploy.

For local development, the key is stored in `.env` and loaded automatically. Install dependencies with `pip install -r requirements.txt`, then run `python app.py`.
