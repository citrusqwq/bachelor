import cv2
import re
import os
import inspect
import glob
from typing import Union

from ViViPlayer.settings import BASE_DIR
from api.models import Meeting


def screenshots(videoPath: str, screenshotPath: str, timestamps: Union[list[tuple[float, int]], tuple[float, int]]) -> None:
    """
    Extracts screenshots from a video given the list of timestamps.
    Overwrites screenshots if file already exists.
    Args:
        param1 (str): path to video
        param2 (list): iterable list of tuples (Timestamps (in seconds as float) and shot id) \
                or one single tuple of a timestamp and shot id
    Returns:
        (str): path to Screenshots directory
    """

    vidcap = cv2.VideoCapture(videoPath)

    if inspect.stack()[1][3] == 'insertShots':
        files = glob.glob(f'{screenshotPath}*.jpg')
        for file in files:
            try:
                os.remove(file)
            except OSError as e:
                print(f'Error: {file} : {e.strerror}')

    # Save enumerating screenshots into Screenshots directory
    if isinstance(timestamps, list):
        for elem in timestamps:
            vidcap.set(cv2.CAP_PROP_POS_MSEC, elem[0] * 1000)
            success, image = vidcap.read()
            if success:
                cv2.imwrite(f'{screenshotPath}{elem[1]}.jpg', image) # save frame as JPEG file
                cv2.waitKey()
    # Save single screenshot with given shot id
    else:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, timestamps[0] * 1000)
        success, image = vidcap.read()
        if success:
            cv2.imwrite(f'{screenshotPath}{timestamps[1]}.jpg', image)
            cv2.waitKey()

    return


# Test run (list of tuples)
# sections = [(sec, n+1) for sec, n in enumerate([2, 4, 6, 8, 10])]
# outPath = screenshots('goldeneye.mp4', sections)
# print(outPath)

# Test run (single tuple)
# outPath = screenshots('goldeneye.mp4', (42, 2))
# print(outPath)

def deletescreenshot(meetingName: int, shot_id: int) -> None:
    """
    Deletes screenshot with given shot_id, decreases all following filenames.
    Args:
        param1 (int): meetingName
        param2 (int): shot id
    Returns:
        None
    """
    DIRPath = os.path.join(BASE_DIR, Meeting.objects.get(name=meetingName).screenshot_path[1:])

    # Lambda function for natural sort
    natsort = lambda s: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
    # Regex to extract filenames
    regex = r"(.*\/)(\d+)(.jpg)"

    files = sorted(glob.glob(f'{DIRPath}*.jpg'), key=natsort)

    # match[0] = /code/media/Screenshots/
    # match[1] = number
    # match[2] = .jpg
    for i in range(len(files)):
        match = re.findall(regex, files[i])[0]
        if int(match[1]) == shot_id:
            os.remove(files[i])
            print()
            for j in range(i+1, len(files)):
                match = re.findall(regex, files[j])[0]
                os.rename(files[j], f'{match[0]}{int(match[1])-1}{match[2]}')
            return
