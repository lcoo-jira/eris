2. Edit the ``/etc/eris/eris.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://eris:ERIS_DBPASS@controller/eris
