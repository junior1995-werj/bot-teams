# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import re

from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import PromptOptions, TextPrompt
from handler.user import User

class InitDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(InitDialog, self).__init__(dialog_id or InitDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.welcome_dialog,
                    self.dialog_init,
                ],
            )
        )
        self.padrao = r"tudo\s*bem|est[aá]\s*tudo|tranquilo|tudo\scerto|estou\sbem|bem|ta|ok|tudo"
        self.initial_dialog_id = dialog_id

    async def welcome_dialog(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        name = step_context.context.activity.from_property.name
        id_connection = step_context.context.activity.from_property.aad_object_id
        user_id_teams = step_context.context.activity.from_property.id
        conversation_id = step_context.context.activity.conversation.id
        service_url = step_context.context.activity.service_url

        user = User(name=name,user_id_teams=user_id_teams, id_connection=id_connection, conversation_id=conversation_id, service_url=service_url, user_activity=None)
        user.update_and_create_user()

        return await step_context.prompt(
            TextPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.text(f"Ola! {name}, sou Bot teams. Estou aqui para tirar suas dúvidas!<br> Como você esta?"))
        )
    
    async def dialog_init(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        imput_user = step_context.result
        #team_members = await self._get_paged_members(step_context)
        correspondencia = re.search(self.padrao, imput_user, re.I)
        if correspondencia: 
            await step_context.context.send_activity(f"Fico feliz em ouvir que você está bem!")
            return await step_context.end_dialog() 
        else: 
            await step_context.context.send_activity(f"Tudo vai ficar bem!")
        return await step_context.end_dialog()
