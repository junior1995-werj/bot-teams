import json
import os

from botbuilder.core import  CardFactory, MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import TextPrompt, ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice
from botbuilder.schema import ActivityTypes, Activity
from handler.card import AccessedCard

from handler.topdesk import TopDesk
from handler.user import User


CARD_PROMPT = "cardPrompt"


class DialogTopdeskCreateIncident(ComponentDialog):
    def __init__(self, dialog_id: str = None, module:str = None):
        super(DialogTopdeskCreateIncident, self).__init__(dialog_id or DialogTopdeskCreateIncident.__name__)

        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.incident_question,
                    self.problem_description,
                    self.open_case,
                ],
            )
        )
        self.module = module
        self.initial_dialog_id = dialog_id
        self.accessed_card = AccessedCard()

    async def incident_question(self, step_context:WaterfallStepContext): 
        return await step_context.prompt(
            CARD_PROMPT,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Deseja abrir um chamado? "
                ),
                retry_prompt=MessageFactory.text(
                    "Deseja abrir um novo chamado? \n\n"
                    "\n1 - Sim"
                    "\n\n2 - Não"
                ),
                choices=self.get_choices(),
            )
        )

    async def problem_description(self, step_context:WaterfallStepContext):
        found_choice_index = step_context.result
        if found_choice_index.index == 0:
            card_path = os.path.join(os.getcwd(), "json_file/card_create_incident.json")
            with open(card_path, "rb") as in_file:
                card_base = json.load(in_file)
            
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(card_base)],
            )

            await step_context.context.send_activity(message)
            return ComponentDialog.end_of_turn
        
        return await step_context.end_dialog()

    
    async def open_case(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(f"Ok, Aguarde enquanto abrimos o seu chamado.")
        
        briefDescription = step_context.context.activity.value['briefDescription']
        request = step_context.context.activity.value['request']

        name = step_context.context.activity.from_property.name
        user = User(name=name)
        user = user.get_user_by_name()
        topdesk = TopDesk()

        incident_cod = topdesk.create_incident(user=user,briefDescription=briefDescription, request=request, module=self.module)

        await step_context.context.send_activity(f"{name}, O seu chamado foi aberto, o numero é: {incident_cod}\n\n Logo o {self.module} vai entrar em contato.")
        
        self.accessed_card.create_register(card_id="4", username=name)
        return await step_context.end_dialog() 
    
    def get_choices(self):
        card_options = [
            Choice(value="Sim", synonyms=["sim"]),
            Choice(value="Não", synonyms=["nao"]),
        ]

        return card_options     
        
class DialogTopdeskListIncident(ComponentDialog):
    def __init__(self, dialog_id: str = None, module:str = None):
        super(DialogTopdeskListIncident, self).__init__(dialog_id or DialogTopdeskListIncident.__name__)
        
        self.topdesk = TopDesk()

        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(TextPrompt(TextPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.inform_cod_incident,
                    self.get_incident,
                ],
            )
        )
        self.module = module
        self.initial_dialog_id = dialog_id
    
    async def inform_cod_incident(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            TextPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.text("Favor informar apenas o numero do chamado!"))
        )
    
    async def get_incident(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        incident_result = step_context.result
        nome = step_context.context.activity.from_property.name
        incident = self.topdesk.get_incident_by_cod_in_topdesk(incident_result, nome)
        if incident:
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

            await step_context.context.send_activity(message)
            return await step_context.end_dialog(result=5)
        else: 
            await step_context.context.send_activity(f"Desculpe, não foi possivel localizar o chamado: {incident_result}")
            return await step_context.end_dialog()


    