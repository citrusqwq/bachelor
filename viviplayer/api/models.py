import os
import shutil
import random
import uuid
from datetime import datetime, timedelta    
from typing import Any, Dict, Optional, Tuple

from django.contrib.auth import hashers
from django.contrib.auth.base_user import BaseUserManager
from django.utils.timezone import now
from django.db import models
from django.db.models import Max
from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete 
from django.dispatch import receiver
from django.conf import settings

from ViViPlayer.settings import BASE_DIR, MEDIA_URL

def get_file_path(instance, filename) -> str:
    """ Generate unique name
    https://stackoverflow.com/a/2677474
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('video', filename)

def get_random_screenshot_path() -> str:
    """ Generate unique path to save screenshots to
    """
    screenshot_path = os.path.join(MEDIA_URL, "screenshot")
    return os.path.join(screenshot_path, str(uuid.uuid4())) + "/"

def generate_random_password(length: int=10) -> str:
    return BaseUserManager().make_random_password(
            length=length,
            allowed_chars='abcdefghjkmnpqrstuvwxyz'
            'ABCDEFGHJKLMNPQRSTUVWXYZ'
            '23456789'
            '!$%&?*+#-_')

def generate_valid_until() -> datetime:
    """Generate a datetime with x days/hours in the future
    """
    return now() + timedelta(days=1)


class UserCreationSecret(models.Model):
    password_hash = models.CharField(default=generate_random_password, max_length=200) # default generate cleartext pwd -> hash in save()
    valid_until = models.DateTimeField(default=generate_valid_until)

    def __str__(self):
        return "Secret valid until " + str(self.valid_until)

    def save(self, *args, **kwargs):
        """Hash the cleartext password generated from generate_random_password
        """
        self.password_hash = hashers.make_password(password=self.password_hash)
        super().save(*args, **kwargs)


class MeetingVideo(models.Model):
    videofile = models.FileField(upload_to=get_file_path)

    def __str__(self):
        return str(self.videofile)


class Meeting(models.Model):
    name = models.PositiveIntegerField(unique=True)
    password_cleartext = models.CharField(max_length=200, default=generate_random_password)
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    video = models.ForeignKey(
        MeetingVideo,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    screenshot_path = models.CharField(max_length=100, default=get_random_screenshot_path)

    def __str__(self) -> str:
        return "Meeting " + str(self.name)

    def save(self, *args, **kwargs):
        """Custom save method to generate a unique name if no name is given
        
        Raises:
            TODO throw exception if no meeting name is available
        """

        #if we create a Meeting in the admin dashboard we might already have a name
        if (self.name == None):

            #4digit meeting name
            #we dont need a strong random generator for the meeting name
            newMeetingName = random.randint(1000, 9999)

            #if we generated a Name that already exists just generate a new one
            #TODO throw exception if no meeting name is available
            #TODO if a meeting is not active and x days old overwrite
            while (Meeting.objects.filter(name=newMeetingName).exists()):
                newMeetingName = random.randint(1000, 9999)

            #set name to the newly generate meeting name
            self.name = newMeetingName

        # create screenshot folder
        # remove leading / with [1:] to get complete path and not relative path
        if not os.path.exists(os.path.join(BASE_DIR, self.screenshot_path[1:])):
            os.makedirs(os.path.join(BASE_DIR, self.screenshot_path[1:]))

        super().save(*args, **kwargs)

    def validName(meetingName: int) -> Optional[str]:
        """Check if meeting name is valid

        args:
            meetingName: the meeting name to check
        
        Return:
            str: Returns an error message as string. When the Meeting does not exist or is not ready. 
            None: If everything is ok.
        """

        if not (Meeting.objects.filter(name=meetingName).exists()):
            return "Meeting does not exist"

        if not (Meeting.objects.get(name=meetingName).active):
            #the boolean field active is set to false
            return "Meeting not active"

        #everthing valid
        return None


@receiver(post_delete, sender=Meeting)
def handle_delete_Meeting(sender, instance, **kwargs):

    # delete screenshot folder
    if os.path.exists(os.path.join(BASE_DIR, instance.screenshot_path[1:])):
        try:
            shutil.rmtree(os.path.join(BASE_DIR, instance.screenshot_path[1:]))
        except:
            # Screenshots already deleted, silently ignore
            pass
    
    # delete meeting video
    try:
        MeetingVideo.objects.filter(id=instance.video.id).delete()
    except:
        # Video already deleted, silently ignore
        pass


class DataShot(models.Model):
    meeting_id = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
    )
    per_meeting_id = models.PositiveIntegerField()
    description = models.CharField(
        max_length=1650
    )  #ein Wort im Schnitt 11 Buchstaben -> ein Satz im Schnitt 15 Wörter -> 10 Sätze: 11*15*10=1650
    frm = models.FloatField()
    to = models.FloatField()

    class Meta:
        unique_together = (("meeting_id", "per_meeting_id"), )
        ordering = ["meeting_id", "per_meeting_id"]

    def __str__(self) -> str:
        return "ShotID: " + str(self.per_meeting_id)

    def update_or_create(self) -> Tuple[Any, bool]:
        """ Since meeting_id and per_meeting_id are unique we can use the django method update_or_create
        with those two fields.

        https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update-or-create
        """
        return DataShot.objects.update_or_create(
            meeting_id=self.meeting_id,
            per_meeting_id=self.per_meeting_id,
            defaults={
                'description': self.description,
                'frm': self.frm,
                'to': self.to
            })


class DataUserStory(models.Model):
    meeting_id = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
    )
    per_meeting_id = models.PositiveIntegerField()
    shot_id = models.ForeignKey(DataShot, on_delete=models.CASCADE)
    role = models.CharField(max_length=30)
    capability = models.CharField(max_length=3300)  #20 Sätze: 11*15*10=3300
    benefit = models.CharField(max_length=3300)  #20 Sätze: 11*15*10=3300

    class Meta:
        unique_together = (("meeting_id", "per_meeting_id"), )
        ordering = ["meeting_id", "per_meeting_id"]

    def __str__(self) -> str:
        return "UserStoryID: " + str(self.per_meeting_id)

    def update_or_create(self) -> Tuple[Any, bool]:
        """ Since meeting_id and per_meeting_id are unique we can use the django method update_or_create
        with those two fields.

        https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update-or-create
        """
        return DataUserStory.objects.update_or_create(
            meeting_id=self.meeting_id,
            per_meeting_id=self.per_meeting_id,
            defaults={
                'shot_id': self.shot_id,
                'role': self.role,
                'capability': self.capability,
                'benefit': self.benefit
            })


class DataSatz(models.Model):
    meeting_id = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
    )
    per_meeting_id = models.PositiveIntegerField()
    shot_id = models.ForeignKey(DataShot, on_delete=models.CASCADE)
    satz = models.CharField(max_length=3300)  #20 Sätze: 11*15*10=3300

    class Meta:
        unique_together = (("meeting_id", "per_meeting_id"), )
        ordering = ["meeting_id", "per_meeting_id"]

    def __str__(self) -> str:
        return "SatzID: " + str(self.per_meeting_id)

    def update_or_create(self) -> Tuple[Any, bool]:
        """ Since meeting_id and per_meeting_id are unique we can use the django method update_or_create
        with those two fields.

        https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update-or-create
        """
        return DataSatz.objects.update_or_create(
            meeting_id=self.meeting_id,
            per_meeting_id=self.per_meeting_id,
            defaults={
                'shot_id': self.shot_id,
                'satz': self.satz,
            })


class DataPoll(models.Model):
    meeting_id = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
    )
    per_meeting_id = models.PositiveIntegerField()
    shot_id = models.ForeignKey(DataShot, on_delete=models.CASCADE)
    response = models.SmallIntegerField(default=0) #  0 singel choice, 1 muliple choice
    question = models.CharField(max_length=1000)
    options = models.JSONField(default=list)
    active = models.BooleanField(default=True)
    public = models.BooleanField(default=True)

    class Meta:
        unique_together = (("meeting_id", "per_meeting_id"), )
        ordering = ["meeting_id", "per_meeting_id"]

    def __str__(self) -> str:
        return "PollID: " + str(self.per_meeting_id)

    def update_or_create(self) -> Tuple[Any, bool]:
        """ Since meeting_id and per_meeting_id are unique we can use the django method update_or_create
        with those two fields.

        https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update-or-create
        """
        return DataPoll.objects.update_or_create(
            meeting_id=self.meeting_id,
            per_meeting_id=self.per_meeting_id,
            defaults={
                'shot_id': self.shot_id,
                'response': self.response,
                'question': self.question,
                'active': self.active,
                'options': self.options
            })  


class DataPollAnswer(models.Model):
    poll_id = models.ForeignKey(
        DataPoll,
        on_delete=models.CASCADE,
    )
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, blank=True, null=True)
    option_id = models.PositiveIntegerField()

    def __str__(self) -> str:
        return "Vote with option_id " + str(self.option_id)


class DataAnnotation(models.Model):
    meeting_id = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
    )
    per_meeting_id = models.PositiveIntegerField()
    shot_id = models.ForeignKey(DataShot, on_delete=models.CASCADE)
    pos_x = models.PositiveIntegerField()
    pos_y = models.PositiveBigIntegerField()
    titel = models.CharField(max_length=1000)
    text_type = models.SmallIntegerField(default=0) # 0 text, 1 url/link
    text = models.CharField(max_length=1000)

    class Meta:
        unique_together = (("meeting_id", "per_meeting_id"), )
        ordering = ["meeting_id", "per_meeting_id"]

    def __str__(self) -> str:
        return "AnnotationID: " + str(self.per_meeting_id)

    def update_or_create(self) -> Tuple[Any, bool]:
        """ Since meeting_id and per_meeting_id are unique we can use the django method update_or_create
        with those two fields.

        https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update-or-create
        """
        return DataAnnotation.objects.update_or_create(
            meeting_id=self.meeting_id,
            per_meeting_id=self.per_meeting_id,
            defaults={
                'shot_id': self.shot_id,
                'pos_x': self.pos_x,
                'pos_y': self.pos_y,
                'titel': self.titel,
                'text_type': self.text_type,
                'text': self.text,
            })


def getNextPerMeetingId(model: models.Model, meetingName: int) -> int:
    """This returns the the next per_meeting_id from model and meeting.

    Args:
        model:
        meetingName:

    Returns:
        int: Returns the next per_meeting_id if the table is empty return 0
            This uses the MAX method of sql/objects. This means no number can be reused.
            E.g:
                per_meeting_id: 1,2,3
                Now 2 gets deleted
                per_meeting_id: 1,3
                !!! the return value is 4 not 2, a number can't be reused
    """
    meetingModelFilter = model.objects.filter(meeting_id__name=meetingName)
    if not (meetingModelFilter.exists()):
        return 0

    return meetingModelFilter.aggregate(
        Max('per_meeting_id')).get("per_meeting_id__max") + 1
