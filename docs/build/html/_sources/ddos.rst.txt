Mitigace DDoS
=============

Níže popsané metody mitigace DDoS útoku jsou pouze návrhy ke zmírnění nebo znemožnení
těchto útoků, tyto návrhy nebyly nijak implementovány ani testovány na tomto projektu.
Návrhy také neberou ohled na to zda by se v současném stavu kódu daly uskutečnit nebo
by bylo nutné logiku kódu předělat.

**1) Omezení počtu připojených uživatelů**

V závislosti na tom kolik uživatelů by aktivně využívalo toto uložiště by byl nastaven
maximální počet uživatelů, kteří mohou být v jednu chvíli připojeni k serveru. Tím by byla
zaručena minimální rychlost přenosu dat a zajištěno, že server nebude přetížen dotazy od mnoha uživatelů.
V případě naplnění kapacity připojených uživatelů, by byly ostatní ověření uživatelé informování o tom, že
kapacita serveru je naplněna a je nutné vyčkat k uvolnění místa.

**2) Maximální doba nečinnosti**

Dobou nečinnosti se rozumí chvíle od posledního přenosu dat od uživatele nebo k uživateli, které neslouží
k udržení spojení. Po překročení maximální doby nečinnosti bude uživatel odpojen aby došlo k uvolnění
místa pro dalšího uživatele a pro uvolnění kapacity serveru čímž by se také zvýšila přenosová rychlost.

**3) Rozdělení kapacity serveru**

Aby byly všichni uživatelé obsluhování stejnou rychlostí nezávisle na okamžiku připojení nebo zadání požadavku
bude kapacita serveru rozdělena rovnoměrně podle počtu připojených uživatelů.

**4) Whitelisting**

Pro možnost připojení se k serveru bude uživatel registrován na serveru a jeho IP adresa bude na seznamu
povolených adres pro připojení. Pokusy o připojení z neregistrované IP adresy bude server aktivně blokovat.
Server také bude kontrolovat zda se nějaký uživatel nepokouší připojet vícekrát z jiných IP adres v jeden časový okamžik
v takovém případě server nepovolí vytvořit takové spojení.

**5) Obrana před ICMP útoky**

Server bude aktivně blokovat jakkékoliv ICMP pakety a to i od registrovaných uživatelů s povolenou IP adresou k připojení.
Server také nebude přijmat fragmentované pakety ať už jsou fragmentovány z jakéhokoliv důvodu.

**6) Využití firewallu a IPS**

Firewall obsahuje jednoduché procesy k blokování IP adres nebo celých protokolů, nelze ho ale využívat učinně
protože by tím mohli být ovlivněni i legitimní uživatelé.
IPS může dopředu rozeznat jednotlivé druhy útoků v případě, že má útok shodný popis s již dříve provedeným útokem.




