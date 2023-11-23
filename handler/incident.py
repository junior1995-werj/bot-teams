from sqlalchemy.orm import sessionmaker
from data_models.connect_db import engine
from data_models.models import IncidentModel
from handler.user import User
from datetime import datetime

class Incident: 

    def __init__(self):
        self.session = sessionmaker(bind=engine)
        self.user = User()
    
    def update_and_create_incident(self, cod_incident, user_id=None, brief_description=None, description=None, module=None,
                                   last_update_description=None, status="Pending", operator_name=None):
        """Cria um novo incidente no banco de dados, para um novo incidente é obrigatorio os campos 
        cod_incident, user_id, brief_description, description, module, last_update.
        Os demais campos vão ser alimentados pelo cronjob.
        """
        
        sessao = self.session()
        incidents_model = None
        incident = sessao.query(IncidentModel).filter(IncidentModel.cod_incident == str(cod_incident)).first()
        if incident: 
            if module:
                incident.module = module
            if last_update_description: 
                incident.last_update_description = last_update_description
            if status:
                incident.status = status
            if operator_name: 
                incident.operator_name = operator_name
            if brief_description: 
                incident.brief_description = brief_description
            if description:
                incident.description = description
            
            incident.last_update = datetime.now()
            sessao.add(incident)
        else: 
            incidents_model = IncidentModel(cod_incident=cod_incident, 
                                     user_id=user_id, 
                                     brief_description=brief_description, 
                                     description=description, 
                                     module=module, 
                                     status=status,
                                     last_update_description=last_update_description,
                                     operator_name = operator_name,
                                     last_update=datetime.now())
            sessao.add(incidents_model)
        
        sessao.commit()
        sessao.close()
        
        return self.get_incident_by_cod(cod_incident)

    def get_incident_by_cod(self, cod_incident) -> IncidentModel:
        sessao = self.session()
        incident = sessao.query(IncidentModel).filter(IncidentModel.cod_incident == str(cod_incident)).first()
        sessao.close()
        if incident:
            user = self.user.get_user_by_id(incident.user_id)
            return incident, user
        return None, None
    
    def get_all_incidents(self) -> IncidentModel: 
        sessao = self.session()
        incident = sessao.query(IncidentModel).filter(IncidentModel.status != "Resolvido").all()

        return incident