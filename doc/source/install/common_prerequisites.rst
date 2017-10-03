Prerequisites
-------------

Before you install and configure the eris service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``eris`` database:

     .. code-block:: none

        CREATE DATABASE eris;

   * Grant proper access to the ``eris`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON eris.* TO 'eris'@'localhost' \
          IDENTIFIED BY 'ERIS_DBPASS';
        GRANT ALL PRIVILEGES ON eris.* TO 'eris'@'%' \
          IDENTIFIED BY 'ERIS_DBPASS';

     Replace ``ERIS_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``eris`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt eris

   * Add the ``admin`` role to the ``eris`` user:

     .. code-block:: console

        $ openstack role add --project service --user eris admin

   * Create the eris service entities:

     .. code-block:: console

        $ openstack service create --name eris --description "eris" eris

#. Create the eris service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        eris public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        eris internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        eris admin http://controller:XXXX/vY/%\(tenant_id\)s
