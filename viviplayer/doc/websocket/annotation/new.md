# Return annotation

The server returns a new annotation.

**direction**: `receive from server`

**type** : `annotation`

**cmd** : `new`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
        "pos":[[int], [int]], // array with two ints for x and y
        "titel": [string],
        "text_type": "0 or 1"[int], //0 for text, 1 for url/link
        "text": [[string]]
    },
    ...
]
```

## Example

Example answer of server.

```json
{
    "type": "annotation",
    "cmd": "new",
    "data":[
         {
            "id": 1,
            "shot_id": 5,
            "pos": [1,1],
            "titel": "Beispiel Titel",
            "text_type": 0,
            "text": "Beispiel Text"
        }
    ]
}
```

## Notes

A new annotation has always the next available id starting with 0.
A id is never changed or used twice.