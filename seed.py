""" Seed database with sample user, board and posts """

from app import db
from models import User, Post, Board
import requests


db.drop_all()
db.create_all()


u1 = User.signup("Bob", "Dillon", "bdillon5", "bob@bob.com", "Ieatchickens")

u1.id = 3838

db.session.add(u1)
db.session.commit()

b1 = Board(title="General", description="A hodge podge collection of cool stuff!", user_id=3838)

db.session.add(b1)
db.session.commit()

authdata = {"key": "5de43e49ee756412a082e563990f3740", "q": "https://www.urlencoder.io/python/"}
authdata2 = {"key": "5de43e49ee756412a082e563990f3740", "q": "https://www.google.com"}

resp = requests.get("http://api.linkpreview.net/", params=authdata)

p1 = Post(title=resp.json()["title"], description=resp.json()["description"], image_url=resp.json()["image"], url=resp.json()["url"], board_id=1)

db.session.add(p1)
db.session.commit()


