import os
import json


from botbuilder.core import CardFactory, TurnContext,MessageFactory 
from botbuilder.schema import ActivityTypes, Activity, CardAction, HeroCard, Mention, ConversationParameters
from typing import List
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import  Activity
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes

from config import settings

class ProativeMessage:
    def __init__(self, ADAPTER) -> None:
        self.adapter = ADAPTER

    async def notify(self, user, incident):
        await self._send_proactive_message(user, incident)


    async def _send_proactive_message(self, user, incident):

        id_conversarion = TurnContext.get_conversation_reference(
            activity=Activity().deserialize(
            data={
                    "channelId": "msteams",  
                    "from": {"id": user.user_id_teams, "name": user.name},
                    "serviceUrl": user.service_url,
                    "conversation": {'conversationType':'personal', "id": user.conversation_id},
                }
            )
        )

        await self.adapter.continue_conversation(
            id_conversarion,
            lambda turn_context: turn_context.send_activity(f"Ola, Tenho uma atualização para você, no chamado: {incident.cod_incident}"),
            settings.APP_ID,
        )

        await self.adapter.continue_conversation(
            id_conversarion,
            lambda turn_context: turn_context.send_activity(self._create_card(incident=incident)),
            settings.APP_ID,
        )


    def _create_card(self,incident):

        card_path = os.path.join(os.getcwd(), "json_file/card_list_update_incident.json")
        with open(card_path, "rb") as in_file:
            card_base = json.load(in_file)

        card_base['body'][0]['items'][0]['columns'][0]['items'][0]['text'] = incident.cod_incident
        card_base['body'][1]['items'][0]['items'][1]['text'] = incident.description
        card_base['body'][1]['items'][1]['facts'][0]['value'] = incident.module
        card_base['body'][1]['items'][1]['facts'][1]['value'] = incident.last_update
        card_base['body'][1]['items'][1]['facts'][3]['value'] = incident.status
        if incident.operator_name:
            card_base['body'][1]['items'][1]['facts'][2]['value'] = incident.operator_name
        else: 
            card_base['body'][1]['items'][1]['facts'][2]['value'] = "Ainda não Atribuido"
        if incident.last_update_description:
            card_base['body'][3]['items'][0]['columns'][0]['items'][0]['text'] = incident.last_update_description
        else: 
            card_base['body'][3]['items'][0]['columns'][0]['items'][0]['text'] = "Ainda não temos atualização neste chamado"

        message = Activity(
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(card_base)],
        )
        return message
