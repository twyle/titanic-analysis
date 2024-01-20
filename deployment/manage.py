from api import create_app
from api.helpers import generate_data, post_data
import os


app = create_app()

def seed_data():
    data = generate_data(count=1)
    url: str = os.environ.get('url', 'http://127.0.0.1:8000/predict')
    post_data(data=data, url=url)
    
if __name__ == '__main__':
    seed_data()