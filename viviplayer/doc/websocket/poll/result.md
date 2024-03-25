# Return result of poll.

The server returns the result of a poll. For the moderator this message gets send everytime someone send their vote message.
For all users this messages gets send if the poll is closed.

**direction**: `receive from server`

**type** : `poll`

**cmd** : `result`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
        "response" : [int],
        "active": "true or false"[boolean],
        "question": [string],
        "result": [
           {"option": "1st voted option"[string], "count": [int]},
           {"option": "2nd voted option"[string], "count": [int]},
           ...
        ]
    },
    ...
]
```

option in data is the option as string and NOT the id.
The data is sorted by count. The option with the most votes is also first in the data array.

The format is the same as in [new](./new.md) only the options field is swapped with result.

All options of poll are returned even those with 0 votes.

## Example

Example answer of server.

```json
{
    "type": "poll",
    "cmd": "result",
    "data":[
        {
            "id": 0,
            "shot_id": 0,
            "response" : 0,
            "active": false,
            "question": "The Question.",
            "result": [
                {"option": "B", "count": 3},
                {"option": "A", "count": 2},
                {"option": "C", "count": 0},
            ]
        },
    ]
}

```

## Notes
The result message gets send to the moderator everytime a user cast their vote. This is meant to enable the moderator to see the live result of the poll. The active flag is therefore true for der moderator.

If the poll is closed by the moderator all users, also the moderator, recevie the final result with the active flag set to false.

