import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from api import authSession, deserializers, serializers
from api.models import DataAnnotation, DataSatz, DataShot, DataUserStory, Meeting
from websocket.ResponseHandler import controlResponseHandler, dataResponseHandler, pollResponseHandler, videoResponseHandler


class MeetingConsumer(WebsocketConsumer):
    def connect(self):
        """
        Accept incoming Websocket request and add current connection to the meeting group.
        self.channel_name -> Is automaticly generate and unique name for current Websocket connection.
        """

        # check if this is a valid meeting name
        notValidMeeting = Meeting.validName(
            self.scope['url_route']['kwargs']['meetingName'])
        if notValidMeeting:
            return self.close()

        # check if session is authenticated
        if not (authSession.authenticatedInMeeting(
                self.scope['session'],
                self.scope["user"],
                self.scope['url_route']['kwargs']['meetingName'])):
            self.close()
            return None

        # everything ok, add this session/websocket to the channel group of this meeting and accept websocket connection
        async_to_sync(self.channel_layer.group_add)(
            "meeting_" + str(self.scope['url_route']['kwargs']['meetingName']),
            self.channel_name)

        # add moderator to own channgel group to enable moderator only messages
        if (authSession.isModeratorInMeeting(
            self.scope['session'],
            self.scope['url_route']['kwargs']['meetingName'])):

            async_to_sync(self.channel_layer.group_add)(
                "meeting_" + str(self.scope['url_route']['kwargs']['meetingName'] + "_mod"),
                self.channel_name)
        
        self.accept()

    def disconnect(self, close_code: int):
        """Websocket was closed. Remove current Websocket from channel group.
        """
        # discard general channel group
        async_to_sync(self.channel_layer.group_discard)(
            "meeting_" + str(self.scope['url_route']['kwargs']['meetingName']),
            self.channel_name)

        # discard moderator only channel group
        async_to_sync(self.channel_layer.group_discard)(
            "meeting_" + str(self.scope['url_route']['kwargs']['meetingName'] + "_mod"),
            self.channel_name)

    def receive(self, text_data: str) -> None:
        """Handle messages from frontend.

        Args:
            msg: Recieved message as string from frontend. This is the data the fronted sends through the websocket to us(backend).
        """

        # string from frontend, needs to be JSON
        try:
            dataJSON = json.loads(text_data)
            print("Websocket RECV: ", dataJSON)  #DEBUG message
        except:
            self.sendErrorMessage("unknown", "not valid JSON")
            return

        # make sure we got all data fields
        if not ("type" in dataJSON) or not ("cmd" in dataJSON) or not (
                "data" in dataJSON):
            self.sendErrorMessage("unknown",
                                  "invalid format need type, cmd and data")

        # choose correct response handler with given Model, serializer and deserializer
        if (dataJSON['type'] == "shot"):
            dataResponseHandler(self, "shot", DataShot,
                                serializers.DataShotSerializer,
                                deserializers.DataShotDeserializer, dataJSON)

        elif (dataJSON['type'] == "userstory"):
            dataResponseHandler(self, "userstory", DataUserStory,
                                serializers.DataUserStorySerializer,
                                deserializers.DataUserStoryDeserializer,
                                dataJSON)

        elif (dataJSON['type'] == "satz"):
            dataResponseHandler(self, "satz", DataSatz,
                                serializers.DataSatzSerializer,
                                deserializers.DataSatzDeserializer, dataJSON)

        elif (dataJSON['type'] == "annotation"):
            dataResponseHandler(self, "annotation", DataAnnotation,
                                serializers.DataAnnotationSerializer,
                                deserializers.DataAnnotationDeserializer, dataJSON)

        elif (dataJSON['type'] == "video"):
            videoResponseHandler(self, dataJSON)

        elif (dataJSON['type'] == "poll"):
            pollResponseHandler(self, dataJSON)

        elif (dataJSON['type'] == "control"):
            controlResponseHandler(self, dataJSON)

        else:
            self.sendErrorMessage("unknown",
                                  dataJSON['type'] + " is not a valid type")

    def group_msg(self, event: dict) -> None:
        """Handle the message we recive on the channel group.
        Send the mesage from the channel group back to the fronted over the websocket.

        Args:
            event: should be JSON, the message for the frontend MUST BE in msg list
        """

        print(self.scope['client'], "Channel Group RECV: ", event) #DEBUG message
        # send message from channel group to recivers
        self.send(text_data=json.dumps(event["msg"]))

    def end(self, event: dict) -> None:
        """Handle the message we recive on the channel group.
        Send end the Meeting for everyone.
        """

        self.send(text_data=json.dumps({
            "type": "control",
            "cmd": "end",
            "data": []
        }))

        # remove cookie for everyone else
        self.scope['session'].flush()

        # end websocket session, and remove websocket from channel_layer
        # TODO investigate if we have to call disconnect
        self.disconnect(0)
        self.close()

    def refresh(self, event: dict) -> None:
        """Handle the message we recive on the channel group.
        Send refresh message to everyone.
        """
        self.send(text_data=json.dumps({
            "type": "control",
            "cmd": "refresh",
            "data": []
        }))

    def sendErrorMessage(self, typeStr: str, message: str) -> None:
        """This just sends an error message over the websocket to the frontend.
        """
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': 'error',
                    'data': [message]
                }
            },
        )
