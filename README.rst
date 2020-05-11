===============
IfxSemanticData
===============

IfxSemanticData is a Django app with models relating to semantic data that must be imported into non semantic tables in other ifx applications.


Installation
------------

1. Add ifxsemanticdata to your requirements or Dockerfile (using direct installation from git with commit hashes forces rebuild of the docker image when the package is updated)::

     RUN pip install git+https://github.com/harvardinformatics/ifxsemanticdata.git@4eae20d6046f011d8c4cb0c981bf257077c94a10


2. Add "ifxsemanticdata" to your INSTALLED_APPS before the contrib.django.admin setting

    INSTALLED_APPS = [
        'ifxsemanticdata',
        ...
    ]


Importing semantic data into the model
--------------------------------------

Create a mysqldump of your semantic data and make sure to specify the columns and no create info:
(replace semantic_database and semantic_data_table with your database and table names)::

    mysqldump --no-create-info --complete-insert @@semantic_database@@ @@semantic_data_table@@ > semantic_data_dump.sql

Copy the mysqldump into your database docker container for your app::

    docker cp semantic_data_dump.sql @@app_db_1@@:/

Then load that data into the semantic_data table created by this app::

    mysql -u @@user@@ -p @@database@@ semantic_data < semantic_data_dump.sql

Make sure to run makemigrations and migrate.


Load data from semantic_data model into your app tables
-------------------------------

  Note: these instructions assume that your application includes a model for the data in its final
  form, i.e. a Django model with fields that map to the @@semantic_type@@ being migrated.
  If this is not the case, add a model to models.py, make migrations, and run migrations.

First add any configuration details to
@@app_dir@@/@@app_name@@/ifxsemanticdata_config.py.  You can find an example
file in this repository ifxsemanticdata/ifxsemanticdata/ifxsemanticdata_config.py.example.
Here you can specify
table name changes, column name changes and functions to translate values into
foreign keys or  to meet the needs of your new tables.

Then run this management command, if since is set then only data newer than that
date will be migrated, there can be more than one thing::

    ./manage.py migrateSemanticData @@app_name@@ --thing @@semantic_type@@ --since 2019-07-01

The above will only show you what rows would be created if you actually want to
create them then add the --create option::

    ./manage.py migrateSemanticData @@app_name@@ --thing @@semantic_type@@ --since 2019-07-01  --create

