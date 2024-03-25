from datetime import datetime
from django.contrib import admin
from django.utils.timezone import now
from rangefilter.filters import DateTimeRangeFilter

from api.models import DataAnnotation, DataPoll, DataPollAnswer, DataSatz, DataUserStory, Meeting, DataShot, MeetingVideo, UserCreationSecret


class DataAdmin(admin.ModelAdmin):
    list_display = (
        "meeting_id",
        "per_meeting_id",
    )
    list_filter = ("meeting_id", )


class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "active",
        "moderator",
        "created_at",
    )
    list_editable = ("active", )
    list_filter = ("moderator", )


class UserCreationSecretAdmin(admin.ModelAdmin):
    # https://github.com/silentsokolov/django-admin-rangefilter
    list_display = (
        'valid_until',
        'isValid'
    )

    list_filter = (
        ('valid_until', DateTimeRangeFilter),
    )

    @admin.display(boolean=True)
    def isValid(self, obj):
        if obj.valid_until < now():
            return False
        else:
            return True
    

    def get_rangefilter_valid_until_default(self, request):
        return (datetime.fromtimestamp(0), now())


# Register your models here.
admin.site.register(DataShot, DataAdmin)
admin.site.register(DataUserStory, DataAdmin)
admin.site.register(DataSatz, DataAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingVideo,)
admin.site.register(DataPoll, DataAdmin)
admin.site.register(DataPollAnswer,)
admin.site.register(DataAnnotation, DataAdmin)
admin.site.register(UserCreationSecret, UserCreationSecretAdmin)