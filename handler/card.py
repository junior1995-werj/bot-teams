from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import datetime
from data_models.connect_db import engine
from data_models.models import AccessedCardModel, CardModel, UserModel

class Card: 

    def __init__(self) -> None:
        self.session = sessionmaker(bind=engine)

    def get_tittle_card_by_team(self, team:str) -> list: 
        sessao = self.session()
        card_models = sessao.query(CardModel).filter(
            and_(
                    CardModel.team == team,
                    CardModel.status == True,
                )
            ).all()

        list_return = []
        for card in card_models: 
            list_return.append(card.tittle)

        return list_return
    
    def get_card_by_tittle(self, tittle) -> CardModel:
        sessao = self.session()
        card_models = sessao.query(CardModel).filter(CardModel.tittle == tittle).first()

        return card_models
    
class AccessedCard:
    def __init__(self) -> None:
        self.session = sessionmaker(bind=engine)

    def create_register(self, username, card_id): 
        sessao = self.session()

        sessao.add(AccessedCardModel(
            id_card=card_id,
            username=username,
            date_accessed=datetime.now()))
        
        sessao.commit()
        sessao.close()