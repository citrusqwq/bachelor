# Close poll

This message is for the moderator to close a poll and signal for all users that a poll was closed.

!! The message to the server looks **different** than the message from the server.

**direction**: `send to`

**permission** : `Moderator only`

**type** : `poll`

**cmd** : `close`

**data** :

```json
[
    {
        "id": [int],
        "publish": [bool]
    }
]
```

The id of the poll to close and if the poll should be published for everyone or should be kept secret for the moderator.

If you receive from the server:

**direction**: `receive from server`

**type** : `poll`

**cmd** : `close`

**data** :

```json
[[int]]
```

## Example

This closes poll 0 if send my moderator to server.

```json
{
    "type": "poll",
    "cmd": "close",
    "data":[
        {
        "id": 0,
        "publish": true
        }
    ]
}
```

## Response

The server returns this messsage for all users to indicate that poll 0 was closed.

```json
{
    "type": "poll",
    "cmd": "close",
    "data":[0]
}

```

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

