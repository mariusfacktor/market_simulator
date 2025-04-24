
# guinicorn --bind 0.0.0.0:8000 wsgi:app

from market_sim_backend import app

if __name__ == '__main__':
    app.run()

