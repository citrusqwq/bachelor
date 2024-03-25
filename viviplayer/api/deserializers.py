"""This contains all deserializer for the models.
Every deserializer is a derived from the base class DataDeserializer.

Usage:
    XDeserializer(meetingName).update_or_create(list[dict])
"""
from typing import Tuple

from django.db import models
from django.db.models.base import Model

from api.models import (DataAnnotation, DataPoll, DataSatz, DataShot, DataUserStory, Meeting,
                        getNextPerMeetingId)


class DataDeserializer:
    """This is the BaseClass for all Deserializers.
    The method deserialize an list of dictionaries from JSON data and converts it to a model.
    Every DataDeserializer is tied to a meeting name.

    Following methods need to be implemented by the derived class:
        -obj_deserialize -> This takes one dictionary and converts it to a model
        _obj_update_or_create -> This just maps the correct update_or_create method from the model

    Only the method update_or_create() should be called from the outside.
    This method takes a list of one or more dictionarys and updates or creates a model.
    """
    def __init__(self, meetingName: int) -> None:
        """
        Args:
            meetingName: The generated model is tied to the meeting number.
        """
        self._meetingName = meetingName

    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        """Needs to be implemented by the derived class.
        This converts a dict to a model.

        Args:
            inputDict: JSON object as python dict

        Returns:
            models.Model: The converted model

        Raises:
            Exception: If dict can't be converted to a model
        """
        pass

    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        """Needs to be implemented by the derived class.
        This just maps the correct update_or_create method, for the deserializer, from the model.
        For more info take a look at the update_or_create method from a model

        Args:
            input: A instance of a model for which the method update_or_create gets called

        Returns:
            Tuple[Model, bool]: The result of of update_or_create
        """
        pass

    def _getPerMeetingID(self, model: Model, perMeetingID: int,
                         meetingObj: Meeting.objects) -> int:
        """This gets the the correct per_meeting_id from the given model in a meeting.
        If the per_meeting_id already exists return the per_meeting_id unchanged else return the next per_meeting_id.

        Args:
            model: The model for which the correct per_meeting_id gets calculated
            perMeetinigID: The curent per_meeting_id
            meetingObj: The instance of the meeting object

        Returns:
            int: A new per_meeting_id or if the given per_meeting_id exist return it unchanged
        """
        try:
            model.objects.filter(meeting_id=meetingObj).get(
                per_meeting_id=perMeetingID)
            return perMeetingID
        except:
            return getNextPerMeetingId(model, self._meetingName)

    def _getDataShotFromPerMeetingID(self, shot_id: int,
                                     meetingObj: Meeting.objects) -> DataShot:
        """This takes a shot_id as int and returns the correct DataShot instance.
        The shot_id is NOT the key from DataShot. This is the per_meeting_id from DataShot.
        For per_meeting_id this method also needs the meeting instance.

        Args:
            shot_id: The per_meeting_id in DataShot
            meetingObj: The instance of the meeting object

        Returns:
            DataShot: The instance of DataShot identified from per_meeting_id and meeting_id.
                Since per_meeting_id and meeting_id are unique together they can identify a DataShot instance.

        Raises:
            Exception: If no DataShot can be found.
        """
        try:
            return DataShot.objects.filter(meeting_id=meetingObj).get(
                per_meeting_id=shot_id)
        except:
            raise Exception("invalid or missing shot_id")

    def update_or_create(
            self, inputList: list[dict]
    ) -> Tuple[list[Model], list[Model], list[str]]:
        """This takes a list from a JSON string and inserts or updates them in the database.
        For future handling the method returns three lists, if a model got updated, created or if an error occured.
        !!! The returned models are at this point already inserted or updated in the databses.

        Args:
            inputData: list of dict from json.loads(data)

        Returns:
            as Tuple ->(
            createList: a list of instances of model that got created
            updateList: a list of instances of model that got updated
            errorList:  a list of string with an error message for the frontend
            )
        """

        updateList = []
        createList = []
        errorList = []

        for input in inputList:
            try:
                obj, created = self._obj_update_or_create(
                    self._obj_deserialize(input))
                if created:
                    createList.append(obj)
                else:
                    updateList.append(obj)
            except Exception as e:
                errorList.append(str(e))

        return (updateList, createList, errorList)


class DataShotDeserializer(DataDeserializer):
    """This class deserializes the model DataUserStory
    """
    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        meeting_id = Meeting.objects.get(name=self._meetingName)

        try:
            result = DataShot(
                meeting_id=meeting_id,
                per_meeting_id=self._getPerMeetingID(DataShot, inputDict['id'],
                                                     meeting_id),
                description=inputDict['description'],
                frm=inputDict['frm'],
                to=inputDict['to'],
            )
        except:
            raise Exception(
                "failed to create Model, are all data fields there?")

        return result

    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        return DataShot.update_or_create(input)


class DataUserStoryDeserializer(DataDeserializer):
    """This class deserializes the model DataUserStory
    """
    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        meeting_id = Meeting.objects.get(name=self._meetingName)
        try:
            shot_id = self._getDataShotFromPerMeetingID(
                inputDict['shot_id'], meeting_id)
        except:
            raise Exception("invalid or missing shot_id")

        try:
            result = DataUserStory(
                meeting_id=meeting_id,
                per_meeting_id=self._getPerMeetingID(DataUserStory, inputDict['id'],
                                                     meeting_id),
                shot_id=shot_id,
                role=inputDict['role'],
                capability=inputDict['capability'],
                benefit=inputDict['benefit'],
            )
        except:
            raise Exception(
                "failed to create Model, are all data fields there?")

        return result

    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        return DataUserStory.update_or_create(input)


class DataSatzDeserializer(DataDeserializer):
    """This class deserializes the model DataUserStory
    """
    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        meeting_id = Meeting.objects.get(name=self._meetingName)
        try:
            shot_id = self._getDataShotFromPerMeetingID(
                inputDict['shot_id'], meeting_id)
        except:
            raise Exception("invalid or missing shot_id")

        try:
            result = DataSatz(
                meeting_id=meeting_id,
                per_meeting_id=self._getPerMeetingID(DataSatz, inputDict['id'],
                                                     meeting_id),
                shot_id=shot_id,
                satz=inputDict['satz'],
            )
        except:
            raise Exception(
                "failed to create Model, are all data fields there?")

        return result

    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        return DataSatz.update_or_create(input)


class DataPollDeserializer(DataDeserializer):
    """This class deserializes the model DataPoll
    """
    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        meeting_id = Meeting.objects.get(name=self._meetingName)
        try:
            shot_id = self._getDataShotFromPerMeetingID(
                inputDict['shot_id'], meeting_id)
        except:
            raise Exception("invalid or missing shot_id")
        
        try:
            result = DataPoll(
                meeting_id=meeting_id,
                per_meeting_id=self._getPerMeetingID(DataPoll, -1, meeting_id),
                shot_id=shot_id,
                response= inputDict['response'],
                question= inputDict['question'],
                options= inputDict['options']
            )

        except:
            raise Exception(
                "failed to create Model, are all data fields there?")

        return result


    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        return DataPoll.update_or_create(input)


class DataAnnotationDeserializer(DataDeserializer):
    """This class deserializes the model DataAnnotatio
    """
    def _obj_deserialize(self, inputDict: dict) -> models.Model:
        meeting_id = Meeting.objects.get(name=self._meetingName)
        try:
            shot_id = self._getDataShotFromPerMeetingID(
                inputDict['shot_id'], meeting_id)
        except:
            raise Exception("invalid or missing shot_id")
        
        try:
            result = DataAnnotation(
                meeting_id=meeting_id,
                per_meeting_id=self._getPerMeetingID(DataAnnotation, inputDict['id'], meeting_id),
                shot_id=shot_id,
                pos_x =  inputDict['pos'][0],
                pos_y =  inputDict['pos'][1],
                titel = inputDict['titel'],
                text_type = inputDict['text_type'],
                text = inputDict['text']
            )

        except:
            raise Exception(
                "failed to create Model, are all data fields there?")

        return result


    def _obj_update_or_create(self, input: Model) -> Tuple[Model, bool]:
        return DataAnnotation.update_or_create(input)