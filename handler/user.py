from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from data_models.connect_db import engine
from data_models.models import UserModel, UserAuthModel

class User: 

    def __init__(self, name:str=None, user_id_teams:str=None, id_connection:str=None, conversation_id:str=None, service_url:str=None, user_activity:str=None):
        self.name = name
        self.user_id_teams = user_id_teams
        self.id_connection = id_connection
        self.session = sessionmaker(bind=engine)
        self.conversation_id=conversation_id
        self.service_url=service_url
        self.user_activity= user_activity
    
    def update_and_create_user(self):
        sessao = self.session()
        user = sessao.query(UserModel).filter(UserModel.name == str(self.name)).first()
        if user: 
            if user.id_conversation != self.id_connection or user.user_id_teams != self.user_id_teams or user.conversation_id != self.conversation_id: 
                user.user_id_teams = self.user_id_teams
                user.id_conversation = self.id_connection
                user.conversation_id = self.conversation_id
                sessao.add(user)
        else: 
            sessao.add(UserModel(name=self.name, user_id_teams=self.user_id_teams, id_conversation=self.id_connection, conversation_id=self.conversation_id, service_url=self.service_url))

        sessao.commit()
        sessao.close()

    def get_user_by_name(self) -> UserModel:
        sessao = self.session()
        user = sessao.query(UserModel).filter(UserModel.name == str(self.name)).first()
        sessao.close()
        return user
    
    def get_user_by_id(self, id) -> UserModel:
        sessao = self.session()
        user = sessao.query(UserModel).filter(UserModel.id == id).first()
        sessao.close()
        return user

class UserAuth: 

    def __init__(self, name, password) -> None:
        self.name = name 
        self.password = password
        self.session = sessionmaker(bind=engine)
    
    def get_user(self) -> bool:
        sessao = self.session()
        user = sessao.query(UserAuthModel).filter(
                UserAuthModel.name == str(self.name),
            ).first()
        
        if check_password_hash(user.password, self.password):
            return True

        return False
    
    def create_user(self):
        sessao = self.session()
        sessao.add(
            UserAuthModel(
                name=self.name,
                password=generate_password_hash(self.password, method="sha256")
            )
        )
        sessao.commit()
        sessao.close()