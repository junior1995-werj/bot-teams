# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.core import UserState, CardFactory
from dialogs.init_dialog import InitDialog
from dialogs.top_level_dialog import TopLevelDialog
from botbuilder.schema import ActivityTypes, Activity


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.user_state = user_state
        self.add_dialog(InitDialog(InitDialog.__name__))
        self.add_dialog(TopLevelDialog(TopLevelDialog.__name__))
        
        self.add_dialog(
            WaterfallDialog("WFDialog", [self.initial_step,self.options_step, self.final_step])
        )

        self.initial_dialog_id = "WFDialog"


    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        #await step_context.begin_dialog(InitDialog.__name__)
        return await step_context.begin_dialog(InitDialog.__name__)

    async def options_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        #await step_context.begin_dialog(InitDialog.__name__)
        return await step_context.begin_dialog(TopLevelDialog.__name__)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        card_path = os.path.join(os.getcwd(), "json_file/start_card.json")
        with open(card_path, "rb") as in_file:
            card_base = json.load(in_file)
        
        message = Activity(
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(card_base)],
        )

        await step_context.context.send_activity(message)
        return await step_context.end_dialog()
