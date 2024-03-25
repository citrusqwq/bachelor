# Push annotation

Allows the moderator to add/change an annotation.

**direction**: `send to server`

**permission** : `Moderator only`

**type** : `annotation`

**cmd** : `push`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
        "pos":[[int], [int]], // array with two ints for x and y
        "titel": [string],
        "text_type": "0 or 1"[int], //0 for text, 1 for url/link
        "text": [[string]]
    },
    ...
]
```

If the send id already exisit the annotation with the given id is overwriten with the send data.
If the id does not exisit a new annotation is created with the next available id(not the send id).

text_type indicates if the data in text is text or a url. The Backend doesn't check if text matches the text_type, it is just a hint for the Frontend to handle text and urls diffrent. In both cases the text field is a string.

## Example

Example for creating a annotation.

```json
{
    "type": "annotation",
    "cmd": "push",
    "data":[
        {
            "id": -1,
            "shot_id": 5,
            "pos": [1,1],
            "titel": "Beispiel Titel",
            "text_type": 0,
            "text": "Beispiel Text"
        }
    ]
}
```

One liner for copy paste.
```
{"type": "annotation", "cmd": "push", "data": [{"id": -1, "shot_id": 5, "pos":[1,1], "titel":"Titel", "text_type":0, "text":"Hallo"}]}
```

Example for changing annotation with id 1.

```json
{
    "type": "annotation",
    "cmd": "push",
    "data":[
        {
            "id": 1,
            "shot_id": 5,
            "pos": [1,1],
            "titel": "Geänderter Beispiel Titel",
            "text_type": 0,
            "text": "Geänderter Beispiel Text"
        }
    ]
}
```

## Response

If a new annotation is created the annotation gets published for all users, including the moderator himself.
With cmd [new](./new.md).

If an id already exisit on a push message a message with cmd [update](./update.md) is send.

## Error Response

If the annotation can't be created/updated.
The message has a wrong format.
Sender is not moderator.

The error response is for the sender only.
```json
{
    "type": "poll",
    "cmd": "error",
    "data": ["Error mesage[string]"]
}
```

## Notes

