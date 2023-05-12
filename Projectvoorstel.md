# Projectvoorstel: Beumerverwarming
Door Wessel Beumer

## Het probleem:
Mijn vader heeft een eigen systeem gemaakt om de ventielen van de vloerverwaming aan te sturen. Dit systeem draait op een Arduino, maar omdat deze op zolder achter een schot zit, is het erg onhandig om te zien wanneer een kamer wel of niet verwarmt wordt. Het zou fijn zijn om te kunnen zien welke zones van het huis verwarmt worden en waarom.

## Verwachte gebruikers
Deze applicatie moet makkelijk gebruikt kunnen worden door iedereen in mijn huis. De applicatie moet dus simpel in gebruik zijn. Het zou het beste zijn als iedereen zonder uitleg van mij de app meteen begrijpt.

## Setting
De app hoeft alleen in mijn huis gebruikt te worden, maar het zou fijn zijn als je op iedere plek de app zou kunnen bekijken. Daarom zou het fijn zijn als deze app op een smartphone werkt. Het is dan dus belangrijk dat de interface grote klikbare elementen heeft

## Waarom dit?
Omdat mijn vader dit systeem zelf heeft gemaakt, kunnen we geen of-the-shelf interface gebruiken. Daarnaast zijn wij ook de enige met dit probleem. 

## Schetsen
(Zie grotere fotos in het zipbestand.)
![Schets van de layout/uiterlijk van de app.](/schets_voor_kleiner.png)
Met deze applicatie is het makkelijk om te zien of een zone vraag heeft en/of verwarmt wordt. Daarnaast kan het inzichten geven in de activiteit van de verwarming.
![Beschrijving van de output van de Arduino](/schets_achter_kleiner.png)
^ Dit is een schets van de output van de Arduino en hoe deze verwerkt moet worden.

## Cruciale eisen
zonder deze eigenschappen is het project niet functioneel:
- Communicatie met Arduino over Serial
- Ingest van output Arduino
- Webapp voor weergave Overzicht (welke kamers hebben vraag/verwarming) bruikbaar op smartphone in portretmodus.
- Hosten webpagina op lokaal netwerk
Ik vind het vooral de Overzichtspagina belangrijk, dus deze zal relatief snel afgemaakt moeten worden.

## Andere eisen
De lijst met cruciale eisen is kort en vrij vanzelfsprekend, maar er zijn ook een aantal nice to haves die ik ook graag zou implementeren
### Hoge prio
- Manier vinden zodat begeleiders het project na kunnen kijken terwijl de app alleen bij mij thuis toegankelijk is.
- Samenvatting per kamer -> klik op kamer, krijg details te zien. Zie schets.
- Opslaan geschiedenis -> Geeft inzichten in gedrag verwarming.
- Weergeven geschiedenis -> Je hebt weinig aan een geschiedenis als je het niet kan zien. Zie schets
- App ook bruikbaar maken op andere apparaten -> laptops; tablets in portret, landschap. Moet vooral bruikbaar zijn voor tablet in onze keuken.
- Overzicht update live, zonder dat de pagina herladen moet worden.
### Medium prio
- alleen belangrijke data behouden -> Is het echt nodig om te weten dat drie maanden geleden om 17:03:49 de badkamer verwarmd werd?
- efficiënte manier van data naar disk schrijven -> ik wil niet onnodige slijtage op mijn SSD door heel veel kleine read/writes
- Mooie animaties -> animeer bv. overgangen. Misschien versie zonder animaties voor zwakke apparaten?
### Lage prio
Deze eisen zijn misschien lastig en kunnen weggelaten worden als dit zo is.
- two-way communicatie -> geef de Arduino direct commando's om te verwarmen/stoppen, programma op Arduino moet hiervoor worden aangepast
- integratie met warmtepomp/Homie -> zie in de app hoeveel de warmtepomp verbruikt, of hij verwarmt of koelt, integratie met smarthomesysteem (ik weet nog niet waarvoor maar we zien wel)
- Easter eggs (cruciaal)

## Ingrediënten
gegevensbronnen:
- [Serial Communication between Python and Arduino](https://www.hackster.io/ansh2919/serial-communication-between-python-and-arduino-e7cce0)
- de afgelopen lessen van het programmeerproject.

externe componenten:
- [flask](https://flask.palletsprojects.com/en/2.2.x/) en bijbehorenden, zoals flask.sqlalchemy
- [pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html) voor communicatie tussen server en Arduino
- [bootstrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/) waarschijnlijk ook wel
- geen idee welke, maar een externe library voor het maken van de 3D elementen in mijn overzichtspagina.
- [fontawesome](https://fontawesome.com/) voor icoontjes

## Mogelijke moeilijkheiden
Ik weet niet hoe moeilijk het is om de 3D weegave die ik wil te maken. Voor de rest zie ik geen cruciale dingen die erg moeilijk zullen zijn. 