# Installation

Développement : installation du projet
======================================

Pour installer l'Agenda de l'été, vous n'avez qu'à suivre les différentes
étapes suivantes. (Prérequis: Python 2.7.x, git, sqlite3) :

    $ # su - root
    $ apt-get install git sqlite3

    $ # su - <user>
    $ cd <projet-dir>
    $ git clone https://github.com/vcorreze/agendaEteAccoord.git
    $ cd agendaEteAccoord
    $ python bootstrap.py
    $ bin/buildout -c development.cfg -vvv
    
Les dépendances seront téléchargées et installées dans le répertoire courant.

Paramétrez la configuration d'accès à la base de données, la
configuration des emails etc... :

    $ cp agenda/development.py.tpl agenda/development.py
    $ vi agenda/development.py

Ensuite vous n'avez qu'à initialiser la base de données (SQLite en
développement):

    $ bin/django syncdb
    $ bin/django migrate

Et importer les données relatives aux équipements (le fichier attendu
en entrée doit être au format CSV et contenir une première ligne
d'entêtes avec les noms suivants : 'Nom', 'Adresse', 'Adresse Alt.',
'CP', 'Ville', 'Lat', 'Long', 'Grand Quartier') :

    $ bin/django import_equipements /where/you/want/ListeEquipements.csv

Et voilà, et pour lancer l'agenda:

   $ bin/django runserver 127.0.0.1:8000

Vous n'avez qu'à ouvrir l'url suivante: http://127.0.0.1:8000 dans votre
navigateur !

Production : installation du projet
===================================

Pour installer l'Agenda du libre en production, on vous conseille de ne pas
utiliser SQLite3 car ce n'est pas une base de données très robuste pour un
site web multi-usager. Nous avons donc choisit PostgreSQL afin de faire tourner
l'agenda en production (cf. https://wiki.debian.org/PostgreSql).

Pour installer l'agenda en production il suffit de spécifier à buildout
d'utiliser la configuration de production. Le tout compilera localement une
version de nginx et de uwsgi qui serviront l'agenda.

Vous n'avez donc qu'à suivre les étapes suivantes:

    $ # su - root
    $ apt-get install make gcc python-dev build-essential zlib1g-dev libpcre3 libpcre3-dev libbz2-dev libssl-dev tar unzip libjpeg-dev
    $ apt-get install libpq-dev postgresql postgresql-server-dev-9.4 postgresql-client
    $ # Si vous souhaitez envoyer des emails depuis le serveur - https://wiki.debian.org/Postfix
    $ apt-get install postfix

    $ adduser agenda

    $ # su - agenda
    $ git clone https://github.com/vcorreze/agendaEteAccoord.git
    $ cd agendaEteAccoord
    $ python bootstrap.py
    $ bin/buildout -c production.cfg -vvv

Création de la base de données PostgreSQL:

    $ # su - postgres
    $ psql
    $ postgres=# CREATE USER agenda WITH PASSWORD 'agenda';
    $ postgres=# CREATE DATABASE agenda OWNER agenda;
    $ postgres=# \q

Tester la connexion à la base de données:

    $ su - agenda
    $ psql agenda

Paramétrez la configuration d'accès à la base de données, la
configuration des emails etc... :

    $ cp agenda/production.py.tpl agenda/production.py
    $ vim agenda/production.py

Vous devez encore une fois initialiser la base de données:

!! Attention : La base de données doit déjà être créée dans PostgreSQL.

    $ bin/django syncdb
    $ bin/django migrate

Et importer les données relatives aux équipements (le fichier attendu
en entrée doit être au format CSV et contenir une première ligne
d'entêtes avec les noms suivants : 'Nom', 'Adresse', 'Adresse Alt.',
'CP', 'Ville', 'Lat', 'Long', 'Grand Quartier') :

    $ bin/django import_equipements /where/you/want/ListeEquipements.csv

Pour lancer les services (nginx, uwsgi/django):

    $ bin/supervisord

Vous pouvez toujours vous connecter à supervisor afin d'avoir plus de détails
et intéragir sur les processus, exemples:

    $ bin/supervisorctl
    supervisor> status
    nginx  RUNNING  ...
    uwsgi  RUNNING  ...
    supervisor> restart nginx
    nginx: stopped
    nginx: started
    supervisor> stop nginx
    nginx: stopped
    supervisor> start nginx
    nginx: started
    supervisor> help
    ...

Vous n'avez qu'à ouvrir l'url suivante: http://127.0.0.1:8080 dans votre
navigateur !

Production : nginx
==================

Écouter sur le port 80
----------------------

nginx est configuré pour écouter sur le port 8080. Si vous souhaitez qu'il
écoute sur le port 80 il faut :

- Modifier le port dans la partie `[nginx-conf]` du fichier de configuration
  `production.cfg` et refaire tourner le buildout.

- Permettre à nginx de se binder sur les ports "low ports' avec la commande
  suivante exécutée en root: `setcap 'cap_net_bind_service=+ep' /home/agenda/agendaEteAccoord/parts/nginx/sbin/nginx`

- Relancer les services avec supervisorctl

- Ouvrir son navigateur à l'url suivante: http://127.0.0.1

Et pour tester localement avec le bon nom de domaine :

    $ # su - root
    $ vi /etc/hosts

et ajoutez la ligne suivante :

    127.0.0.1       agenda.mydomain.fr

L'application est alors disponible à l'adresse http://agenda.mydomain.fr

Le fichier de configuration
---------------------------

Il est auto-généré par le buildout à partir du template `agendaEteAccoord/conf/nginx.conf.ini`
et se trouve ici : `${buidout:directory}/etc/nginx/nginx.conf`

SSL
===

Le template de paramétrage du serveur nginx est prévu pour utiliser SSL.

Une utilisation simplifiée de SSL est possible avec le programme `certbot`.

Pour l'installer (sous debian jessie - YMMV) il faut :

1. Ajouter les backports (ajouter une ligne `deb http://ftp.debian.org/debian jessie-backports main` dans un fichier `/etc/apt/sources.list.d/backports.list`)

2. Installer certbot : `apt-get update && apt-get dist-upgrade && apt-get install certbot -t jessie-backports`

3. Obtenir un certificat : `certbot certonly --standalone -d agenda.MyDomain.fr`. Il faut pour cela que le port 80 soit disponible

4. Générer un fichier `dhparam.pem` avec la commande `openssl dhparam -out ${buidout:directory}/etc/ssl/dhparam.pem 2048`

5. copier les fichiers du certificat dans le répertoire `${buidout:directory}/etc/ssl/` et leur donner les droits de l'utilisateur agenda.

6. démarrer ou redémarrer nginx (avec supervisorctl).

URis
====

Les 3 URis utiles sont :
- https://agenda.MyDomain.fr
- https://agenda.MyDomain.fr/admin/
- https://agenda.MyDomain.fr/login/

:sparkles:
