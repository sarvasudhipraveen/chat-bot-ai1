# Local run helper only. Vercel uses api/index.py.
from api.index import app

if __name__ == '__main__':
    app.run(debug=True)
