Úvod
====

Zabezpečené ukladanie údajov súhrnne označuje manuálne alebo automatizované výpočtové procesy a technológie používané na zaistenie bezpečnosti a integrity uložených údajov. 
Táto ochrana môže byť aplikovaná ako ochrana fyzická napríklad fyzickou ochranou hardvéru, na ktorom sú dáta uložené, ako aj použitím zabezpečeného softvéru. 
Používanie vzdialených úložišť sa v poslednom desaťročí rozšírilo takmer na každého užívateľa. Tieto dáta, ktoré putujú od užívateľa až k úložisku,
na ktorom sú následne uložené sú vystavené hrozbám. Táto technika má za potrebu zaistiť užívateľovi spoľahlivú službu a to zaistením jej integrity, 
dôveryhodnosti dát a dostupnosti. Pri nesprávnom overovaní vstupov, je útočník schopný zostaviť vstup vo forme, ktorá sa od zvyšku
aplikácie neočakáva. Toto chovanie môže viesť k tomu, že sa v častiach systému objavia vstupy, ktoré vedia spôsobiť neprajné následky ako zmenený tok riadenia, 
svojvoľné riadenie zdroja alebo vykonávanie ľubovoľného kódu.

Ako sa teda týmto hrozbám vyvarovať môže byť zhrnuté do pár hlavných bodov:

* Šifrovanie údajov
* Access control- mechanizmus kontroly prístupu na každom zariadení alebo softvéri na ukladanie údajov
* Ochrana dát pred poškodením- ochrana pred vírusmi, červami a inými úmyselnými hrozbami
* Fyzická bezpečnosť- bezpečnosť fyzického alebo akékoľvek obsadeného úložného zariadenia a jeho infraštruktúry

Pri hľadaní slabín na bezpečnom úložisku je jednou z najdôležitejších skutočností si všimnúť a overiť
všetky možné formy vstupov jednotlivých užívateľov. Ak sa prvotne zabráni užívateľom so zlým
úmyslom pristupovať k útočným reťazcom, ľahko sa zmierni drvivá väčšina hrozieb. Ošetrenie
jednotlivých slabín môže zmenšiť útočnú plochu a minimalizovať dopad úspešných útokov.

**Dostupnosť** - v kontexte bezpečnosti ukladania údajov dostupnosť znamená minimalizáciu rizika, že
sa zdroje úložiska zničia alebo zneprístupnia buď úmyselne napríklad pomocou DDoS útoku alebo
náhodne v dôsledku prírodnej katastrofy, výpadku napájania alebo iného mechanického zlyhania.
Dôveryhodnosť- udržiavanie údajov v tajnosti zabezpečením toho, že k nim nemajú prístup
neoprávnené osoby ani cez sieť, ani lokálne, je kľúčovým princípom zabezpečenia úložiska na
predchádzanie narušeniu údajov.

**Integrita** - integrita údajov v kontexte bezpečnosti ukladania údajov znamená zabezpečenie, že s
údajmi nemožno manipulovať ani ich zmeniť.

Ciele projektu
==============

Pre aplikáciu symetrickej a asymetrickej kryptografie bude použitá kryptografická Python knižnica s
názvom PyCryptodome. Táto knižnica umožňuje využiť radu rôznych funkcií ako režimy overeného
šifrovania (GSM, CCM), kryptografiu nad eliptickými krivkami, hashovacie algoritmy (SHA-3, BLAKE2)
alebo prúdové šifry. Okrem zabezpečenia dát sa do projektu implementuje aj nutná autentizácia
užívateľa pred prístupom k samotným dátam. Tento užívateľ sa bude môcť autentizovať či už
využitím symetrických alebo asymetrických algoritmov implementovaných v projekte.


Vývojový diagram
================

.. figure:: ../../graphics/vyvojovy-diagram.svg
   :width: 100%
