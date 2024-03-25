"""This File contains help function for the ResponseHandler's
Here are the function implemented for specific commands like get, push or del
"""
# 'MeetingConsumer' and if TYPE_CHECKING to prevent circular import
# https://stackoverflow.com/a/39757388
# https://stackoverflow.com/a/65619382
import os
import threading
from typing import TYPE_CHECKING, Tuple

from django.db.models.aggregates import Count
if TYPE_CHECKING:
    from websocket.consumer import MeetingConsumer

from asgiref.sync import async_to_sync

from django.db.models import F
from django.db.models.base import ModelBase
from django.contrib.admin.utils import NestedObjects
from django.contrib.sessions.models import Session

from ViViPlayer.settings import BASE_DIR
from api import authSession, deserializers, screenshots, serializers
from api.models import DataAnnotation, DataPoll, DataPollAnswer, DataSatz, DataShot, DataUserStory, Meeting, MeetingVideo


def dataGet(consumer: 'MeetingConsumer', typeStr: str, model: ModelBase,
            serializer: serializers.DataSerializer, input: dict,
            meetingName: int):
    """generic get method for all data types.

    send cmd=new(get) or cmd=export(getExport) on channel_layer for specific user.
    (not the group but the user who send get)
    sends all data if data array is empty or specified ids in data.

    """

    cmd = "new" if (input['cmd'] == "get") else "export"

    # empty list, we send all available data from database
    if (len(input['data']) == 0):
        async_to_sync(consumer.channel_layer.send)(
            consumer.channel_name,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': cmd,
                    'data': serializer().serialize(
                        model.objects.filter(meeting_id__name=meetingName))
                }
            },
        )

    else:
        """
        We got a list of ids
        Send an error if id is not found but dont cancel complete transaktion.
        Example:
            id 1 is valid, id 55 is not valid
            -> "data": [1, 55]
            we send one message with data id=1 and one error message with id=55
        """
        dataList = []
        for id in input['data']:
            try:
                dataList.append(
                    model.objects.filter(meeting_id__name=meetingName).get(
                        per_meeting_id=id))
            except:
                consumer.sendErrorMessage(typeStr, "can't find id " + str(id))

        # dont send empty response
        if (len(dataList) != 0):
            async_to_sync(consumer.channel_layer.send)(
                consumer.channel_name,
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': cmd,
                        'data': serializer().serialize(dataList)
                    }
                },
            )


def dataPush(consumer: 'MeetingConsumer', typeStr: str,
             serializer: serializers.DataSerializer,
             deserializer: deserializers.DataDeserializer, input: dict,
             meetingName: int):
    """generic push method for all data types.
    send cmd=update or cmd=new back based on if data was newly inserted or updated.
    
    """

    updateList, createList, errorList = deserializer(
        meetingName).update_or_create(input['data'])

    # send error one by one
    if (len(errorList) != 0):
        for error in errorList:
            consumer.sendErrorMessage(typeStr, error)

    if (updateList):
        async_to_sync(consumer.channel_layer.group_send)(
            "meeting_" + meetingName,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': 'update',
                    'data': serializer().serialize(updateList)
                }
            },
        )

    if (createList):
        async_to_sync(consumer.channel_layer.group_send)(
            "meeting_" + meetingName,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': 'new',
                    'data': serializer().serialize(createList)
                }
            },
        )


def dataDel(consumer: 'MeetingConsumer', typeStr: str, model: ModelBase,
             input: dict, meetingName: int):
    """generic delete method for data
    """
    
    if (len(input['data']) != 1):
        consumer.sendErrorMessage(typeStr, "you can only delete one shot at a time")
        return
    
    objToDelete = model.objects.filter(meeting_id__name=meetingName).filter(per_meeting_id=input['data'][0])

    if (objToDelete):
        objToDelete.delete()

        async_to_sync(consumer.channel_layer.group_send)(
            "meeting_" + meetingName,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': 'del',
                    'data': input['data']
                }
            },
        )

    else:
        consumer.sendErrorMessage(typeStr, "cant find id to delete")


def shotPush(consumer: 'MeetingConsumer', typeStr: str, input: dict,
             meetingName: int):
    """specific push method for DataShot 
    send always all data with cmd=new
    
    """

    if (str(input['cmd']).endswith("left")):

        consumer.sendErrorMessage(typeStr, "pushLeft is not implemented")
        return

    elif (str(input['cmd']).endswith("right")):
        
        if (len(input['data']) != 1 and type(input['data'][0]) == int):
            consumer.sendErrorMessage(typeStr, "you can only insert one shot at a time or data is not an int")
            return

        # get all shots greater than or equal to the given shot
        Shots = DataShot.objects.filter(meeting_id__name=meetingName).filter(per_meeting_id__gte=input['data'][0])

        # calculate half of the duration of the given shot
        newShotDuration = (Shots[0].to - Shots[0].frm)/2.0
        # new shot start from given id since we insert the new shot to the left
        newShotFrm = Shots[0].frm + newShotDuration
        # new shot ends at half of the given shot
        newShotTo = Shots[0].to
        # the shot to the right of the new shot -> the given shot
        # starts at the new shot to value
        Shots[0].to = newShotFrm
        # save the given shot with the new timestamps
        Shots[0].save()

        # all shots after the inserted shot need to be incremented
        # but only every shot greater than given shot no greater than or equal -> [1:]
        for shot in reversed(Shots[1:]):
            shot.per_meeting_id = F('per_meeting_id') + 1
            shot.save()

        # create shot with the given shot id since we incremented every shot after that
        DataShot.objects.create(
            meeting_id=Meeting.objects.get(name=meetingName),
            per_meeting_id=input['data'][0] + 1,
            description="Eingefügter Shot nach Shot " + str(input['data'][0]),
            frm=newShotFrm,
            to=newShotTo
        )

        # generate new screenshots with thread -> so we dont block the send message
        def updateScreenShots(meetingName: int):
            video_path = MeetingVideo.objects.get(meeting__name=meetingName).videofile.path
            meeting_id = Meeting.objects.get(name=meetingName)
            
            screenshots.screenshots(video_path, os.path.join(BASE_DIR, meeting_id.screenshot_path[1:]), 
                [((shot.to + shot.frm) // 2,shot.per_meeting_id) for shot in DataShot.objects.filter(meeting_id__name=meetingName)])

        threading.Thread(target=updateScreenShots,
                                            args=(meetingName,),
                                            daemon=True,
                                            name="updateScreenShots").start()

    else:
        # just update the current shots
        # ignore update or create list, send all data down below
        _, _, errorList = deserializers.DataShotDeserializer(
            meetingName).update_or_create(input['data'])

        # send error one by one
        if (len(errorList) != 0):
            for error in errorList:
                consumer.sendErrorMessage("shot", error)
            return

    # send all shots back with cmd new
    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': typeStr,
                'cmd': 'new',
                'data': serializers.DataShotSerializer().serialize(
                    DataShot.objects.filter(meeting_id__name=meetingName))
            }
        },
    )

    sendUpdateAfterShotChange(consumer, meetingName)


def shotDel(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """specific delete method for DataShot

    deletes one shot based on his id.
    Inserted timestamp onto the left/previous shot,
    except if it is the first shot then onto the right/next shot.

    """
    if (len(input['data']) != 1):
        consumer.sendErrorMessage(typeStr, "you can only delete one shot at a time")
        return

    # get all shots
    Shots = DataShot.objects.filter(meeting_id__name=meetingName)

    # init collector
    # https://stackoverflow.com/a/12162619
    collector = NestedObjects(using='default')

    if (len(Shots) < 2):
        consumer.sendErrorMessage(typeStr, "there is only one shot left, can't delete that one")
        return

    decrement = False
    for idx, shot in enumerate(Shots):

        # decrement the following ids after delete
        if (decrement):
            # https://docs.djangoproject.com/en/3.1/ref/models/instances/#updating-attributes-based-on-existing-fields
            shot.per_meeting_id = F('per_meeting_id') - 1
            shot.save()

        # insert timestamp onto the previous one, and delete shot with given id
        if (idx > 0 and shot.per_meeting_id == input['data'][0]):
            Shots[idx - 1].to = shot.to
            Shots[idx - 1].save()

            # only delete shot without any data
            # 1 since nested returns the shot itself
            collector.collect([shot])
            if (len(collector.nested()) != 1):
                consumer.sendErrorMessage(typeStr, """Du kannst diesen Shot nicht löschen. 
                    An diesem Shot sind UserStorys, Sätze oder Annotationen verknüpft.
                    Lösche vorher die an den Shot verknüpften Daten.""")
                return

            shot.delete()
            # mark decrement as True so that in the next loop the per_meeting_id's can be decremented
            decrement = True

            # delete screenshot
            screenshots.deletescreenshot(meetingName, input['data'][0])

        # insert timestamp onto the next one, and delete shot with given id
        # this is shot 0
        elif (shot.per_meeting_id == input['data'][0]):

            # only delete shot without any data
            # 1 since nested returns the shot itself
            collector.collect([shot])
            if (len(collector.nested()) != 1):
                consumer.sendErrorMessage(typeStr, """Du kannst diesen Shot nicht löschen. 
                    An diesem Shot sind UserStorys, Sätze oder Annotationen verknüpft.
                    Lösche vorher die an den Shot verknüpften Daten.""")
                return

            # save old frm field and delete shot
            oldShotFrm = shot.frm
            shot.delete()

            Shots[idx + 1].frm = oldShotFrm
            Shots[idx + 1].save()

            # mark decrement as True so that in the next loop the per_meeting_id's can be decremented
            decrement = True

            # delete screenshot
            screenshots.deletescreenshot(meetingName, input['data'][0])

    # check if decrement flag was set
    if not decrement:
        consumer.sendErrorMessage(typeStr, "not a valid shot id")
        return

    # send the new shots with cmd=new to all users
    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': typeStr,
                'cmd': 'new',
                'data': serializers.DataShotSerializer().serialize(
                    DataShot.objects.filter(meeting_id__name=meetingName))
            }
        },
    )

    sendUpdateAfterShotChange(consumer, meetingName)


def sendUpdateAfterShotChange(consumer: 'MeetingConsumer', meetingName: int):
    """
    #TODO add more data if there is more than userstory, satz
    """
    
    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': "userstory",
                'cmd': 'update',
                'data': serializers.DataUserStorySerializer().serialize(
                    DataUserStory.objects.filter(meeting_id__name=meetingName))
            }
        },
    )

    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': "satz",
                'cmd': 'update',
                'data': serializers.DataSatzSerializer().serialize(
                    DataSatz.objects.filter(meeting_id__name=meetingName))
            }
        },
    )

    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': "annotation",
                'cmd': 'update',
                'data': serializers.DataAnnotationSerializer().serialize(
                    DataAnnotation.objects.filter(meeting_id__name=meetingName))
            }
        },
    )

    # send update of shot_id in poll
    pollUpdate(consumer, "poll", meetingName)

def pollCreate(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """Always creates a new poll.
    After a poll was created send a new message to everyone in the meeting.
    """

    if (len(input['data']) != 1):
        consumer.sendErrorMessage(typeStr, "you can only create one poll at a time.")
        return

    if (DataPoll.objects.filter(meeting_id__name=meetingName).filter(active__exact=True).exists()):
        consumer.sendErrorMessage(typeStr, "you can only have one active poll at a time.")
        return

    # dataPoll can't get updates only new polls are created
    _, createList, errorList = deserializers.DataPollDeserializer(
            meetingName).update_or_create(input['data'])

    # send error one by one
    if (len(errorList) != 0):
        for error in errorList:
            consumer.sendErrorMessage(typeStr, error)

    if (createList):
        async_to_sync(consumer.channel_layer.group_send)(
            "meeting_" + meetingName,
            {
                'type': 'group_msg',
                'msg': {
                    'type': typeStr,
                    'cmd': 'new',
                    'data': serializers.DataPollSerializer().serialize(createList)
                }
            },
        )

    # send empty result to moderator
    sendResult(consumer, "poll", createList, meetingName)


def pollVote(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """Every session can cast a vote in a poll.
    Send result to moderator for live updates.
    """

    # input['data'] can have more than one vote
    for voteObj in input['data']:

        # check if poll_id exists
        try:
            poll_id = DataPoll.objects.filter(meeting_id__name=meetingName).get(per_meeting_id=voteObj['poll_id'])
        except:
            consumer.sendErrorMessage(typeStr, "poll_id " + str(voteObj['poll_id']) + " does not exists")
            continue

        # check if the set(unique values only) is the same as the array itself
        if len(voteObj['vote']) > len(set(voteObj['vote'])):
            consumer.sendErrorMessage(typeStr, "values in vote are not unqiue")
            # skip this vote data 
            continue

        # dont allow voting afer poll is closed
        if not (poll_id.active):
            consumer.sendErrorMessage(typeStr, "you cant vote on a closed poll")
            continue

        # check if session has already voted in poll
        if (DataPollAnswer.objects.filter(poll_id=poll_id).filter(session=Session.objects.get(pk=consumer.scope['session'].session_key)).exists()):
            consumer.sendErrorMessage(typeStr, "you already voted in poll_id "+ str(voteObj['poll_id']))
            continue
        
        maxOption_id = len(poll_id.options)

        for vote in voteObj['vote']:

            # check if the id is between 0 and max allowed index
            if (vote >= maxOption_id or vote < 0):
                consumer.sendErrorMessage(typeStr, "not a valid option_id in vote")
            else:
                DataPollAnswer(
                    poll_id=poll_id,
                    session=Session.objects.get(pk=consumer.scope['session'].session_key),
                    option_id=vote
                ).save()

        sendResult(consumer, "poll", [poll_id], meetingName)


def getResult(polls: list[DataPoll]) -> Tuple[list[dict], list[dict], list[dict]]:
    """Create active and inactive Poll list with results from DataPoll list.
    """

    activePolls = []
    inActivePollsPublic = []
    inActivePollsPrivate = []

    for poll in polls:

        # count every option_id in database
        pollAnswerRanking = DataPollAnswer.objects.filter(poll_id=poll).values('option_id').annotate(count=Count('option_id')).order_by('-count')

        result = []
        optionInResult = []

        for rank in pollAnswerRanking:
            result.append({
                'option': poll.options[rank.get('option_id')],
                'count': rank.get('count')
            })
            # save option(NOT id, the string) which is in the pollAnswerRanking
            optionInResult.append(poll.options[rank.get('option_id')])

        # add options with a count of 0 -> missing in result/pollAnswerRanking
        for missingOption in [x for x in poll.options if x not in optionInResult]:
            result.append({
                'option': missingOption,
                'count': 0
            })

        # create the serialized data from DataPoll and replace options with result
        jsonDataPoll = serializers.DataPollSerializer().serialize([poll])[0]
        # index 0 since we got a list with only one DataPoll
        jsonDataPoll.pop('options')
        jsonDataPoll['result'] = result

        if(poll.active):
            activePolls.append(jsonDataPoll)
        else:
            if poll.public:
                inActivePollsPublic.append(jsonDataPoll)
            else:
                inActivePollsPrivate.append(jsonDataPoll)
    
    return activePolls, inActivePollsPublic, inActivePollsPrivate


def sendResult(consumer: 'MeetingConsumer', typeStr: str, polls: list[DataPoll],
            meetingName: int, isResultExport: bool = False, forAll: bool = True) -> None:
    """Send a result message to moderator and/or user.
    For the user a message is send only if poll is closed.
    The moderator can receive message if the poll is still active.
    """
    activePolls, inActivePollsPublic, inActivePollsPrivate = getResult(polls)

    # message for all users/moderator
    if forAll:
        # only allow active polls to be send to moderator
        if (len(activePolls) != 0):

            async_to_sync(consumer.channel_layer.group_send)(
                "meeting_" + meetingName + "_mod",
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': 'result',
                        'data': activePolls
                    }
                },
            )

        # send closed poll to everyone
        # but only if the poll is public
        if (len(inActivePollsPublic) != 0):

            async_to_sync(consumer.channel_layer.group_send)(
                "meeting_" + meetingName,
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': "exportResult" if (isResultExport) else "result",
                        'data': inActivePollsPublic
                    }
                },
            )

        # send closed poll to moderator
        # since the poll should be private
        if (len(inActivePollsPrivate) != 0):

            async_to_sync(consumer.channel_layer.group_send)(
                "meeting_" + meetingName + "_mod",
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': "exportResult" if (isResultExport) else "result",
                        'data': inActivePollsPrivate
                    }
                },
            )

    # only for sender i.e. get message
    else:
        # only allow active polls to be send to moderator
        if (len(activePolls) != 0 and authSession.isModeratorInMeeting(consumer.scope['session'], meetingName)):

            async_to_sync(consumer.channel_layer.send)(
                consumer.channel_name,
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': 'result',
                        'data': activePolls
                    }
                },
            )

        # send public poll to sender
        if (len(inActivePollsPublic) != 0):

            async_to_sync(consumer.channel_layer.send)(
                consumer.channel_name,
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': "exportResult" if (isResultExport) else "result",
                        'data': inActivePollsPublic
                    }
                },
            ) 
        
        if (len(inActivePollsPrivate) != 0 and authSession.isModeratorInMeeting(consumer.scope['session'], meetingName)):

            async_to_sync(consumer.channel_layer.send)(
                consumer.channel_name,
                {
                    'type': 'group_msg',
                    'msg': {
                        'type': typeStr,
                        'cmd': "exportResult" if (isResultExport) else "result",
                        'data': inActivePollsPrivate
                    }
                },
            )


def pollClose(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """Set poll to inactive/closed.
    At the end send the result to everyone.
    """
    
    if (len(input['data']) != 1):
        consumer.sendErrorMessage(typeStr, "can only close one poll at a time")
        return

    poll = DataPoll.objects.filter(meeting_id__name=meetingName).get(per_meeting_id=input['data'][0].get('id'))

    if not (poll.active):
        consumer.sendErrorMessage(typeStr, "poll already closed")
        return

    poll.public = input['data'][0].get('publish')
    poll.active = False
    poll.save()

    # send close message to everyone
    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': typeStr,
                'cmd': "close",
                'data': [poll.per_meeting_id]
            }
        },
    ) 

    sendResult(consumer, typeStr, [poll], meetingName)

def pollGet(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """Implement custom get message with return of new/export and result/resultExport.
    """
    
    # send new/export message with generic data handler
    dataGet(consumer, "poll", DataPoll, serializers.DataPollSerializer, input, meetingName)

    isExport = True if input['cmd'] == "getExport" else False

    # send result/getExport to moderator and user
    if (len(input['data']) == 0):
        sendResult(consumer, typeStr, list(DataPoll.objects.filter(meeting_id__name=meetingName)), meetingName, isExport, False)
    else:
        # got a list of ids
        dataList = []
        for id in input['data']:
            try:
                dataList.append(
                    DataPoll.objects.filter(meeting_id__name=meetingName).get(
                        per_meeting_id=id))
            except:
                consumer.sendErrorMessage(typeStr, "can't find id " + str(id))

        # dont send empty response
        if (len(dataList) != 0):
            sendResult(consumer, typeStr, dataList, meetingName, isExport, False)

def pollUpdate(consumer: 'MeetingConsumer', typeStr: str, meetingName: int):
    """This sends an update of all finshed polls to change the shot_id.
    """

    updateList = []

    for poll in DataPoll.objects.filter(meeting_id__name=meetingName).filter(active__exact=False):
        updateList.append({
            "id": poll.per_meeting_id,
            "shot_id": poll.shot_id.per_meeting_id
        })

    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': typeStr,
                'cmd': 'update',
                'data': updateList
            }
        },
    )

def annotationDel(consumer: 'MeetingConsumer', typeStr: str, input: dict,
            meetingName: int) -> None:
    """specific delete method for DataAnnotation

    deletes one Annotation based on his id.
    Return message that the given id is deleted.
    The id's are not changed -> every id is only used once.
    """
    if (len(input['data']) != 1):
        consumer.sendErrorMessage(typeStr, "you can only delete one annotation at a time")
        return

    try:
        deletedAnno = DataAnnotation.objects.filter(meeting_id__name=meetingName).get(per_meeting_id=input['data'][0])
        deletedAnno.delete()
    except:
        consumer.sendErrorMessage(typeStr, "Annotation does not exists.")
        return

    # send message that annotation was deleted
    async_to_sync(consumer.channel_layer.group_send)(
        "meeting_" + meetingName,
        {
            'type': 'group_msg',
            'msg': {
                'type': typeStr,
                'cmd': 'del',
                'data': {
                    'id': deletedAnno.per_meeting_id,
                    'shot_id': deletedAnno.shot_id.per_meeting_id
                }
            }
        },
    )