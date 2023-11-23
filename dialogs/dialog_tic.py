# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import PromptOptions, TextPrompt, NumberPrompt, ChoicePrompt
from botbuilder.dialogs.choices import Choice
from dialogs.dialog_topdesk import DialogTopdeskCreateIncident, DialogTopdeskListIncident

CARD_PROMPT = "cardPrompt"

class DialogTic(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(DialogTic, self).__init__(dialog_id or DialogTic.__name__)

        # Key name to store this dialogs state info in the StepContext
        self.USER_INFO = "value-userInfo"
        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(DialogTopdeskCreateIncident(DialogTopdeskCreateIncident.__name__, "TIC"))
        self.add_dialog(DialogTopdeskListIncident(DialogTopdeskListIncident.__name__, "TIC"))

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.question,
                    self.verify_question,
                    self.topdesk_call,
                ],
            )
        )

        self.initial_dialog_id = dialog_id

    async def question(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        return await step_context.prompt(
            CARD_PROMPT,
            PromptOptions(
                prompt=MessageFactory.text(
                    "Possui chamado?"
                ),
                retry_prompt=MessageFactory.text(
                    "Possui Chamado?\n\n"
                    "\n1 - Sim"
                    "\n\n2 - Não"
                ),
                choices=self.get_choices(),
            ),
        )

    async def verify_question(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        found_choice = step_context.result.index

        if found_choice == 0:
            return await step_context.begin_dialog(DialogTopdeskListIncident.__name__)
        else: 
            return await step_context.begin_dialog(DialogTopdeskCreateIncident.__name__)

    async def topdesk_call(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()
            
    def get_choices(self):
        card_options = [
            Choice(value="Sim", synonyms=["sim"]),
            Choice(value="Não", synonyms=["nao"]),
        ]

        return card_options     