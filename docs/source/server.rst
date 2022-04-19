Server
======

Zde bude slovní popis Serveru, co dokáže a jak to dělá.

server.server module
--------------------

.. automodule:: server.server
   :members:
   :show-inheritance:

server.db module
----------------
 
V modulu server.db se nachází zdrojový kód sprostředkující serveru přístup k databázím uživatelů, souborů uložených na serveru a průběžných hashů logů pro zajištění integrity těchto logů. Formát databází se používá SQLite.

server.db.File_index
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.File_index
   :members:
   :show-inheritance:

server.db.User_db
~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.User_db
   :members:
   :show-inheritance:

server.db.Hmac_index
~~~~~~~~~~~~~~~~~~~~

server.db.Database
~~~~~~~~~~~~~~~~~~

.. autoclass:: server.db.Database
   :members:
   :show-inheritance:

server.loglib module
--------------------

.. automodule:: server.loglib
   :members:
   :show-inheritance:

server.rsalib module
--------------------

.. automodule:: server.rsalib
   :members:
   :show-inheritance:
