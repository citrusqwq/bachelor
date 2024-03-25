"""This File contains the ResponseHandler's.
"""
# 'MeetingConsumer' and if TYPE_CHECKING to prevent circular import
# https://stackoverflow.com/a/39757388
# https://stackoverflow.com/a/65619382
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from websocket.consumer import MeetingConsumer

from django.core.cache import cache
from asgiref.sync import async_to_sync
from django.db.models.base import ModelBase

from api import authSession, deserializers, serializers
from api.models import DataAnnotation, DataSatz, DataShot, DataUserStory
from websocket.ResponseHandlerHelper import annotationDel, dataDel, dataGet, dataPush, pollClose, pollCreate, pollGet, pollVote, shotDel, shotPush


def dataResponseHandler(consumer: 'MeetingConsumer', typeStr: str,
                        model: ModelBase,
                        serializer: serializers.DataSerializer,
                        deserializer: deserializers.DataDeserializer,
                        input: dict) -> None:
    """This is a generic response handler for all DataX Models.
    This implements "push", "get" and "del"(only for DataShot).
    To response correctly this needs the model, a serializer and a deserializer.
    If no error occurs the input get's deserialized and inserted or updated in the database.
    Then a message to the meeting channel group get's send if the data was inserted or updated.
    With cmd="new" or cmd="update".
    If it's a "get" request only the sender gets a message back.
    The answer to "get" is always the date with cmd = "new".
    
    More info in README.md of api.

    Args:
        typeStr: The type of message e.g "userstory"
        model: The model
        serializer: The correct serializer from api.serializers
        deserializer: The correct deserializer from api.deserializers
        input: The complete message as dict from JSON.loads()
    """

    # validate input
    if not (isinstance(input["data"], list)):
        consumer.sendErrorMessage(typeStr, "data field is not a list/array")
        return

    # dont allow empty data except if we get a "get" command
    if ((len(input['data']) == 0)
            and not ((input['cmd'] == "get") or input['cmd'] == "getExport")):
        consumer.sendErrorMessage(typeStr, "data field is empty")
        return

    # set the meetingName of this websocket
    meetingName = consumer.scope['url_route']['kwargs']['meetingName']

    # the data needs to be inserted or updated
    if (str(input['cmd']).startswith("push")):

        # only the moderator can add/change shots
        if (model.__name__ == DataShot.__name__):
            if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                                    meetingName)):
                consumer.sendErrorMessage(
                    typeStr, "only the Moderator can add/change shots")
                return

            shotPush(consumer, typeStr, input, meetingName)
        else:

            # only the moderator can add/change annotation
            if (model.__name__ == DataAnnotation.__name__):
                if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                                        meetingName)):
                    consumer.sendErrorMessage(
                        typeStr, "only the Moderator can add/change annotation")
                    return

            dataPush(consumer, typeStr, serializer, deserializer, input,
                     meetingName)

    # a sender asked for specific data
    # only send data back to sender not all channel members
    elif ((input['cmd'] == "get") or (input['cmd'] == "getExport")):
        dataGet(consumer, typeStr, model, serializer, input, meetingName)

    elif (input['cmd'] == "del"):

        # only the moderator can delete data
        if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                                meetingName)):
            consumer.sendErrorMessage(
                typeStr, "only the Moderator can delete data")
            return

        #enable delete for annotation shot
        if (model.__name__ == DataShot.__name__):
            shotDel(consumer, typeStr, input, meetingName)

        #enable delete for annotation
        elif (model.__name__ == DataAnnotation.__name__):
            annotationDel(consumer, typeStr, input, meetingName)
        
        elif (model.__name__ == DataUserStory.__name__):
            dataDel(consumer, "userstory", DataUserStory, input, meetingName)
        
        elif (model.__name__ == DataSatz.__name__):
            dataDel(consumer, "satz", DataSatz, input, meetingName)

        else:
            consumer.sendErrorMessage(typeStr,
                                      "del is not allowed for this type")

    else:
        consumer.sendErrorMessage(typeStr,
                                  input['cmd'] + " is not a valid command")


def videoResponseHandler(consumer: 'MeetingConsumer', input: dict) -> None:
    """specific Response Handler for video messages
    """

    # set the meetingName of this websocket
    meetingName = consumer.scope['url_route']['kwargs']['meetingName']

    # only the moderator can sync the video
    if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                             meetingName)):
        consumer.sendErrorMessage(
            "video", "only the Moderator can play/pause the video")
        return

    # make sure we got any data or to much data
    if (len(input['data']) != 1):
        consumer.sendErrorMessage(
            "video", "data field is empty, or has more than one entry")
        return

    # check if commands are valid
    if (not ((input['cmd'] == "play") or (input['cmd'] == "pause") or
             (input['cmd'] == "skip") or (input['cmd'] == "cmp"))):
        consumer.sendErrorMessage("video",
                                  input['cmd'] + " is not a valid command")
        return

    # check if we got a timestamp
    if (not ("ts" in input['data'][0])):
        consumer.sendErrorMessage("video", "data needs a timestamp")
        return

    # check if we got status in data from "cmp"
    if ((input["cmd"] == "cmp") and not ("status" in input['data'][0])):
        consumer.sendErrorMessage("video",
                                  "cmp needs a status message in data")
        return

    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': "video",
                'cmd': input['cmd'],
                'data': input['data']
            }
        },
    )


def pollResponseHandler(consumer: 'MeetingConsumer', input: dict) -> None:
    """specific Response Handler for poll messages
    """

    # TODO validate input

    # set the meetingName of this websocket
    meetingName = consumer.scope['url_route']['kwargs']['meetingName']

    if (input['cmd'] == "create"):

        # only the moderator can create polls
        if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                                meetingName)):
            consumer.sendErrorMessage(
                "poll", "only the Moderator can create polls")
            return

        pollCreate(consumer, "poll", input, meetingName)

    elif (input['cmd'] == "get" or input['cmd'] == "getExport"):
        pollGet(consumer, "poll", input, meetingName)

    elif (input['cmd'] == "close"):

        # only the moderator can close polls
        if not (authSession.isModeratorInMeeting(consumer.scope['session'],
                                                meetingName)):
            consumer.sendErrorMessage(
                "poll", "only the Moderator can close polls")
            return
            
        pollClose(consumer, "poll", input, meetingName)

    elif (input['cmd'] == "vote"):
        pollVote(consumer, "poll", input, meetingName)
    else:
        consumer.sendErrorMessage("poll", input['cmd'] + " is not a valid command")

def controlResponseHandler(consumer: 'MeetingConsumer', input: dict) -> None:
    """specific Response Handler for get control messages

    This implements get for control.
    This just checks if there are any outstanding control messages.
    """

    # set the meetingName of this websocket
    meetingName = consumer.scope['url_route']['kwargs']['meetingName']

    if (input['cmd'] == "get"):

        # check if shots are still loading
        # a key in the cache is set if shots are loading
        isLoadingShots = False

        # https://docs.djangoproject.com/en/3.2/topics/cache/#django.core.caches.cache.get
        sentinel = object()
        if cache.get("meeting_" + str(meetingName) + "_loadShot", sentinel) is not sentinel:
            isLoadingShots = True
        
        # send control message for loading shots
        async_to_sync(consumer.channel_layer.group_send)(
            "meeting_" + meetingName,
            {
                'type': 'group_msg',
                'msg': {
                    'type': 'control',
                    'cmd': 'loadShot',
                    'data': isLoadingShots
                }
            },
        )

    else:
        consumer.sendErrorMessage("control", input['cmd'] + " is not a valid command")
