# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
import jwt
from datetime import datetime, timedelta
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes
from handler.route_proative.routes import ProativeMessageUpdateIncident
from bots import DialogAndWelcomeBot

# Create the loop and Flask app
from config import settings
from dialogs import MainDialog
from handler.user import UserAuth

# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(settings.APP_ID, settings.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

route_proative_update_incident = ProativeMessageUpdateIncident(ADAPTER)

# Create MemoryStorage and state
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create Dialog and Bot
DIALOG = MainDialog(USER_STATE)
BOT = DialogAndWelcomeBot(CONVERSATION_STATE, USER_STATE, DIALOG)

# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("Foi encontrado um erro!")
    await context.send_activity(
        "Entrar em contato com a equipe de desenvolvimento para verificar o erro."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

    # Clear out state
    await CONVERSATION_STATE.delete(context)

ADAPTER.on_turn_error = on_error

async def login(request):
    
    data = await request.json()
    username = data['username']
    password = data['password']
    user_auth = UserAuth(name=username, password=password)
    user_auth.get_user()
    if user_auth.get_user():
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return web.json_response({'token': token, "expiration_time": "1800"})
    else:
        return web.json_response({'error': 'user not found'}, status=401)
    

async def auth_middleware(app, handler):

    async def middleware(request):
        if request.path in settings.IGNORED_ENDPOINTS:
            return await handler(request)
        
        token = request.headers.get('Authorization', None)
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request['user'] = payload['username']
            except jwt.ExpiredSignatureError:
                return web.json_response({'error': 'Token expirado'}, status=401)
            except jwt.DecodeError:
                return web.json_response({'error': 'Token inválido'}, status=401)
        else:
            return web.json_response({'error': 'Token ausente'}, status=401)

        return await handler(request)

    return middleware


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)

def init_func(argv):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.middlewares.append(auth_middleware)

    APP.router.add_post("/api/messages", messages)
    APP.router.add_get("/api/messages", messages)
    APP.router.add_post("/", messages)
    APP.router.add_options("/", messages)
    APP.router.add_post('/api/login', login)
    APP.router.add_get('/api/last_update_incident/{cod_incident}', route_proative_update_incident.last_update_incident_get)
    APP.router.add_patch('/api/last_update_incident/{cod_incident}', route_proative_update_incident.last_update_incident_patch)
    APP.router.add_get('/api/all_incidents', route_proative_update_incident.get_all_incidents)

    return APP

if __name__ == "__main__":

    APP = init_func(None)
    
    try:
        web.run_app(APP, host="0.0.0.0", port=settings.PORT)
    except Exception as error:
        raise error
