# Get poll

Allows all users to get a specific poll or all polls.

**direction**: `send to server`

**permission** : `all users`

**type** : `poll`

**cmd** : `get`

**data** :

```json
[[int],...]
```

In the data array are the id's of the polls the sender wants.
The data array can be empty. This returns all available polls.

## Example

Example of requesting all polls.

```json
{
    "type": "poll",
    "cmd": "get",
    "data":[]
}
```

Example of requesting poll id 0 and 1.

```json
{
    "type": "poll",
    "cmd": "get",
    "data":[0,1]
}
```

## Response

The answer is cmd [new](./new.md) and [result](./result.md) but only for the requesting user and not all members of the meeting.

## Error Response

For every id that is not found an error message is send.

If all polls are requested(empty array) and there is no data saved no message is send(new and result).

## Notes

