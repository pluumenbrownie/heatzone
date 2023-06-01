# Top 3 code:
## 1. FakeArduino
Ik vind de FakeArduino class goed bedacht. Ik had manier nodig om de arduino te 
simuleren wanneer ik niet thuis was, op een manier die er in de code identiek
eruit ziet. De FakeArduino class is misschien niet heel netjes, maar het vervult
goed deze rol.
## 2. Histogrammen voor data plotten
Om de grafieken te maken, heb ik de numpy functie histogram gebruikt. Ik neem 
genoeg data uit de database om minimaal een dag aan data te bevatten. Vervolgens
verdeelt de numpy functie alle data over een histogram met als buitengrenzen de
huidige tijd en de tijd een uur of dag geleden. Hierdoor is het mogelijk om weer
te geven wanneer de listener actief was.
## 3. Het importeren van de grafieken
De drawsvg module heeft een optie om een svg te returnen als string. Door in deze 
return de header uit te zetten, kan de resterende code rechtstreeks in een webpagina
worden gezet. Dit is een simpele manier om de grafieken te renderen.

Een beslissing om de listener en de webapp niet direct met elkaar te laten 
communiceren, maar om deze communicatie via de database te laten gaan. De 
negatieve gevolgen hiervan zijn erg beperkt; alleen wat extra reads van mijn SSD.
Deze beslissing maakte het ontwerp van de hele app echter veel eenvoudiger dan
wat ik eerst in mijn hoofd had.

Een tweede beslissing was het vermijden van het map/area element. Ik wilde dit 
element gebruiken om de kamer van mijn plattegrond klikbaar te maken, maar de 
elementen weigerden te schalen met de afbeeldingen waar ze bijhoorden. Door deze
elementen te vervangen met een svg alternatief, ging het schalen wel. Dit zorgde er
echter wel voor dat ik mijn offcanvas op een apparte pagina moest laden.