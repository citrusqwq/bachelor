import io
import os
from zipfile import ZipFile
from typing import Text
import zipfile

from django.db.models.aggregates import Count

from api.models import DataPollAnswer, DataSatz, DataShot, DataUserStory, DataPoll, Meeting
from ViViPlayer.settings import BASE_DIR

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span
from odf.draw import Frame,Image
from odf import teletype

def ExportODT(meetingNumber: int):
    """Exports User Stories and Sätze of this meeting as an .odt file

    Args: 
        meetingNumber
    Returns:
        odt file containing data of meeting
    """

    screenshot_path = os.path.join(BASE_DIR, Meeting.objects.get(name=meetingNumber).screenshot_path[1:])

    # create new odt file
    textdoc = OpenDocumentText()

    #create all neccessery styles
    documentStyles = textdoc.styles

    # style for headlines
    h1style = Style(name="Heading 1", family="paragraph")
    h1style.addElement(TextProperties(attributes={'fontsize':"26pt",'fontweight':"bold" }))
    documentStyles.addElement(h1style)

    # style for under headline (shots in this case)
    underHeadline = Style(name="Heading 2", family="paragraph")
    underHeadline.addElement(TextProperties(attributes={'fontsize':"18pt"}))
    documentStyles.addElement(underHeadline)

    # style for text (storys and sentences in this case)
    textStyle = Style(name="Text 1", family="paragraph")
    textStyle.addElement(TextProperties(attributes={'fontsize':"14pt"}))
    documentStyles.addElement(textStyle)

    # create headline for document
    header=H(outlinelevel=1, stylename=h1style, text="Ergebnisse Meeting: ")
    textdoc.text.addElement(header)
    emptyLine = P(text="")
    textdoc.text.addElement(emptyLine)

    # Justified style
    justifystyle = Style(name="justified", family="graphic")
    justifystyle.addElement(ParagraphProperties(attributes={"textalign": "justify"}))

    # get shots from this meeting
    shots = DataShot.objects.filter(meeting_id__name=meetingNumber)
    
    for currentShot in shots:
        # get all userstorys and sätze for this shot
        allUserStory = DataUserStory.objects.filter(shot_id=currentShot)
        allSatz = DataSatz.objects.filter(shot_id=currentShot)
        allPolls = DataPoll.objects.filter(shot_id=currentShot)

        # check if there is a userstory or satz writen to a given shot
        if allUserStory or allSatz or allPolls:
            # create style for shot
            shot = H(outlinelevel=2, stylename=underHeadline, text=currentShot.description)
            textdoc.text.addElement(shot)

            shotStringID = str(currentShot).split(' ')[1]
            # Adding a paragraph
            paragraph_element = P(stylename=justifystyle)
            paragraph_text=""
            teletype.addTextToElement(paragraph_element, paragraph_text)
            textdoc.text.addElement(paragraph_element, paragraph_text)

            # add picture
            picframe=Frame(anchortype="as-char", width="100mm", height="80mm",name='image1')
            href=textdoc.addPicture(str(screenshot_path) + str(shotStringID) + ".jpg")
            picframe.addElement(Image(href=href,actuate="onLoad",show="embed",type="simple"))
            paragraph_element.addElement(picframe)

            emptyLine = P(text="")
            textdoc.text.addElement(emptyLine)

            # write currentStory to odt file
            for currentStory in allUserStory:
                storyString = str(currentStory).split(' ')[1]
                story = P(stylename=textStyle,
                    text= "User Story " + str(storyString) + ": " + currentStory.role +
                    " " + currentStory.capability + " " + currentStory.benefit
                )
                textdoc.text.addElement(story)

            # if there is at least one usertstory in this shot, add newline
            if allUserStory:
                emptyLine = P(text="")
                textdoc.text.addElement(emptyLine)

            # add sätze to document
            for currentSatz in allSatz:
                storyString = str(currentSatz).split(' ')[1]
                satz = P(stylename=textStyle, text= "Satz " + str(storyString) + ": " + currentSatz.satz)
                textdoc.text.addElement(satz)

            if allPolls:
                for currentPoll in allPolls:
                    pollString = str(currentPoll).split(' ')[1]
                    poll = P(stylename=textStyle, text= "Umfrage " + str(pollString) + ": " + str(currentPoll.question))
                    textdoc.text.addElement(poll)

                    # count every option_id in database
                    pollAnswerRanking = DataPollAnswer.objects.filter(poll_id=currentPoll).values('option_id').annotate(count=Count('option_id')).order_by('-count')

                    result = []
                    optionInResult = []

                    for rank in pollAnswerRanking:
                        result.append((currentPoll.options[rank.get('option_id')], rank.get('count')))
                        # save option(NOT id, the string) which is in the pollAnswerRanking
                        optionInResult.append(currentPoll.options[rank.get('option_id')])

                    # add options with a count of 0 -> missing in result/pollAnswerRanking
                    for missingOption in [x for x in currentPoll.options if x not in optionInResult]:
                        result.append((missingOption, 0))

                    for currentAnswer in result:
                        answer = P(stylename=textStyle, text="Antwort: '" + str(currentAnswer[0]) + "'" + " Stimmen: '" + str(currentAnswer[1]) + "'") 
                        textdoc.text.addElement(answer)

                    emptyLine = P(text="")
                    textdoc.text.addElement(emptyLine)

            if not allPolls:
                # add newline
                emptyLine = P(text="")
                textdoc.text.addElement(emptyLine)

    # save and return result
    result = io.BytesIO()
    textdoc.save(result)
    return result

def ExportCSV(meetingNumber: int):
    """Exports User Stories and Sätze of this meeting as an .zip file with csv file and screenshots

    Args: 
        meetingNumber
    Returns:
        bytesIO object of zip file with csv and screenshots ! use .seek(0)
    """

    # shot_id set
    # only add screenshot with a userStory or satz
    shotIdUnqiue = set()

    textFileStringIO = io.StringIO()

    textFileStringIO.write("Nummer,")
    textFileStringIO.write("ShotNummer,")
    textFileStringIO.write("ShotName,")
    textFileStringIO.write("Inhalt,")
    textFileStringIO.write("ScreenshotDateiname")
    textFileStringIO.write("\n")

    for userStory in DataUserStory.objects.filter(meeting_id__name=meetingNumber):
        # user story info
        textFileStringIO.write("UserStory ")
        textFileStringIO.write(str(userStory.per_meeting_id))
        textFileStringIO.write(",Shot ")
        textFileStringIO.write(str(userStory.shot_id.per_meeting_id))
        textFileStringIO.write(",")
        textFileStringIO.write(str(userStory.shot_id.description))
        textFileStringIO.write(",")
        # user story content
        textFileStringIO.write(str(userStory.role))
        textFileStringIO.write(str(userStory.capability))
        textFileStringIO.write(str(userStory.benefit))

        textFileStringIO.write("," + str(userStory.shot_id.per_meeting_id) + ".jpg")
        textFileStringIO.write('\n')

        shotIdUnqiue.add(userStory.shot_id.per_meeting_id)

    for satz in DataSatz.objects.filter(meeting_id__name=meetingNumber):
        # satz info
        textFileStringIO.write("Satz ")
        textFileStringIO.write(str(satz.per_meeting_id))
        textFileStringIO.write(",Shot ")
        textFileStringIO.write(str(satz.shot_id.per_meeting_id))
        textFileStringIO.write(",")
        textFileStringIO.write(str(satz.shot_id.description))
        textFileStringIO.write(",")
        # satz content
        textFileStringIO.write(str(satz.satz))

        textFileStringIO.write("," + str(satz.shot_id.per_meeting_id) + ".jpg")
        textFileStringIO.write('\n')

        shotIdUnqiue.add(satz.shot_id.per_meeting_id)

    # create bytesIO object for zipFile
    textFileStringIO.seek(0)
    textfileBytesIO = io.BytesIO(textFileStringIO.read().encode('utf8'))

    # create zip file
    zip_buffer  = io.BytesIO()
    zipObj = ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

    # add txt file
    with zipObj.open('Meeting' + str(meetingNumber) + '.csv', 'w') as textFile:
        textFile.write(textfileBytesIO.read())
    
    # add shot screenshots
    screenshot_path = os.path.join(BASE_DIR, Meeting.objects.get(name=meetingNumber).screenshot_path[1:])

    # Iterate over all the files in screenshot dir
    for folderName, _, filenames in os.walk(screenshot_path):
        for filename in filenames:

            # check if shot_id is present
            # only add screenshot that have a userstory or satz
            # split because screenshots look like this x.jpg -> we only need x the shot_id
            if int(filename.split('.')[0]) in shotIdUnqiue:
                #create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath, 'screenshots/' + filename)

    # write zip obj and return bytesIO
    zipObj.close()
    zip_buffer.seek(0)
    return zip_buffer
    