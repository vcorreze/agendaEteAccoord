Présentation
============

L'Agenda de l'été à l'Accoord est un fork de l'[Agenda du libre du Québec](https://github.com/mlhamel/agendadulibre) pour
permettre de l'adapter aux besoins d'une structure socioculturelle Nantaise
afin de publier l'ensemble de nos animations de l'été.

Plusieurs textes du site proviennent des versions d'origine. Dans les détails cette
version est une mise à jour mineure de l'agenda du libre du Québec.

Cette version est disponible sous licence GNU Affero General Public License.
C'est une licence qui est plus restritive que la GNU General Public License
dû au fait qu'elle oblige les applications accessibles via le Web à rendre leur
 code source disponible. Le code source est disponible ici. Les
icônes proviennent également du projet Tango.

L'Agendu de l'été est maintenu par l'[Accoord](https://www.accoord.fr/).

Note: La procédure d'installation a été testée sous Debian 8.

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
    $ apt-get install make gcc python-dev build-essential zlib1g-dev libpcre3 libpcre3-dev libbz2-dev libssl-dev tar unzip
    $ apt-get install libpq-dev postgresql postgresql-server-dev-9.4 postgresql-client 
    $ # Si vous souhaitez envoyer des emails depuis le serveur - https://wiki.debian.org/Postfix
    $ apt-get install postfix
    
    $ adduser agendadulibre

    $ # su - user
    $ git clone https://github.com/vcorreze/agendaEteAccoord.git
    $ cd agendaEteAccoord
    $ python bootstrap.py
    $ bin/buildout -c production.cfg -vvv

Création de la base de données PostgreSQL:

    $ # su - postgres
    $ psql
    $ postgres=# CREATE USER agendadulibre WITH PASSWORD 'agendadulibre';
    $ postgres=# CREATE DATABASE agendadulibre OWNER agendadulibre;
    $ postgres=# \q

Tester la connexion à la base de données:

    $ su - agendadulibre
    $ psql agendadulibre

Paramétrez la configuration d'accès à la base de données, la 
configuration des emails etc... :

    $ cp agenda/production.py.tpl agenda/production.py
    $ vi agenda/production.py

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

- Modifier le port dans la partie [nginx-conf] du fichier de configuration
  production.cfg et refaire tourner le buildout.

- Permettre à nginx de se binder sur les ports "low ports' avec la commande 
  suivante exécutée en root: setcap 'cap_net_bind_service=+ep' /home/agendadulibre/agendaEteAccoord/parts/nginx/sbin/nginx

- Relancer les services avec supervisorctl

- Ouvrir son navigateur à l'url suivante: http://127.0.0.1

Et pour tester localement avec le bon nom de domaine :

    $ # su - root
    $ vi /etc/hosts

et ajoutez la ligne suivante :

    127.0.0.1       agenda.accoord.fr

L'application est alors disponible à l'adresse http://agenda.accoord.fr

Le fichier de configuration
---------------------------

Il est auto-généré par le buildout à partir du template agendaEteAccoord/conf/nginx.conf.ini
et se trouve ici : /home/agendadulibre/agendaEteAccoord/etc/nginx/nginx.conf






