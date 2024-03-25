"""This file contains the logic to authenticate a session for a meeting.
"""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.permissions import BasePermission
from rest_framework import request, viewsets

from api.models import Meeting


class CanCreateMeeting(BasePermission):
    """For Rest API PermissionClass calls canCreateMeeting()
    """
    def has_permission(self, request: request, view: viewsets.ViewSet) -> bool:
        return canCreateMeeting(request)


def canCreateMeeting(request: request) -> bool:
    """This checks if request can create a meeting

    Args:
        request:
    Returns:
        bool: If request is allowed return true
    """
    #If a request has a django account
    return request.user.is_authenticated


def addToMeeting(request: request,
                 meetingName: int,
                 asMod: bool = False) -> None:
    """Enables the request to enter the meeting by placing a cookie and saving the the session in the database

    Args:
        request: The request the session should be enabled
        meetingName:
        asMod: If this request should be the moderator for the meeting. Defaults to False (request is user).

    Returns:
        None: If the session was succesfully added

    Raises:
        Exception: If the session can't be enabled for the meeting
    """
    # https://docs.djangoproject.com/en/3.2/topics/http/sessions/#when-sessions-are-saved

    # uses id not meeting name
    # to make sure if a meeting is recreated with the same name we don't authenticate them in the new meeting
    meeting_id = str(Meeting.objects.get(name=meetingName).id)

    # add/auth meeting to session
    addToMeetingSession(request.session, meeting_id, asMod)
    

def addToMeetingSession(session: SessionStore, meeting_id: str, asMod: bool = False) -> None:
    """
    """

    # every meeting gets a meeting_x dict with two entrys allowed and isMod
    session["meeting_" + meeting_id] = {}
    session["meeting_" + meeting_id]["allowed"] = True
    if (asMod):
        session["meeting_" + meeting_id]["isMod"] = True

        # for mods enable session for 24 hours
        # 86.400 = 24 * 60 * 60
        session.set_expiry(86400)
    else:
        # for users only enable session until browser is clossed
        session.set_expiry(0)

    # since meeting_x is a dict signal django that the session was changed
    session.modified = True

    return None


def authenticatedInMeeting(session: SessionStore, user: settings.AUTH_USER_MODEL, meetingName: int) -> bool:
    """Checks if request.session is allowed in the given meeting

    Args:
        session: SessionStore from the request !!! request.session and not just request
        meetingName: This is the meeting name from the url. This is guaranteed to be an int, enforced in urls.py.

    Returns:
        bool: True if request is authenticated in meeting.

    """
    # uses id not meeting name
    # to make sure if a meeting is recreated with the same name we don't authenticate them in the new meeting
    meeting_id = str(Meeting.objects.get(name=meetingName).id)

    try:
        # returns true if authenticated in meeting
        return session["meeting_" + meeting_id]["allowed"]
    except Exception:
        pass

    # no active session was found for user
    # if the user is not an AnonymousUser this is a potential moderator since the session is logged in
    # allow access and add meeting to session if the user is the moderator of a meeting
    if not (isinstance(user, AnonymousUser)):
        if (Meeting.objects.get(name=meetingName).moderator == user):
            addToMeetingSession(session, meeting_id, True)
            return True

    return False

def isModeratorInMeeting(session: SessionStore, meetingName: int) -> bool:
    """Checks if request.session is Moderator in the given Meeting

    Args:
        session: SessionStore from the request !!! request.session and not just request
        meetingName: 

    Returns:
        bool: True if session is moderator in meeting.
    """
    # uses id not meeting name
    # to make sure if a meeting is recreated with the same name we don't authenticate them in the new meeting
    meeting_id = str(Meeting.objects.get(name=meetingName).id)

    try:
        # returns true if authenticated in meeting and moderator
        return session["meeting_" + meeting_id]["isMod"] and session[
            "meeting_" + meeting_id]["allowed"]
    except Exception:
        return False
