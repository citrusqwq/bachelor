# Update poll

The server updates the shot_id of the poll.

**direction**: `receive from server`

**type** : `poll`

**cmd** : `update`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
    },
    ...
]
```

## Example

In this message the server updates the shot_id to 10 of the poll with id 0.

```json
{
    "type": "poll",
    "cmd": "update",
    "data":[
        {
            "id": 0,
            "shot_id": 10
        }
    ]
}
```

## Notes

