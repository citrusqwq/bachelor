import os
import threading
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import request, HttpResponseForbidden
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import redirect, render
from django.contrib import messages

from api import authSession, pyscenedetect
from api.forms import UserCreationFormSecret, VideoForm
from api.models import DataShot, Meeting, MeetingVideo
from ViViPlayer import settings, urls
from users.forms import CustomUserCreationForm


# Create your views here.
def registerView(request: request) -> HttpResponse:
    """Register for moderator. Split into 2 steps.
    1 Step: Check if secret is valid. If valid goto Step 2.
    2 Step: Create Account.
    Args:

    Returns:

    """
    # checkSecret is Step nr. 1.
    checkSecret = True
    # if allowedToRegister is set, we are in Step nr. 2
    if "allowedToRegister" in request.session:
        checkSecret = False

    if checkSecret:
        form = UserCreationFormSecret()
    else:
        form = CustomUserCreationForm()

    if request.method == 'POST':
        if checkSecret:
            form = UserCreationFormSecret(request.POST)
        else:
            form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            if checkSecret:
                # Step 1, set allowedToRegister for session
                request.session['allowedToRegister'] = True
                # just call this function again but this time allowedToRegister is set
                return redirect('register')
            else:
                # the session created a user, now delete the key for this session
                del request.session['allowedToRegister']
                return redirect('loginMain')

    return render(request, 'register.html', {'form': form})


def meetingList(request: request) -> HttpResponse:
    """List all active Meetings the user has created
    """
    if not (authSession.canCreateMeeting(request)):
        return HttpResponseForbidden(
            "Sie haben keinen Zugriff auf diese Seite. Versuchen Sie sich einzuloggen!")
    
    # create a list with url/name for each meeting
    meetingList = []
    for meeting in Meeting.objects.filter(active=True).filter(moderator=request.user):
        meetingList.append({
            "name": meeting.name,
            "url": request.build_absolute_uri('/' + urls.MEETING_PATH) + str(meeting.name) + "/",
        })
    
    return render(request, 'list.html', context={
        "meetingList": meetingList
    })


def meetingCreateInvite(request: request) -> HttpResponse:
    """Create meeting website after moderator is authenticated
    Args:

    Returns:

    """
    if not (authSession.canCreateMeeting(request)):
        return HttpResponseForbidden(
            "Sie können kein Meeting erstellen. Versuchen Sie sich einzuloggen!")

    return render(request, 'invite.html')


def meetingJoin(request: request, meetingName: int) -> HttpResponse:
    """Returns HttpResonse of join meeting website and redirects to meeting if valid password is given.

    Args:
        request: Request from django/user
        meetingName: This is the meeting name from the url. This is guaranteed to be an int, enforced in urls.py.

    Returns:
        HttpResonse: of the join meeting screen with meetingName as context for template.
        If meeting is not valid returns HttpResponseForbidden.
        If a password is provided check password and redirect to main meeting screen if correct.
    """

    #check if this is a valid meeting name
    notValidMeeting = Meeting.validName(meetingName)
    if notValidMeeting:
        return HttpResponseForbidden(notValidMeeting)

    if request.method == 'POST':
        #password from frontend with a POST request

        #check password
        if request.POST.get('password') == Meeting.objects.get(name=meetingName).password_cleartext:

            #The user provided the correct password and is now allowed to join the meeting
            try:
                authSession.addToMeeting(request, meetingName)
            except:
                #TODO notify frontend
                return HttpResponseServerError()

            #we redirect to meeting e.g. /meeting/1234/join to /meeting/1234
            #the meeting view should now allow access to the meeting since the request is allowed in the meeting
            return redirect("./..")
        else:
            messages.error(request, "Falsches Meeting Passwort")
            return render(request, 'join.html')

    else:
        #html of the join meeting website

        #TODO Session: comment out since it returns allways true for now
        #redirect to meeting if this request is already allowed in meeting
        if (authSession.authenticatedInMeeting(request.session, request.user, meetingName)):
            return redirect("./..")

        return render(request, 'join.html', {"meetingName": meetingName})


def meetingIndex(request: request, meetingName: int) -> HttpResponse:
    """Returns HttpResponse with the main meeting website

    Args:
        request: Request from django/user
        meetingName: This is the meeting name from the url. This is guaranteed to be an int, enforced in urls.py.

    Returns:
        HttpResonse: of the meeting with meetingName as context for template.
        If meeting is not valid returns HttpResponseForbidden.
    """

    #check if this is a valid meeting name
    notValidMeeting = Meeting.validName(meetingName)
    if notValidMeeting:
        return HttpResponseForbidden(notValidMeeting)

    #check if this request is allowed in the meeting
    if not (authSession.authenticatedInMeeting(request.session, request.user, meetingName)):
        return render(request, 'error/meetingDenied.html')

    # get old video, if there is one
    videoUrl = Meeting.objects.get(name=meetingName).video
    videoUrlBase = None

    # get url plus Media directory for frontend
    if videoUrl:
        videoUrlBase = settings.MEDIA_URL + str(Meeting.objects.get(name=meetingName).video)

    # Video upload
    form = VideoForm(request.POST or None, request.FILES or None)
    # a valid video was uploaded from Moderator
    #   - delte old video
    #   - update to new video
    #   - make sure we dont already have a thread running that is detecting shots
    #   - delete old shots
    #   - add new shots
    #   - update videoUrlBase for frontend
    if (form.is_valid() and authSession.isModeratorInMeeting(request.session, meetingName)):
        newVideo = form.save()

        # delete previous video
        oldVideoID = Meeting.objects.values_list('video_id', flat=True).get(name=meetingName)
        if oldVideoID:
            MeetingVideo.objects.filter(id=oldVideoID).delete()

        # update database with new video
        Meeting.objects.filter(name=meetingName).update(video=newVideo)

        # delete old shots
        if DataShot.objects.filter(meeting_id__name=meetingName).exists():
            DataShot.objects.filter(meeting_id__name=meetingName).delete()

        # set videoUrlBase since the url has changed with the new video
        videoUrlBase = settings.MEDIA_URL + str(newVideo)

        # detect shots
        # videoUrlBase[1:] since videoUrlBase is a relative path(starts with /)
        # uses daemon thread, since we would block the return of meeting.html.
        threading.Thread(target=pyscenedetect.findInsertShots,
                                        args=(meetingName, os.path.join(settings.BASE_DIR,videoUrlBase[1:])),
                                        daemon=True,
                                        name="ShotsThread_" + str(meetingName)).start()

        # video upload was successful
        # notify all users
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "meeting_" + str(meetingName), 
            {
                'type': 'group_msg',
                'msg': {
                    'type': "control",
                    'cmd': 'reload',
                    'data': []
                }
            },
        )

        # don't need to reponse with any data since the page will reload
        return HttpResponse("")

    return render(request, 'meeting.html', {
        "meetingName": meetingName,
        'screenshot_path': Meeting.objects.get(name=meetingName).screenshot_path,
        'form': form,
        'video': videoUrlBase,
        'isMod': authSession.isModeratorInMeeting(request.session, meetingName)
    })


def meetingEnd(request: request, meetingName: int) -> HttpResponse:
    """This ends the meeting. Only the moderator is allowed to end the meeting.
    This also notifies all other users.
    """

    if request.POST:

        #check if this request is allowed in the meeting as Moderator
        if not (authSession.isModeratorInMeeting(request.session, meetingName)):
            return HttpResponseForbidden("Sie dürfen das Meeting nicht beenden!")

        # delete moderator cookie for meeting
        request.session.flush()

        # send end Meeting to all Members via the group channel.
        # more in method end in consumer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "meeting_" + str(meetingName), 
            {
                'type': 'end',
            }
        )

        # set Meeting to inactive
        Meeting.objects.filter(name=meetingName).update(active=False)

        return HttpResponseRedirect("end")
    
    return render(request, "end.html" , {"meetingName": meetingName})


def meetingLeave(request: request, meetingName: int) -> HttpResponse:
    """This allows a user to leave a meeting.
    """

    if request.POST:

        # delete session
        request.session.flush()
    
        return HttpResponseRedirect("leave")
    
    return render(request, "leave.html" , {"meetingName": meetingName})