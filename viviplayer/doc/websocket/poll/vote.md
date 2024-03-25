# Cast a vote in a poll

Allows all users to cast a vote in a poll.

For now a user can't update/change their vote.

**direction**: `send to server`

**permission** : `all users`

**type** : `poll`

**cmd** : `vote`

**data** :

```json
[
    {
        "poll_id": [int],
        "data": [
            {
            "poll_id": [int],
            "vote":[
                "option_id"[int],
                "option_id"[int],
            ...
            ]
        }
    },
    ...
]
```

The option_id is equal to the index in the options array, in the [new](./new.md)/[create](./create.md) message.

If the poll is single choice only one option_id can be in the vote array.

## Example

Example for casting a vote in a single choice poll. With option_id 3. The last option in a poll with single choice and 4 options.

```json
{
    "type": "poll",
    "cmd": "vote",
    "data": [
        {
            "poll_id": 0,
            "vote":[3]
        }
    ]
}
```

One liner for copy paste.
```
{ "type": "poll", "cmd": "vote", "data": [ { "poll_id": 0, "vote":[3] } ] }
```

## Response

For a users there is no response if the vote was succesfull.
For the moderator a new [result](./result.md) message is send to view the live count for the poll.

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

