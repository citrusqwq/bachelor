"""Serialization of Models

Usage:
   XSerializer().serialize(data)

"""
from django.db.models.base import Model


class DataSerializer:
    """
    TODO
    """
    def get_dump_object(self, obj) -> dict:
        """
        TODO
        """
        pass

    def serialize(self, objList: list[Model]) -> list[dict]:

        result = []
        for obj in objList:
            result.append(self.get_dump_object(obj))

        return result


class DataUserStorySerializer(DataSerializer):
    """Custom serializer for DataUserStory.
    Hide meeting_id and dont return the key from DataUserStory but rather the per_meeting_id of DataUserStory
    """
    def get_dump_object(self, obj) -> dict:

        return {
            "id": obj.per_meeting_id,
            "shot_id": obj.shot_id.per_meeting_id,
            "role": obj.role,
            "capability": obj.capability,
            "benefit": obj.benefit
        }


class DataShotSerializer(DataSerializer):
    """Custom serializer for DataSatz.
    Hide meeting_id.
    """
    def get_dump_object(self, obj) -> dict:

        return {
            "id": obj.per_meeting_id,
            "description": obj.description,
            "frm": obj.frm,
            "to": obj.to
        }


class DataSatzSerializer(DataSerializer):
    """Custom serializer for DataSatz.
    Hide meeting_id and dont return the key from DataSatz but rather the per_meeting_id of DataSatz.
    """
    def get_dump_object(self, obj) -> dict:

        return {
            "id": obj.per_meeting_id,
            "shot_id": obj.shot_id.per_meeting_id,
            "satz": obj.satz,
        }


class DataPollSerializer(DataSerializer):
    """Custom serializer for DataPoll.
    Hide meeting_id and dont return the key from DataPoll but rather the per_meeting_id of DataPoll.
    """
    def get_dump_object(self, obj) -> dict:

        return {
            "id": obj.per_meeting_id,
            "shot_id": obj.shot_id.per_meeting_id,
            "response": obj.response,
            "active": obj.active,
            "question": obj.question,
            "options": obj.options
        }


class DataAnnotationSerializer(DataSerializer):
    """Custom serializer for DataAnnotation.
    Hide meeting_id and dont return the key from DataAnnotation but rather the per_meeting_id of DataAnnotation.
    """
    def get_dump_object(self, obj) -> dict:

        return {
            "id": obj.per_meeting_id,
            "shot_id": obj.shot_id.per_meeting_id,
            "pos": [obj.pos_x, obj.pos_y],
            "titel": obj.titel,
            "text_type": obj.text_type,
            "text": obj.text
        }
