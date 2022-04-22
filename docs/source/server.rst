Server
======

.. _Server:

Server je python aplikace běžící na hostujícím zařízení naslouchající na přidělené IP adrese a PORTU. Realizuje vzdálené zabezpečené úložiště. 
Vyřizuje příchozí dotazy od `klienta <client.html>`_. Zajišťuje také registraci uživatelů, jejich autentizaci a řízení jejich přístupu. Přijímá pouze spojení zabezpečené pomocí TLS.
Server `loguje <server.html#server-loglib-module>`_ důležité probíhající události a ukládá je do souboru, kde je zajištěna jejich integrita.

server.server module
--------------------

.. automodule:: server.server
   :members:
   :show-inheritance:

server.db module
----------------
 
V modulu server.db se nachází zdrojový kód sprostředkující serveru přístup k databázím uživatelů, souborů uložených na serveru a průběžných hashů logů pro zajištění integrity těchto logů. Formát databází se používá SQLite.

server.db.User_db
~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.User_db
   :members:
   :show-inheritance:

server.db.File_index
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.File_index
   :members:
   :show-inheritance:

server.db.Hmac_index
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.Hmac_index
   :members:
   :show-inheritance:

server.loglib module
--------------------

.. autoclass:: server.loglib.Log
   :members:
   :undoc-members:
   :show-inheritance:

server.rsalib module
--------------------

.. automodule:: server.rsalib
   :members:
   :show-inheritance:
