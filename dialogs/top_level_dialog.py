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

from dialogs.dialog_tic import DialogTic
from dialogs.dialog_rh import DialogRh
from dialogs.dialog_topdesk import DialogTopdeskListIncident

CARD_PROMPT = "cardPrompt"

class TopLevelDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(TopLevelDialog, self).__init__(dialog_id or TopLevelDialog.__name__)

        # Key name to store this dialogs state info in the StepContext
        self.add_dialog(ChoicePrompt(CARD_PROMPT))

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(DialogTic(DialogTic.__name__))
        self.add_dialog(DialogRh(DialogRh.__name__))
        self.add_dialog(DialogTopdeskListIncident(DialogTopdeskListIncident.__name__))

        self.add_dialog(
            WaterfallDialog(
                dialog_id,
                [   
                    self.question_type,
                    self.selected_type,
                    self.new_question,
                    self.end_step,
                ],
            )
        )

        self.initial_dialog_id = dialog_id

    async def question_type(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        1. Prompts the user if the user is not in the middle of a dialog.
        2. Re-prompts the user when an invalid input is received.
        """

        # Prompt the user with the configured PromptOptions.
        name = step_context.context.activity.from_property.name
        return await step_context.prompt(
            CARD_PROMPT,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"{name}, Como eu poderia te ajudar?"
                ),
                retry_prompt=MessageFactory.text(
                    "Favor escolher uma das opções abaixo\n\n"
                    "\n1 - RH"
                    "\n\n2 - TI Interna"
                    "\n\n3 - Consultar Chamados"
                ),
                choices=self.get_choices(),
            ),
        )

    async def selected_type(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        found_choice = step_context.result.value
        if found_choice == "RH":
            return await step_context.begin_dialog(DialogRh.__name__)
        elif found_choice == "TI Interna":
            return await step_context.begin_dialog(DialogTic.__name__)
        elif found_choice == "Consultar chamado":
            return await step_context.begin_dialog(DialogTopdeskListIncident.__name__)

    async def new_question(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        if step_context.result == 4:
            return await step_context.begin_dialog(self.initial_dialog_id)
        
        nome = step_context.context.activity.from_property.name
        return await step_context.prompt(
            CARD_PROMPT,
            PromptOptions(
                prompt=MessageFactory.text(
                    f"{nome}, posso te ajudar com mais algo?"
                ),
                retry_prompt=MessageFactory.text(
                    "Favor escolher uma das opções abaixo\n\n"
                    "\nSim"
                    "\n\nNão"
                ),
                choices=self.get_yes_or_not(),
            ),
        )

    async def end_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        found_choice = step_context.result.value
        if found_choice == "Sim":
            return await step_context.begin_dialog(self.initial_dialog_id)
            
        else:  
            nome = step_context.context.activity.from_property.name
            await step_context.context.send_activity(f"Ok {nome}, Volte sempre!")
            return await step_context.end_dialog()

    def get_choices(self):
        card_options = [
            Choice(value="RH", synonyms=["rh"]),
            Choice(value="TI Interna", synonyms=["TI Interna"]),
            Choice(value="Consultar chamado", synonyms=["consultar_chamado"]),
        ]

        return card_options     
    
    def get_yes_or_not(self):
        card_options = [
            Choice(value="Sim", synonyms=["sim"]),
            Choice(value="Não", synonyms=["nao"]),
        ]

        return card_options