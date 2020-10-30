""" Seed database with sample user, board and posts """

from app import db
from models import User, Post, Board
import requests


db.drop_all()
db.create_all()


u1 = User.signup("Bob", "Dillon", "bdillon5", "Ieatchickens")

u1.id = 3838

db.session.add(u1)
db.session.commit()

b1 = Board(title="General", description="A hodge podge collection of cool stuff!", user_id=3838)

db.session.add(b1)
db.session.commit()




