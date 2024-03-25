# Return poll

The server returns a poll.

**direction**: `receive from server`

**type** : `poll`

**cmd** : `new`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
        "response": "0 or 1"[int],
        "active": "true or false"[boolean],
        "question": [string],
        "options": [
            "choice 0"[string],
            "option 1"[string],
            ...
            "option n"[string],
        ]
    },
    ...
]
```

response is a int indicates if a poll is 0 singel choice or 1 multiple choice.

id is a unique id given to the poll by the server. For future requests i.e. voting the poll is identified with this id.

The option id is equal to the index in the options array.

## Example

Example answer of server.

```json
{
    "type": "poll",
    "cmd": "new",
    "data":[
        {
            "id": 0,
            "shot_id": 0,
            "response": "single",
            "active": true,
            "question": "Hier die Frage.",
            "options": ["A", "B", "C", "D"]
        }
    ]
}
```
A is option id 0, and D id 3.

## Notes

