# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import ast
import os
import json

from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import PromptOptions, TextPrompt, ChoicePrompt, NumberPrompt

from botbuilder.schema import Attachment, ActivityTypes, Activity, CardAction, ActionTypes, HeroCard
from data_models.models import CardModel

from dialogs.dialog_topdesk import DialogTopdeskCreateIncident
from handler.card import Card, AccessedCard


CARD_PROMPT = "cardPrompt"

class DialogRh(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(DialogRh, self).__init__(dialog_id or DialogRh.__name__)

        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(DialogTopdeskCreateIncident(DialogTopdeskCreateIncident.__name__, "RH"))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.question,
                    self.response_question
                ],
            )
        )
        self.card = Card()
        self.accessed_card = AccessedCard()
        self.initial_dialog_id = dialog_id

    async def question(self, step_context: WaterfallStepContext):
        choices = self.card.get_tittle_card_by_team(team="RH")
        choices.append("O que procuro não esta aqui")
        choices.append("Voltar")

        card_actions = []
        for choice in choices:
            card_action = CardAction(
                type=ActionTypes.im_back,
                title=choice,
                value=choice
            )
            card_actions.append(card_action)

        card = HeroCard(
            text="Qual a sua duvida?",
            buttons=card_actions
        )

        return await step_context.prompt(
            TextPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.attachment(CardFactory.hero_card(card)))
        )
        

    async def response_question(self, step_context: WaterfallStepContext) -> DialogTurnResult: 
        found_choice = step_context.result
        name = step_context.context.activity.from_property.name

        find_card = self.card.get_card_by_tittle(tittle=found_choice)

        if find_card:

            message = Activity(
                type=ActivityTypes.message,
                attachments=[self.create_card_data(card_data=find_card)],
            )
            await step_context.context.send_activity(message)
            self.accessed_card.create_register(card_id=find_card.id, username=name)
        elif found_choice == "O que procuro não esta aqui" or found_choice.lower().find("chamado") != -1:
            return await step_context.begin_dialog(DialogTopdeskCreateIncident.__name__)
        else:
            return await step_context.end_dialog(result=4)
        
        return await step_context.end_dialog()
            
    def create_card_data(self, card_data:CardModel) -> Attachment:

        card_path = os.path.join(os.getcwd(), "json_file/base.json")
        with open(card_path, "rb") as in_file:
            card_base = json.load(in_file)

        card_base['body'][0]['text'] = card_data.tittle
        description = ast.literal_eval(card_data.description)
        for data in description['description']:
            card_base['body'].append({'type': 'TextBlock', 'text': data['description'], 'wrap': True})

        return CardFactory.adaptive_card(card_base)
    