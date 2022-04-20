Začínáme
========

Kryptograficky zabezpečené uložiště (Kryzbu) se skládá ze 2 částí a to serveru a klienta. Komunikace probíhá ve formátu server-klient. Tento 
celek umožňuje klientům využívat vzdálené uložiště (cloud) pro ukládání svých souborů a data.

Instalace
---------

Pro instalaci zadejte do příkazové řádku.

::

    git clone https://github.com/martin-nohava/kryzbu.git
    cd kryzbu/
    pip install -r requirements.txt

Nyní máme vše připraveno a může přejít k použití.

Použití
-------

Přístup k souborům je řízen podle uživatelských účtů. Každý uživatel musí být nejprve zaregistrován na serveru.

::

    cd src/
    python kryzbu_server.py --register John aaa

Takto můžeme vytvořit nový účet se jménem `John` a heslem `aaa`.

S jiš vytvořeným uživatelským účtem můžeme server spustit.

::

    python kryzbu_server.py

V nové přikazové řádce se nyní pomocí dříve vytvořeného účtu přihlásíme do klientské aplikace.

::

    python kryzbu.py -s

Budeme vyzváni k zadání uživatelského jména a hesla. Zadáme dříve vytvořené údaje, tedy jméno `John` a heslo `aaa`. 

.. note::
    Pokud přihlášení proběhlo úspěšně, v příkazové řádce by se měla objevit hlášky oznamující úspěšné přihlášení pomocí účtu `John` (*INFO: You are now logged in as John*).

Nyní můžeme z klienta přistupovat k uložisti na serveru pomocí dostupných příkazů. Seznam aktuálně dostupných příkazů lze zjistit pomocí přepínače `\-\-help`.

::

    python kryzbu.py -h

Výstup příkazové řádky bude vypadat podobně:

::

    usage: kryzbu.py [-h] [-i] [-l] [-s] [-la] [-fk] [-V] [-u FILE [FILE ...] | -d FILE [FILE ...] | -r FILE [FILE ...]]
                [--setfolder /path/to/file]

    options:
    -h, --help            show this help message and exit
    -i, --info            show user information and client settings
    -l, --list            list available files to download
    -s, --switchusr       switch to different user account
    -la, --listall        list available files to download including additional info
    -fk, --flushkey       flush saved server public key
    -V, --version
    -u FILE [FILE ...], --upload FILE [FILE ...]
                            upload file to server
    -d FILE [FILE ...], --download FILE [FILE ...]
                            download file from server
    -r FILE [FILE ...], --remove FILE [FILE ...]
                            remove file from server
    --setfolder /path/to/file
                            set download folder

Výpis dostupných souborů
~~~~~~~~~~~~~~~~~~~~~~~~

::

    python kryzbu.py -l     # Krátký výpis
    python kryzbu.py -la    # Plný výpis


Nahrání souboru
~~~~~~~~~~~~~~~

Uživatel může nahrát soubory pomocí přepínače `\-\-upload` a uvedení jednoho nebo více souboru.

::

    python kryzbu.py -u <cesta/k/souboru> ...

.. note::
    Pro lehkost uvádění souborů je možné chtělný soubor myší přetáhnout z prohlížeče souborů do příkazové řádky. Příkazová řádka si sama načte správnou cestu k souboru.

Stažení souboru
~~~~~~~~~~~~~~~

Uživatel si může dříve nahrané soubory stáhnout pomocí přepínače `\-\-download` a uvedení jednoho nebo více názvů souborů ke stažení.

::

    python kryzbu.py -d <název_soubor> ...

Mazání souboru
~~~~~~~~~~~~~~

Uživatel může své dříve nahrané soubory ze vzdaleného uložiště smazat pomocí přepínače `\-\-remove` a uvedením jednoho nebo více názvů souborů ke smazání.

::

    python kryzbu.py -r <název_soubor> ...

.. attention::
    Při smazání prosím berte na vědomí, že soubory budou nenávratně smazány společně se všemi jejich metadaty.

Nastavení složky pro ukládání stažených souborů
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ze serveru stažené soubory jsou defaultně ukládány do lokálního systémového adresáže `Stažené soubory` na disk `C:`. Uživatel si může defaultní adresář změnit a to pomocí přepínače `\-\-setfolder` a uvedení cesty k novému adresáři.

::

    python kryzbu.py --setfolder <absolutní/cesta/k/adresáři>

