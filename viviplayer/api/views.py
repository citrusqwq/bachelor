import os
import smtplib

from django.http.response import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError, JsonResponse
from rest_framework import request, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from ViViPlayer.settings import BASE_DIR
from api.export import ExportODT, ExportCSV
from api.models import Meeting, MeetingVideo
from api import authSession, mail
from ViViPlayer import urls
from api.screenshots import screenshots


# Create your views here.
class MeetingApiViewSet(viewsets.ViewSet):
    """Viewset of the meeting api.

    ./create/               creates a meeting
    ./<pk>/mail/ #TODO      add mail addresses to meeting
    
    """
    @action(detail=False,
            methods=['get'],
            url_path='create',
            permission_classes=[authSession.CanCreateMeeting])
    def createMeeting(self, request: request) -> Response:
        """Creates a new meeting with name and password from http GET

        Args:
            request: Request from django/user

        Returns:
            Response: In json format with name, password, url and a status message.
        """

        #creates a new meeting in database
        try:
            newMeeting = Meeting.objects.create(
                moderator=request.user
            )
        except Exception as e:
            #TODO notify frontend that creating of a new meeting failed
            return HttpResponseServerError(str(e))

        #add session to meeting as moderator
        try:
            authSession.addToMeeting(request, newMeeting.name, asMod=True)
        except Exception as e:
            #TODO could not add moderator to meeting so we schould delete the meeting, notify frontend
            return HttpResponseServerError(str(e))

        return Response({
            'status': 'meeting ' + str(newMeeting.name) + ' created',
            'url': ('/' + urls.MEETING_PATH) + str(newMeeting.name),  # generate relative url to meeting
            'name': newMeeting.name,
            'password': newMeeting.password_cleartext
        })

    @action(detail=True,
            methods=['post'],
            url_path='mail',
            name='Add Emails to a meeting')
    def sendMail(self, request: request, pk=None) ->HttpResponse:
        """Send invite mails.

        Args:
            request: Request from django/user

        Returns:

        """

        #check if this is a valid meeting name
        notValidMeeting = Meeting.validName(pk)
        if notValidMeeting:
            return JsonResponse({
                "msg": "Meeting not active or valid."
            }, status=403)

        #check if this request is moderator in the meeting
        if not (authSession.isModeratorInMeeting(request.session, pk)):
            return JsonResponse({
                "msg": "Youre not allowed in the meeting"
            }, status=403)

        # only send mail if got mails
        if (('emaillist' in request.POST) and (len(request.POST['emaillist']) != 0)):
            
            # build url to join meeting
            # set https or http based on ENV PROXY_HTTPS
            # this is not set if startet with python runserver
            # but docker-compose sets PROXY_HTTPS to 1
            httpsEnabled = bool(int(os.environ.get("PROXY_HTTPS", default=0)))

            meetingURL = "https://" if httpsEnabled else "http://"
            meetingURL += request.get_host()
            meetingURL += '/' + urls.MEETING_PATH + str(pk + "/join/")
            # send mail
            try:
                mail.sender(pk, 
                    meetingURL,
                    Meeting.objects.get(name=pk).password_cleartext,
                    request.POST['emaillist'])
            except Exception as e:
                msg = "Fehler beim Senden der Mails."
                # returns SMTPServerDisconnected if no mail was set in ENV file(settings.py)
                if isinstance(e, smtplib.SMTPServerDisconnected):
                    msg = "Es wurde keine Email konfiguriert oder fehlerhaft konfiguriert da keine Verbindung zum Email Server aufgebaut werden konnte."

                return JsonResponse({
                    "msg": msg
                }, status=400)

        return JsonResponse({
            "msg": "Mails wurden versand."
        })

    @action(detail=True,
            methods=['get'],
            url_path='info',
            name='Get Meeting password')
    def getMeetingPassword(self, request: request, pk=None) -> HttpResponse:

        #check if this is a valid meeting name
        notValidMeeting = Meeting.validName(pk)
        if notValidMeeting:
            return JsonResponse({
                "msg": "Meeting not active or valid."
            }, status=403)

        #check if this request is moderator in the meeting
        if not (authSession.isModeratorInMeeting(request.session, pk)):
            return JsonResponse({
                "msg": "Youre not allowed in the meeting"
            }, status=403)

        meeting = Meeting.objects.get(name=pk)

        return JsonResponse({
            'password': meeting.password_cleartext
        })

    @action(detail=True,
            methods=['get'],
            url_path='export',
            name="get export data")
    def exportMeeting(self, request: request, pk=None) -> HttpResponse:

        #check if this is a valid meeting name
        notValidMeeting = Meeting.validName(pk)
        if notValidMeeting:
            return HttpResponseForbidden("Meeting not active or valid.")

        #check if this request is moderator in the meeting
        if not (authSession.isModeratorInMeeting(request.session, pk)):
            return HttpResponseForbidden("Youre not allowed in the meeting")

        if (self.request.query_params.get('file') == "odt"):
            # ruf in export.py die Funktion
            result = ExportODT(pk)
            result.seek(0)
            return FileResponse(result, as_attachment=True, filename= 'Meeting' +str(pk) + '.odt')

        elif (self.request.query_params.get('file') == "csv"):
            result = ExportCSV(pk)
            result.seek(0)
            return FileResponse(result, as_attachment=True, filename= 'Meeting' +str(pk) + '.zip')

        else:
            return HttpResponseBadRequest("wrong/missing file type")

    @action(detail=True,
            methods=['post'],
            url_path='screenshot',
            name='change screenshot of shot')
    def changeScreenshot(self, request: request, pk=None) -> HttpResponse:

        #check if this is a valid meeting name
        notValidMeeting = Meeting.validName(pk)
        if notValidMeeting:
            return JsonResponse({
                "msg": "Meeting not active or valid."
            }, status=403)

        #check if this request is moderator in the meeting
        if not (authSession.isModeratorInMeeting(request.session, pk)):
            return JsonResponse({
                "msg": "Youre not allowed in the meeting"
            }, status=403)

        if "time" in request.data and "shot_id" in request.data:

            if not (isinstance(request.data.get('time'), (float, int)) and isinstance(request.data.get('shot_id'), int)):
                return JsonResponse({
                "msg": "time needs to be a float and shot_id an int"
                }, status=400)

            screenshots(
                MeetingVideo.objects.get(meeting__name=pk).videofile.path,
                os.path.join(BASE_DIR, Meeting.objects.get(name=pk).screenshot_path[1:]),
                (request.data.get('time'), request.data.get('shot_id'))
            )

            return JsonResponse({
                "msg": "screenshot changed"
            })
        
        else:

            return JsonResponse({
                "msg": "time and/or shotID missing"
            }, status=400)