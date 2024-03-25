# API

# HTTP API
TODO

Create Meeting, Video Upload, Login Moderator, Join Meeting

# Websocket API

## Client Side / Javasript

Erstmal muss der Client eine Verbindung zum Websocket des Meetings herstellen.

Die URL des Websocket ist:
```
ws://IP:PORT/ws/meeting/<meetingName>
```
In Javascript sieht das wie folgt aus:
```
var socket = new WebSocket('ws://' + window.location.host + "/ws" + window.location.pathname);

//receive
socket.onmessage = function(e) {
    var recv = JSON.parse(e.data)
    console.log(recv);
    //do things
}

//send
socket.send(<someJsonData>)
```

Dies ist das Standartformat zum senden von Daten an den Server über eine Websocket Verbindung.

```
{
	"type": "",
	"cmd": "",
	"data": []
}

```

## type
Beschreibt um welche Arte von Daten es sich handelt:
```
"type": "shot" | "userstory" | "satz" | "video" | "control"
```
Alles kleinschreiben. "type" ist case-sensitive.

## data
In "data" stehen die eigentlichen Daten.
Die Daten werden im folgenden Format gesendet oder empfangen.

### shot
```
{
	"id": 0,
	"description": "text",
	"frm": 0,
	"to": 0
}
```


### userstory
```
{
	"id": 0,
	"shot_id": 0,
	"role": "text",
	"capability": "text",
	"benefit": "text"
}

```
"shot_id" ist das "id" Feld bei shot.
"shot_id" muss exestieren.

### satz
```
{
	"id": 0,
	"shot_id": 0,
	"satz": "text"
}

```
"shot_id" ist das "id" Feld bei shot.
"shot_id" muss exestieren.

### video

```
{
   "ts": 0.0,
   "status": 0 | 1   #nur bei "cmd": "cmp"
}
```
"ts" für timestamp als float. "status" mit 0 für pausiert und 1 das video läuft gerade. "status" wird nur bei "cmp"(compare) genutzt.

### control

Hier sollen Kontroll information gesendet/empfangen werden. Wie z.B. Meeting beendet oder ein neues Video wurde hochgeladen.

TODO

## cmd
Beschreibt die Anweisung(command).
```
"cmd": "push" | "get" | "getExport"       #für "shot" | "userstory" | "satz"
"cmd"; "play" | "pause" | "skip" | "cmp"  #für "video"
```
"push" bedeutet man sendet Daten an den Server.
Hier wird die Änderung an alle Teilnehmer gesendet.

"get" und "getExport" bedeutet man möchte Daten vom Server haben.
Die Antwort wird nur an den gesendet der angefragt hat.

Alles kleinschreiben. "cmd" ist case-sensitive.

### push

Wenn bei "push" die "id" schon existiert. Werden die die Daten auf dem Server überschrieben. Dies ist gedacht zum ändern von Daten.

Wenn die "id" noch nicht exestiert werden die Daten neu gespeichert aber nicht mit der angegeben "id" sondern mit der nächstmöglichen "id".
Mehr dazu in den Beispielen.

In "data" stehen dann die Daten im oben angegebenen Format.

### get
Bei "get" kann der Client nach bestimmten ids fragen oder nach allen ids.
In "data" liegen die nachgefragten "id"
"getExport" funktioniert genau gleich wie "get" nur das die Antwort bei "getExport" cmd = "export" ist.
Bei "get" ist cmd immer "new" bei der Antwort.
```
"data": []          #für alle Daten
"data": [1,2,3]     #für z.B. id 1,2,3
```

### play
Der Sender muss Moderator sein.
Der Empfang ist für alle Teilnehmer.
"play" bedeutet der Moderator hat das Video Playback gestartet mit dem Timstamp an dem das Video gestartet wurde.

### pause
Gleiche wie "play" nur das Video wurde pausiert.

### cmp
Diese Nachricht sendet der Moderator periodisch an alle Teilnehmer.
Auch an sich selber. 
In JS kann daher der Moderator den Empfang von "cmp" ignorieren.
"cmp" beinhaltet den aktullen Timestamp des Videos und ob das Video pausiert ist oder gerade läuft.

## Server Side
Der Server Antwortet im gleichen Format.
Nur "cmd" ist anders.
### cmd
```
"cmd": "new" | "update"                    #für "shot" | "userstory" | "satz"
"cmd": "error"                             #für Fehler Nachricht an Client
"cmd": "play" | "pause" | "skip" | "cmp"   #für "video"
"cmd": "end"                               #für "control"
```
"new" wenn neue Daten hinzugefügt wurden.

"update" wenn Daten geändert worden sind.

Wenn "get" aufgerufen wurde haben alle Antworten :
> "cmd": "new"

Wichtig der Server sendet auch ohne Anfrage Daten an den Client.
Wenn z.B ein anderer Nutzer eine User Story hinzufügt wird an alle Teilnehmer diese User Story gesendet.

Bei einem error steht in "data" ein String mit der Fehlermeldung.

Type "control" signalisiert informationen an das Frontend.
Das Meeting wird beendet dadurch das der Websocket geschlossen wird und eine Nachricht vom type "control" und cmd "end" gesendet wird.

## Beispiele

Folgende Beispiel funktionieren für "shot", "userstory" und "satz".

Der Client sendet eine neue UserStory an den Server.
Wir gehen davon aus das "shot_id" schon existiert.
```
{
   "type":"userstory",
   "cmd":"push",
   "data":[
      {
         "id":-1,
         "shot_id":1,
         "role":"user",
         "capability":"idk",
         "benefit":"idk"
      }
   ]
}
```
Als Einzeiler für copy paste.
```
{ "type":"userstory", "cmd":"push", "data":[ { "id":-1, "shot_id":1, "role":"user", "capability":"idk", "benefit":"idk" } ] }
```
Antwort:
```
{
   "type":"userstory",
   "cmd":"new",
   "data":[
      {
         "id":0,
         "shot_id":1,
         "role":"user",
         "capability":"idk",
         "benefit":"idk"
      }
   ]
}

```
Diese Antwort geht an alle Teilnehmer des Meetings.

Wenn man die gleiche Nachricht nochmal sendet.

Ist die Antwort folgende.
```
{
   "type":"userStory",
   "cmd":"new",
   "data":[
      {
         "id":1,
         "shot_id":1,
         "role":"user",
         "capability":"idk",
         "benefit":"idk"
      }
   ]
}

```
Hier wurde jetzt wieder eine neu UserStory erstell diesmal mit "id" 1.
Da die gesendete "id" -1 nicht existiert wird eine nächstmögliche "id" generiert.

Eine "id" kann nur einmal existieren wenn jetzt "id" 1 gelöscht wird.
Ist die nächstmögliche "id" 3 beim neu einfügen und nicht wieder 1!

Eine UserStory die exestiert wird wie folgt geändert.
```
{
   "type":"userstory",
   "cmd":"push",
   "data":[
      {
         "id":0,
         "shot_id":1,
         "role":"user",
         "capability":"newTextHere",
         "benefit":"idk"
      }
   ]
}

```
Da "id" 0 schon exestiert wird die User Story überschrieben/geändert.

Antwort:
```
{
   "type":"userstory",
   "cmd":"update",
   "data":[
      {
         "id":1,
         "shot_id":1,
         "role":"user",
         "capability":"newTextHere",
         "benefit":"idk"
      }
   ]
}
```
Diese Antwort geht wieder an alle Teilnehmer des Meetings.

Nun ein Beispiel zur Fehler Meldung. Wir senden hier eine "shot_id" die nicht exestiert.
```
{
   "type":"userstory",
   "cmd":"push",
   "data":[
      {
         "id":1,
         "shot_id":0,
         "role":"user",
         "capability":"newText",
         "benefit":"idk"
      }
   ]
}
```
Antwort:
```
{
   "type":"userstory",
   "cmd":"error",
   "data":[
      "invalid or missing shot_id"
   ]
}
```
Die Fehler Meldung geht nur an den Sender und nicht an alle Teilnehmer.

Gleiche passiert auch wenn nicht alle Felder vorhanden sind. Oder ein "type" gesendet wurde der nicht valide ist.
Die Fehler Nachricht steht immer als String in "data".

Ein Beispiel zu "get".
```
{
   "type":"userstory",
   "cmd":"get",
   "data":[
      0
   ]
}
```
Für copy paste
```
{ "type":"userstory", "cmd":"get", "data":[0] }
```

Antwort:
```
{
   "type":"userstory",
   "cmd":"new",
   "data":[
      {
         "id":0,
         "shot_id":1,
         "role":"user",
         "capability":"idk",
         "benefit":"idk"
      }
   ]
}
```
Nach "get" ist "cmd" immer "new".
Die Antwort geht nur an den Sender.

Für alle UserStorys auf dem Server, zum Meeting.
```
{ "type":"userstory", "cmd":"get", "data":[] }
```
Antwort:
```
{
   "type":"userstory",
   "cmd":"new",
   "data":[
      {
         "id":0,
         "shot_id":1,
         "role":"user",
         "capability":"idk",
         "benefit":"idk"
      },
      {
         "id":1,
         "shot_id":1,
         "role":"user",
         "capability":"newTextHere",
         "benefit":"idk"
      }
   ]
}
```

Nun Beispiele für den Video Player.
Diese Nachricht sendet der Moderator an den Websocket.
Die Antwort sieht genau so aus und wird an alle Teilnehmer inklusive dem Moderator gesendet. "pause" sieht genau so aus.
```
{
   "type":"video",
   "cmd":"play",
   "data":[
      {
         "ts":3.568
      }
   ]
}
```

Zum synchronisieren der Teilnehmer muss der Moderator eine "cmp" Nachricht periodisch an alle Teilnehmer senden.
Die Nachricht wird genau so wie "play" und "pause" an alle Teilnehmer gesendet.
Daher kann der Moderator diese Nachricht beim Empfang ignorieren da er sie ja selber gesendet hat.
Folgende Nachricht bedeutet, das aktuelle Video ist pausiert bei Sekunde 3.568.
Wenn das Video abgespielt wird wäre dann "status" 1 und der timestamp aktualisiert sich vortlaufend.
```
{
   "type":"video",
   "cmd":"cmp",
   "data":[
      {
         "ts":3.568,
         "status":0
      }
   ]
}
```
Für JS kann das senden der "cmp" Nachricht wie folgt gestaltet werden.
```
function SendCompare() {
   //send current time and status
}

//start function with timer of 5 sec
var myInterval = setInterval(everyTime, 5000);

//stop function
clearInterval(myInterval);
```

Das End des Meetings wird wie folgt, vom Server, signalisiert.
```
{
   "type":"control",
   "cmd":"end",
   "data":[]
}

```

## Hinweise

Beim Video upload werden automatisch die Scene erkannt.
Wenn PySceneDetect fertig ist werden alle Shots mittels einer Nachricht mit "type": "shots" und "cmd": "new" an das Frontend, über den Websocket, gesendet.
Dies kann zwischen 0-30 Sekunden dauern.



Wenn pyscene zu schnell ist kann es vorkommen das der Client noch nicht über einen Websocket verbunden ist wenn der Server die neuen Daten zum Client senden möchte.
Daher nach jedem Aufruf der Meeting Website mit "get" überprüfen ob schon Daten vorhanden sind.

Idee: Init function in JS die erstmal "get" für alle Datentypen aufruft.
Um das Meeting zu Synchronisieren.