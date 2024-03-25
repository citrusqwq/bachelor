import os
from typing import Type
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache

# Standard PySceneDetect imports:
from scenedetect import VideoManager
from scenedetect import SceneManager

# For content-aware scene detection:
from scenedetect.detectors import ContentDetector
from scenedetect.frame_timecode import FrameTimecode
from api import serializers

from ViViPlayer.settings import BASE_DIR
from api.models import DataShot, Meeting
from api.screenshots import screenshots



def convertTimestamp(timecode: Type[FrameTimecode]) -> int:
    # Helper function returns time in total seconds
    h, m, s = str(timecode).split(':')
    return int(h) * 3600 + int(m) * 60 + int(s[:2])


def find_scenes(video_path: str, threshold=30.0) -> list[tuple[int, int]]:
    """
    Returns a list of int tuples with number of a scene and the starting point in seconds
    Args:
        param1 (str): path to video
        param2 (float): threshold sensitivity
    Returns:
        Returns a list of int tuples. start and stop of each scene in seconds
    """
    # Create our video & scene managers, then add the detector.
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    # Improve processing speed by downscaling before processing.
    video_manager.set_downscale_factor()

    # Start the video manager and perform the scene detection.
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scenes =  scene_manager.get_scene_list()

    shots = []
    # Leave out too short sections
    for scene in scenes:
        start, end = convertTimestamp(scene[0]), convertTimestamp(scene[1])
        if start != end:
            shots.append((start, end))

    return shots


# Beispiel-Durchlauf

# scenes = find_scenes('goldeneye.mp4')

# for scene in scenes:
#     print(scene)

def insertShots(meetingName: int, video_path: str, scenes: list[tuple[int, int]]) -> None:
    """

    Note: If the detection goes to fast the client might not be connected.
    And doesnt recive the websocket message.

    !! old shots need to be delete before this method is called
    """

    meeting_id = Meeting.objects.get(name=meetingName)

    # add shots
    for idx, scene in enumerate(scenes):
        DataShot(
            meeting_id=meeting_id,
            per_meeting_id=idx,
            description= "Detected Shot " + str(idx),
            frm = scene[0],
            to = scene[1]
        ).save()

    # Create initial screenshots of detected scenes (middle of scene)
    screenshots(video_path, os.path.join(BASE_DIR, meeting_id.screenshot_path[1:]) , [((shot[0] + shot[1]) // 2, idx) for (idx, shot) in enumerate(scenes)])

    # send new shots to meeting
    # https://stackoverflow.com/a/51303058
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "meeting_" + str(meetingName),
        {
            'type': 'group_msg',
            'msg': {
                'type': "shot",
                'cmd': 'new',
                'data': serializers.DataShotSerializer().serialize(
                    DataShot.objects.filter(meeting_id=meeting_id).all())
            }
        },
    )

def findInsertShots(meetingName: int, video_path: str, threshold=30.0):
    """
    """
    # signal that shots are loading 
    loadingShots(meetingName)

    try:
        insertShots(meetingName, video_path, find_scenes(video_path, threshold))
        # signal that shots have finished loading
        loadingShots(meetingName, True)
    except Exception as e:
        # signal that shots have finished loading
        loadingShots(meetingName, True)

        # send error to fronted
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "meeting_" + str(meetingName),
            {
                'type': 'group_msg',
                'msg': {
                    'type': "shot",
                    'cmd': 'error',
                    'data': ["Could not detect any Shots. " + str(e)]
                }
            },
        )


def loadingShots(meetingName: int, isFinished: bool = False) -> None:
    """Signal that shots are loading/finished loading for frontend and backend.
    For Backend set/delete a cache key that signals shots are loading/finished loading.
        This cache key can be queried everywhere in the backend to check if shots are loading.
        https://docs.djangoproject.com/en/3.2/topics/cache/#django.core.caches.cache.get
    For Fronted send a control message to enable/disable the loading spinner.

    Args:
        isFinished: If shots loading has finished. Defauls to false -> shots are loading.
    Returns:
        None
    """
    if not isFinished:
        # given the key 120 seconds to live
        cache.set("meeting_" + str(meetingName) + "_loadShot", None, 120)
    else:
        cache.delete("meeting_" + str(meetingName) + "_loadShot")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
            "meeting_" + str(meetingName),
            {
                'type': 'group_msg',
                'msg': {
                    'type': "control",
                    'cmd': 'loadShot',
                    'data': not isFinished
                }
            },
        )