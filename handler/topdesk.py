import requests

from topdesk import Topdesk
from config import settings

from data_models.models import IncidentModel, UserModel
from handler.incident import Incident

OPERATOR_MODULE = {
    "TIC": "8271d2fd-1f12-4071-904b-4a5b26df7091",
    "RH": "5b3d42c3-4719-4b8e-b8e1-30a58de04d74",
}
OBJECT = {
    "TIC" : "5491cbdc-d085-4c5e-aa36-e9017fa78406",
    "RH" : "b38f4cb7-b938-42a8-8c4d-4cff939cc4bd",
}

class TopDesk:
    def __init__(self):
        self.topdesk = Topdesk(url=settings.URL_TOP_DESK, app_creds=(settings.USER_TOP_DESK, settings.PASSWORD_TOP_DESK))
        self.incident = Incident()
        self.data_model = {   
            "request": "",
            "briefDescription" : "",
            "caller" : {
                "email": "", 
                "dynamicName": "",
                "branch": {
                    "id": "", # Corrigir com parametros topdesk
                    "name": "" # Corrigir com parametros topdesk
                }
            },
            "operatorGroup": {
                "id": ""
            },
            "object": {
                "id": ""
            }
        }

    def create_incident(self, user:UserModel, briefDescription:str, request:str, module:str):
        email, id = self._get_email(user.name)
        self.data_model["request"] = request
        self.data_model["briefDescription"] = briefDescription
        self.data_model["caller"]["email"] = email
        self.data_model["caller"]["dynamicName"] = user.name
        self.data_model["operatorGroup"]["id"] = self.get_operator_group(module=module)
        self.data_model["object"]["id"] = self.get_object(module=module)
        
        task_created = self.topdesk.create_incident(data=self.data_model)

        self.incident.update_and_create_incident(cod_incident=task_created['number'],
                                                 brief_description=briefDescription,
                                                 description=request,
                                                 module=module,
                                                 user_id=user.id)       
        return task_created['number']

    @staticmethod
    def _get_email(caller_name:str): 
        url = settings.URL_TOP_DESK + "/tas/api/persons/lookup"
        params = {"name": caller_name}
        user_id_result = requests.get(url=url,params=params, auth=(settings.USER_TOP_DESK, settings.PASSWORD_TOP_DESK)).json()
        user_id = user_id_result['results'][0]['id']
        url = settings.URL_TOP_DESK + f"/tas/api/persons/id/{user_id}"
        user = requests.get(url=url,params=params, auth=(settings.USER_TOP_DESK, settings.PASSWORD_TOP_DESK)).json()
        return user['email'], user_id

    @staticmethod
    def get_operator_group(module):
        return OPERATOR_MODULE[module]
    
    @staticmethod
    def get_object(module):
        return OBJECT[module]
    
    @staticmethod
    def get_actions(id_incident):
        url = settings.URL_TOP_DESK + f"/tas/api/incidents/id/{id_incident}/actions"
        user_id_result = requests.get(url=url, auth=(settings.USER_TOP_DESK, settings.PASSWORD_TOP_DESK))
        
        if user_id_result.status_code == 200: 
            return user_id_result.json()[0]['plainText']
        
        return None

    def get_incident_by_cod_in_topdesk(self, imput_cod_incident, name_user):
        incident_model, username = self.incident.get_incident_by_cod(imput_cod_incident)

        if incident_model:
            if username == name_user:
                return incident_model
        else:
            try:
                incident_model = self.topdesk.incident(imput_cod_incident+" ")
                if name_user == incident_model['operator']['name'] or name_user==incident_model['caller']['dynamicName']:
                    action_by_incident = self.get_actions(incident_model['id'])

                    return self.incident.update_and_create_incident(
                        cod_incident=incident_model['number'],
                        brief_description=incident_model['briefDescription'],
                        description=incident_model['request'],
                        module=incident_model['operatorGroup']['name'],
                        operator_name=incident_model['operator']['name'], 
                        user_id="inserted_by_topdesk_ondemand", 
                        status=incident_model['processingStatus']['name'],
                        last_update_description=action_by_incident
                    )
            except Exception:
                return None
            
    def get_incident_by_cod(self, imput_cod_incident) -> IncidentModel:
        incident_model, username = self.incident.get_incident_by_cod(imput_cod_incident)

        return incident_model
    
    def update_incident_by_database(self, cod_incident:str, data:dict):
        module = None
        last_update_description = None
        status = None
        operator_name = None

        if "module" in data.keys():
            module = data['module']
        if "last_update_description"  in data.keys(): 
            last_update_description = data['last_update_description']
        if "status"  in data.keys():
            status = data['status']
        if "operator_name"  in data.keys(): 
            operator_name = data['operator_name']

        return self.incident.update_and_create_incident(cod_incident=cod_incident, 
                                                        module=module,
                                                        last_update_description=last_update_description,
                                                        status=status,
                                                        operator_name=operator_name)
    
    def get_all(self):
        incident_model = self.incident.get_all_incidents()

        return incident_model