Met behulp van Otto de Jong en Nina van der Meulen.


## Meer uitleg en/of comments
Er is mij aanbevolen om meer comments toe te voegen. Ook moet ik beter uitleggen 
hoe ik dingen heb gedaan en waarom. Het was voor anderen moeilijk te begrijpen 
hoe mijn code in elkaar zit. Meer comments toevoegen zou hier veel bij helpen.

```
@app.route("/_get_status")
def get_status() -> str:
    with engine.begin() as db:
        output = db.execute(
            sql.text("SELECT * FROM direct_history ORDER BY timecode DESC LIMIT 1")
        ).first()
    dictionary: dict[str, str | int | bool] = {}

    if not output:
        return "error"

    for name, value in zip(COLUMN_NAMES, output):
        dictionary[name] = value

    add_colors_to_dict(dictionary)
    dictionary.update(
        {
            "ground_floor_name": "Ground floor",
            "bathroom_name": "Bathroom",
            "blue_room_name": "Blue room",
            "j_bedroom_name": "J bedroom",
            "km_bedroom_name": "KM bedroom",
            "top_floor_name": "Top floor",
        }
    )
    dictionary["timecode"] = time.strftime(
        "%H:%M:%S %d-%m-%Y", time.localtime(float(dictionary["timecode"]) / 10)
    ).__str__()

    return json.dumps(dictionary)
```
Het is hier niet duidelijk wat deze code hoort te doen. Hier is een voorbeeld van 
de code met commments:
```
@app.route("/_get_status")
def get_status() -> str:
    with engine.begin() as db:
        # select the db entry with the highest value for 'timecode'
        output = db.execute(
            sql.text("SELECT * FROM direct_history ORDER BY timecode DESC LIMIT 1")
        ).first()
    dictionary: dict[str, str | int | bool] = {}

    # the db query might fail when it is empty
    if not output:
        return "error"

    # treat 'output' like a tuple and add it's entries to a dict
    for name, value in zip(COLUMN_NAMES, output):
        dictionary[name] = value

    add_colors_to_dict(dictionary)
    # add the displaynames of the rooms to the dict
    dictionary.update(
        {
            "ground_floor_name": "Ground floor",
            "bathroom_name": "Bathroom",
            "blue_room_name": "Blue room",
            "j_bedroom_name": "J bedroom",
            "km_bedroom_name": "KM bedroom",
            "top_floor_name": "Top floor",
        }
    )
    # add a pretty formatted version of the timecode to the dict
    dictionary["timecode"] = time.strftime(
        "%H:%M:%S %d-%m-%Y", time.localtime(float(dictionary["timecode"]) / 10)
    ).__str__()

    # return the dict as a str in json format
    return json.dumps(dictionary)
```

## Js in appart bestand
De javascript van alle webpagina's bestaat nu in embedded `<script>`-tags. Dit 
zorgt ervoor dat deze pagina's onoverzichtelijk en verwarrend zijn. Het project
zou een stuk overzichtelijker worden als deze code in zijn eigen bestand zou 
leven en bovenaan de pagina geïmorteerd werd. Dit zou echter veel tijd en moeite
kosten, door de manier waarop ik Jinja heb gebruikt. De `canvas.html` pagina 
breidt de `index.html` pagina uit in meerdere plekken, zoals het `offcanvas_script` 
block:
```
<script>
    const loc = document.location;
    var ground_floor = document.getElementById("Ground floor");
    var bathroom = document.getElementById("Bathroom");
    var blue_room = document.getElementById("Blue room");
    var j_bedroom = document.getElementById("J bedroom");
    var km_bedroom = document.getElementById("KM bedroom");
    var top_floor = document.getElementById("Top floor");
    var time_text = document.getElementById("time");
    var link = document.getElementById("overview_link");
    link.classList.add("active");
    let ip = loc.origin + "/_get_status";
    console.log(ip);
    {% block offcanvas_script %}{% endblock %}
    runUpdate();
    setInterval(runUpdate, 1000);
```
Om de javascript in een appart bestand te zetten, moet dit hele systeem herdacht
worden. 

## Voorbeeld van de data in de docstring van functie
Het is nu niet duidelijk hoe de data die functies gebruiken of teruggeven eruit
zien. Dit kan verhelderd worden door ergens een voorbeeld van de data te plaatsen,
bij de code zelf of in de `README.md`. Zo zou ik het volgende voorbeeld toe kunnen
voegen voor de `listener.py`:
```
b''
b''
b''
b''
b''
b''
b''
b'66'
b'28'
b'25'
b'19'
b'31'
b'40'
b'[Therm 0]:0 [Therm 1]:0 [Therm 2]:0 [Therm 3]:0 [Therm 4]:0 [Therm 5]:0Actual on:0'
b'0'
b'[0] on:0s, off in 600s'
b'[1] on:0s, off in 600s'
b'[2] on:0s, off in 600s'
b'[3] on:0s, off in 600s'
b'[4] on:0s, off in 600s'
b'[5] on:0s, off in 600s'
```
Hierdoor is het duidelijker waar de functie mee werkt. Als dit in de code zelf
gedaan wordt, zou het echter onoverzichtelijk kunnen worden.

## Meer code in functies stoppen
Code in functies stoppen kan ook de leesbaarheid van de code verbeteren. Dit kan 
er echter ook voor zorgen dat je tijdens het lezen de hele tijd van plek moet 
verspringen, wat weer verwarrend kan zijn. Er moet een afweging gemaakt worden of
een functie of een comment de code duidelijker kan maken.

## Verplaats meer functies naar een helpers.py bestand
In mijn `app.py` zitten ook functies die niet direct webpagina's laden, maar wel 
alleen daar nodig zijn, zoals `determine_color()`. Ik werd aanbevolen om deze 
functies naar een `helpers.py` bestand te verplaatsen. Functies verplaatsen naar 
een appart bestand kan de leesbaarheid van de code verbeteren, maar het kan ook 
verwarrend zijn voor mensen die niet weten hoe je project in elkaar zit. 