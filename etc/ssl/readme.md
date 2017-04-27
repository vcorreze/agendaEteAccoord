# etc/ssl
[fr]
Ce répertoire est destiné à accueillir la copie des certificats ssl. Ils doivent être lisibles par l'utilisateur qui lancera les services.

[en]
This directory is aimed for your certs files. They must be readable by the user who launch the services.

# Fixme
On ne peut pas faire de lien symbolique vers /etc/letsencrypt/... : nginx plante au démarrage. Copier ici les fichiers.
