
from aiohttp import web

from aiohttp.web import Request
from bots.dialog_proative_message import ProativeMessage
from handler.topdesk import TopDesk


class ProativeMessageUpdateIncident:
    def __init__(self, ADAPTER) -> None:
        self.proative = ProativeMessage(ADAPTER)

    @staticmethod
    async def last_update_incident_get( req: Request):
        cod_incident = req.match_info['cod_incident']
        incident = TopDesk().get_incident_by_cod(cod_incident)
        data = {}
        if incident:
            data = {
                "id":str(incident.id),
                "cod_incident":incident.cod_incident,
                "user_id":incident.user_id,
                "brief_description":incident.brief_description,
                "description":incident.description,
                "module":incident.module,
                "last_update":str(incident.last_update),
                "last_update_description":incident.last_update_description,
                "status":incident.status,
                "operator_name":incident.operator_name
            }
        return web.json_response(data)


    async def last_update_incident_patch(self, req: Request):   

        request = await req.json()
        cod_incident = req.match_info['cod_incident']
        incident, user = TopDesk().update_incident_by_database(cod_incident, request)
        data = {}
        if incident:
            data = {
                "id":str(incident.id),
                "cod_incident":incident.cod_incident,
                "user_id":incident.user_id,
                "brief_description":incident.brief_description,
                "description":incident.description,
                "module":incident.module,
                "last_update":str(incident.last_update),
                "last_update_description":incident.last_update_description,
                "status":incident.status,
                "operator_name":incident.operator_name
            }
        
        await self.proative.notify(user, incident)

        return web.json_response(data)
    
    
    @staticmethod
    async def get_all_incidents(req: Request):
        incidents = TopDesk().get_all()
        data = []
        if incidents:
            for incident in incidents: 
                data.append({
                    "id":str(incident.id),
                    "cod_incident":incident.cod_incident,
                    "user_id":incident.user_id,
                    "brief_description":incident.brief_description,
                    "description":incident.description,
                    "module":incident.module,
                    "last_update":str(incident.last_update),
                    "last_update_description":incident.last_update_description,
                    "status":incident.status,
                    "operator_name":incident.operator_name
                })
        return web.json_response(data)