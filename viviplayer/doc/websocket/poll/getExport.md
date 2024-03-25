# Get poll but as export

Allows all users to get a specific poll or all polls for export.

**direction**: `send to server`

**permission** : `all users`

**type** : `poll`

**cmd** : `getExport`

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
    "cmd": "getExport",
    "data":[]
}
```

Example of requesting poll id 0 and 1.

```json
{
    "type": "poll",
    "cmd": "getExport",
    "data":[0,1]
}
```

## Response

The answer is cmd "export", in the same format as [new](./new.md), and cmd "exportResult", in same format as [result](./result.md), but only for the requesting user and not all members of the meeting.

## Error Response

The server doesn't return an error message. 
If the id is not available, data is a empty array in [export](./new.md).


## Notes
If there is no result available for the user, no message with cmd "resultExport" is send.

