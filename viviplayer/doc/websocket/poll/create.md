# Create a new poll

Allows the moderator to create a poll.

**direction**: `send to server`

**permission** : `Moderator only`

**type** : `poll`

**cmd** : `create`

**data** :

```json
[
    {
        "shot_id": [int],
        "response": "0 or 1"[int],
        "question": [string],
        "options": [
            "option 0"[string],
            "option 1"[string],
            ...
            "option n"[string],
        ]
    },
    ...
]
```

response is a int indicates if a poll is 0 singel choice or 1 multiple choice.

The option id is equal to the index in the options array.

## Example

Example for creating a single choice poll.

```json
{
    "type": "poll",
    "cmd": "create",
    "data":[
        {
            "shot_id": 0,
            "response": 0,
            "question": "Hier die Frage.",
            "options": ["A", "B", "C", "D"]
        }
    ]
}
```
A is option id 0, and D id 3.

One liner for copy paste.
```
{ "type":"poll", "cmd":"create", "data":[ { "shot_id":0, "response":0, "question":"Hier die Frage.", "options":[ "A", "B", "C", "D" ] } ] }
```

## Response

The poll gets published for all users, including the moderator himself.
With cmd [new](./new.md).

## Error Response

The error response is for the sender only.
```json
{
    "type": "poll",
    "cmd": "error",
    "data": ["Error mesage[string]"]
}
```

## Notes

