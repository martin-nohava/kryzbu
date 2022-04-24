Závěr
=====

Tato dokumentace společně se zdrojovým kódem byla vytvořena v rámci školního skupinového projektu s tématem *Zabezpečené úložiště* k předmětu MPC-KRY 
vyučovaném v letním semestru roku 2022 na univerzitě VUT v Brně. Projekt vypracovali studenti: Nohava Martin, Matuška Jakub, Kašpar Jan a Fitere Ivana.

Zadáním projektu bylo vytvoření kryptograficky zabezpečeného úložiště s možností dělení uživatelů, jejich autentizací, šifrovanou komunikací mezi 
serverem a klientem, vytváření logů a zajištění jejich integrity. Vytvořený kód zdokumentovat a popsat možnosti ochrany proti DDoS útokům.

V rámci realizace byl projekt pojmenován *Kryzbu* (KRYptograficky ZaBezpečené Úložiště). Byl vytvořen veřejný GitHub repozitář pro společný vývoj kódu a dokumentace.
Odkaz na repozitář je dostupný `zde <https://github.com/martin-nohava/kryzbu>`_. Jako programovací jazyk byl zvolen Python. Kód je rozdělen na dvě části a to na část 
`serveru <server.html>`_ a `klienta <client.html>`_. Uživatelům je vzdálené zabezpečené úložiště zprostředkováno právě klientem skrze příkazovou řádku. Klient uživatelům
dává možnost nahrání, stažení, smazání a výpis souborů na serveru. Uživatelé musí být nejprve na serveru registrováni, poté se pomocí klienta jednou přihlásí a 
klient si údaje pamatuje. Se serverem si pak automaticky vyměňuje údaje potřebné pro autentizaci. Komunikace prochází přes šifrovaný TLS kanál a tím je zajištěna 
důvěrnost komunikace mezi klientem a serverem. Server loguje důležité události jako jsou: nahrání souboru, smazání souboru, stažení souboru, registrace nového 
uživatele a snaha o neautorizovaný přístup. Logy jsou ukládány v textové formátu a pomocí HMAC je zajištěna jejich integrita. Zdrojový kód byl zdokumentován a
byla vytvořena `Začínáme <gettingStarted.html>`_ stránka, kde je popsána instalace aplikace a její použití. A v neposlední řadě byla vytvořena rešerše obecných metod 
`mitigace DDoS <ddos.html>`_ útoků.
