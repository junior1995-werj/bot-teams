from sqlalchemy import  Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "bot_teams_user"
    
    id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(length=255), unique=True)
    user_id_teams = Column(String(length=255))
    id_conversation = Column(String(length=255))
    conversation_id = Column(String(length=255))
    service_url = Column(String(length=255))
    user_activity = Column(String(length=255))


    def __init__(
        self, name:str, user_id_teams:str, id_conversation:str, conversation_id:str, service_url:str, user_activity:str=None
    ):
        self.name = name
        self.user_id_teams = user_id_teams
        self.id_conversation = id_conversation
        self.conversation_id = conversation_id
        self.service_url = service_url
        self.user_activity = user_activity


class IncidentModel(Base):
    __tablename__ = "bot_teams_incident"
    
    id = Column(Integer(), primary_key=True, index=True)
    cod_incident = Column(String(length=255), index=True)
    user_id = Column(String(length=255))
    brief_description = Column(String(length=255))
    description = Column(String(length=255))
    module = Column(String(length=255))
    last_update = Column(DateTime())
    last_update_description = Column(String(length=255))
    status = Column(String(length=255))
    operator_name = Column(String(length=255))

    def __init__(self, cod_incident, user_id, brief_description, description, module, last_update, last_update_description = None, status="pending", operator_name= None):
        self.cod_incident = cod_incident
        self.user_id = user_id
        self.brief_description = brief_description
        self.description = description
        self.module = module
        self.last_update = last_update
        self.last_update_description = last_update_description
        self.status = status
        self.operator_name = operator_name

class UserAuthModel(Base):
    __tablename__ = "bot_teams_user_auth"
    
    id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(length=255), unique=True)
    password = Column(String(length=255))


    def __init__(
        self, name:str, password:str
    ):
        self.name = name
        self.password = password

class CardModel(Base):
    __tablename__ = "bot_teams_card"

    id = Column(Integer(), primary_key=True, index=True)
    tittle = Column(String(length=255)) 
    description = Column(Text()) 
    recurring_send = Column(Boolean()) 
    card_options = Column(Boolean()) 
    last_update = Column(DateTime())
    created_at = Column(DateTime())
    team = Column(String(length=255)) 
    status = Column(Boolean()) 

    def __init__(
        self, tittle, description, recurring_send, card_options, last_update, created_at, team, status=True 
    ):
        self.tittle = tittle
        self.description = description
        self.recurring_send = recurring_send
        self.card_options = card_options
        self.last_update = last_update
        self.created_at = created_at
        self.team = team
        self.status = status

class AccessedCardModel(Base): 
    __tablename__ = "bot_teams_accessed_card"

    id = Column(Integer(), primary_key=True, index=True)
    username = Column(String(length=255)) 
    id_card = Column(String(length=255)) 
    date_accessed = Column(DateTime())

    def __init__(self, username, id_card, date_accessed):
        self.username = username
        self.id_card = id_card
        self.date_accessed = date_accessed
