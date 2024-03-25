# Get annotation

Allows all users to get a specific annotation or all annotation.

**direction**: `send to server`

**permission** : `all users`

**type** : `annotation`

**cmd** : `get`

**data** :

```json
[[int],...]
```

In the data array are the id's of the annotation the sender wants.
The data array can be empty. This returns all available annotations.

## Example

Example of requesting all polls.

```json
{
    "type": "annotation",
    "cmd": "get",
    "data":[]
}
```

Example of requesting poll id 0 and 1.

```json
{
    "type": "annotation",
    "cmd": "get",
    "data":[0,1]
}
```

## Response

The answer is cmd [new](./new.md) but only for the requesting user and not all members of the meeting.

## Error Response

For every id that is not found an error message is send.

If all annotations are requested(empty array) and there is no data saved no message is send.

The error response is for the sender only.
```json
{
    "type": "annotation",
    "cmd": "error",
    "data": ["Error mesage[string]"]
}
```

## Notes

