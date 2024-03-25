# Return annotation

The server returns a updated annotation.

**direction**: `receive from server`

**type** : `annotation`

**cmd** : `update`

**data** :

```json
[
    {
        "id": [int],
        "shot_id": [int],
        "pos":[[int], [int]], // array with two ints for x and y
        "text_type": "0 or 1"[int], //0 for text, 1 for url/link
        "text": [[string]]
    },
    ...
]
```

## Example

Example answer of server if the id in push already exisits.

```json
{
    "type": "annotation",
    "cmd": "update",
    "data":[
         {
            "id": 1,
            "shot_id": 5,
            "pos": [1,1],
            "text_type": 0,
            "text": "Geänderter Beispiel Text"
        }
    ]
}
```

## Notes
