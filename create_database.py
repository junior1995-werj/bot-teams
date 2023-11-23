import time
from datetime import datetime

from data_models.models import UserModel, IncidentModel, CardModel, AccessedCardModel, UserAuthModel
from data_models.connect_db import engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from data_models.connect_db import engine
from handler.user import UserAuth

#UserModel.metadata.drop_all(engine)
#IncidentModel.metadata.drop_all(engine)




time.sleep(2)
UserModel.metadata.create_all(engine)
#IncidentModel.metadata.create_all(engine)
#CardModel.metadata.create_all(engine)
#AccessedCardModel.metadata.create_all(engine)

session = sessionmaker(bind=engine)


user = UserAuth(name="admin", password="8Jh72Gp5([-y")
user.create_user()