# Delete annotation

This message is for the moderator to delete an annotation and signal for all users that a annotation was deleted. 

**direction**: `send to server`

**permission** : `Moderator only`

**type** : `annotation`

**cmd** : `del`

**data** :

```json
[[int]]
```

This is just a array with a singel id of the annotation.

## Example

This deletes annotation 0.

```json
{
    "type": "annotation",
    "cmd": "del",
    "data":[0]
}
```

## Response

All users, including the moderator, receive the cmd del message.

**direction**: `receive from server`

**type** : `annotation`

**cmd** : `del`

**data** :

```json
{
    "id": [int],
    "shot_id": [int]
}
```

## Example

This is the answer after the del message got send by the moderator. 

```json
{
    "type": "annotation",
    "cmd": "del",
    "data": {
        "id": 0,
        "shot_id": 5
    }
}
```

## Error Response

Returns error message if annotation can't be deleted(sender is not moderator, id does not exists, wrong format).

The error response is for the sender only.
```json
{
    "type": "annotation",
    "cmd": "error",
    "data": ["Error mesage[string]"]
}
```

## Notes

