# -*- encoding:utf-8 -*-

import csv

from django.core.management.base import BaseCommand, CommandError

from agenda.events.models import City, Region


class Command(BaseCommand):
    help = u'Import des équipements depuis un fichier CSV'

    # Usage example: bin/django import_equipements /home/agendadulibre/ListeEquipements.csv

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, file_path, *args, **options):

        # Lecture du fichier CSV
        try:
            reader = csv.reader(open(file_path, 'rb'))
            rows = list(reader)
        except IOError:
            self.stderr.write(u'Fichier non trouvé')
            return
        except csv.Error:
            self.stderr.write(u'Erreur inconnue lors de la lecture du fichier')
            return

        expected_colums = ['Nom', 'Adresse', 'Adresse Alt.', 'CP', 'Ville', 'Lat', 'Long', 'Grand Quartier']
        if not rows or rows[0] != expected_colums:
            self.stderr.write(u'Les colonnes attendues sont : {}'.format(expected_colums))
            return

        headers, equipments = rows[0], rows[1:]

        # Id du dernier quartier en base
        last_quartier = Region.objects.order_by('pk').last()
        if last_quartier is not None:
            next_quartier_id = last_quartier.pk + 1
        else:
            next_quartier_id = 0

        # Création des quartiers et des équipements
        for eq in equipments:
            eq_nom = eq[0]
            eq_adresse_ligne1 = eq[1]
            eq_adresse_ligne2 = eq[2]
            eq_cp = eq[3]
            eq_ville = eq[4]
            eq_lat = float(eq[5].replace(',', '.'))
            eq_long = float(eq[6].replace(',', '.'))
            eq_quartier = eq[7]

            adresse_parts = []
            if eq_adresse_ligne1: adresse_parts.append(eq_adresse_ligne1)
            if eq_adresse_ligne2: adresse_parts.append(eq_adresse_ligne2)
            adresse_parts.append('{} {}'.format(eq_cp, eq_ville))
            eq_adresse = ', '.join(adresse_parts)

            # Création du quartier (région)
            try:
                quartier = Region.objects.get(name=eq_quartier)
            except Region.DoesNotExist:
                quartier = Region(
                    name = eq_quartier,
                    id = next_quartier_id
                )
                quartier.save()
                next_quartier_id += 1

            # Création de l'équipement (city)
            eq = City(
                name=eq_nom,
                region=quartier,
                latitude=eq_lat,
                longitude=eq_long,
                address=eq_adresse
            )
            eq.save()

        self.stdout.write('Successfully imported.')
