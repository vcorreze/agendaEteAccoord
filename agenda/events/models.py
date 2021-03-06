# -*- encoding:utf-8 -*-
#
# Copyright (C) 2009 Novopia Solutions Inc.
#
# Author: Pierre-Luc Beaudoin <pierre-luc.beaudoin@novopia.com> + contribs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings

from babel.dates import format_datetime

from agenda.tagging.fields import TagField

from agenda.events.utils import mail_submitter

from agenda.lib.string import truncated_string
from agenda.lib.geocode import GoogleMapsGeocoder
from agenda.lib.twitter import EventTweeter
from agenda.lib.bbox import boundingBox


class Region (models.Model):

  class Meta:
    verbose_name = "Quartier"
    ordering = ['name']

  id = models.PositiveSmallIntegerField(primary_key=True)
  name = models.CharField (max_length=200)
  moderator = models.ForeignKey(
      User, blank=True, null=True,
      related_name="moderated_regions"
  )


  def __unicode__ (self):
    return self.name


class City (models.Model):

  class Meta:
    verbose_name = "Équipement"
    ordering = ['name']

  name = models.CharField (max_length=200)
  region = models.ForeignKey(Region, verbose_name='Quartier', related_name='cities')
  latitude = models.FloatField ()
  longitude = models.FloatField ()
  address = models.CharField(max_length=200, blank=True, null=True,
                             verbose_name="Adresse",
                             help_text="Adresse complète")

  def __unicode__ (self):
    return self.name


class Event (models.Model):

  class Meta:
    verbose_name = "événement"

  DEFAULT_WIDTH = 0.5  # for the geolocalisation

  title = models.CharField(max_length=200, verbose_name="titre",
                           help_text="Décrivez en moins de 5 mots votre événement, sans y indiquer le lieu, la ville ou la date.")

  description = models.TextField(verbose_name="Description",
                                 blank=True, null=True,
                                 help_text="""Décrivez de la manière la plus complète possible votre événement.""")

  image = models.ImageField(verbose_name="Image",
                            upload_to='event_images',
                            blank=True, null=True,
                            help_text='')

  url = models.URLField(verbose_name="site web",
                        blank=True, null=True,
                        help_text="Lien direct vers une page donnant plus d'informations sur l'événement (lieu précis, horaire précis, programme précis...)")

  tags = TagField(help_text="Une liste de mots séparés par un espace. Ne pas mettre de lieu dans les tags. <br/>Exemple: sortie cinéma")

  start_time = models.DateTimeField()
  end_time = models.DateTimeField(blank=True, null=True)

  submission_time = models.DateTimeField(auto_now_add=True);
  updated_time = models.DateTimeField(auto_now=True);

  venue = models.CharField(max_length=200, blank=True, null=True,
                            verbose_name="Nom de l'endroit",
                            help_text="Optionnel. Nom de l'endroit où se déroule l'événement. <br/>Exemple: MQ Doulon, salle de spectacle")

  address = models.CharField(max_length=200, blank=True, null=True,
                             verbose_name="Adresse",
                             help_text="Adresse complète (avec Code Postal et Ville)")

  city = models.ForeignKey(City, blank=True, null=True,
                           verbose_name="Équipement",
                           help_text="<b>N'oubliez-pas de choisir l'équipement concerné</b>")

  latitude = models.FloatField(blank=True, null=True, default=0)
  longitude = models.FloatField(blank=True, null=True, default=0)

  # A global event is displayed in all calendars for all equipements and regions
  global_event = models.BooleanField(verbose_name="Portée globale",
                                     default=False,
                                     help_text="Un événement de portée globale sera affiché dans tous les agendas.")

  contact = models.CharField(max_length=200,
                             verbose_name="Personne ressource",
                             help_text="Entrez le nom d'une personne que les visiteurs peuvent contacter pour plus d'information")

  contact_email = models.EmailField(max_length=200,
                                    verbose_name="Courriel de cette personne",
                                    help_text="Entrez le courriel de la personne ressource")

  twitter = models.BooleanField(default=True,
                                verbose_name="Publier sur Twitter",
                                help_text="Voulez-vous que l'Agenda publie votre événement sur Twitter?")

  moderator = models.ForeignKey(User, blank=True, null=True, related_name="moderated_events")

  moderated = models.BooleanField(default=True)
  announced = models.BooleanField(default=False)

  submiter_email = models.EmailField(max_length=200, verbose_name="Votre courriel",
                                     help_text="Entrez votre courriel, vous serez responsable de cette entrée dans l'Agenda. Ce courriel ne sera pas rendu public. Un modérateur pourrait avoir besoin de vous contacter.")

  def __init__(self, *args, **kwargs):
    super(Event, self).__init__(*args, **kwargs)
    self._disable_signals = False

  def __unicode__ (self):
    return self.title

  @property
  def formated_date(self):
    return format_datetime(self.start_time,
                           format=u"d MMM yyyy à HH:MM",
                           locale="fr_CA")

  @property
  def truncated_title(self):
    return truncated_string(self.title, max_width=100)

  @property
  def mention(self):
    return u"%s, le %s %s" % (self.truncated_title,
                              self.formated_date,
                              self.get_full_url())

  @property
  def bbox(self):
    return boundingBox(self.latitude, self.longitude, self.DEFAULT_WIDTH)

  def save_without_signals(self):
     self._disable_signals = True
     self.save()
     self._disable_signals = False

  def tweet(self):
      if settings.TWITTER_ENABLE:
        tweeter = EventTweeter()
        tweeter.tweet(self.mention)

  @staticmethod
  def announce(sender, instance, **kwargs):
    """ Tweet the event if needed it and wanted """
    if instance._disable_signals:
      return
    elif instance.announced:
      return
    elif not instance.moderated:
      return
    if instance.twitter:
      instance.tweet()
    mail_submitter(instance)
    instance.announced = True
    instance.save_without_signals()

  @staticmethod
  def geocode(sender, instance, **kwargs):
    if not instance._disable_signals:
      coder = GoogleMapsGeocoder()
      try:
        results = coder.geocode(u"%s %s" % (instance.address, instance.city.name))
      except Exception:
        return
      instance.latitude = results.get("latitude")
      instance.longitude = results.get("longitude")
      instance.save_without_signals()

  def get_full_admin_url(self):
    return "http://agenda.accoord.fr/admin/events/event/%d/" % self.id

  def get_full_url(self):
    return "http://agenda.accoord.fr%s" % self.get_absolute_url()

  def get_absolute_url (self):
    return "/event/%i/" % self.id

  @staticmethod
  def get_moderated_events(start_day, end_day, region=None, city=None):
      # Filter events for given region/city, include global events
      # !!!! start_day and end_day must be datetime.date objects

      # Filter on region and city
      if region is not None:
          if city is not None:
              q_where = Q(city__region=region, city=city)
          else:
              q_where = Q(city__region=region)
      else:
          q_where = None

      if q_where is not None:
          # We have only events for a given region (and or city)
          # Include global events, and keep only moderated events
          q = ((q_where | Q(global_event=True)) & Q(moderated=True))
      else:
          # We have events for all regions, keep only moderated events
          q = Q(moderated=True)

      # OLD filter in start_time and end_time
      #event_list = (Event.objects
      #              .filter(start_time__gte=start_day)
      #              .filter(end_time__lte=end_day)
      #              .filter(q))

      # Keep events where :
      # (1) e.start_time or e.end_time is in [start_day, end_day]
      #   => ok if the event is in the asked period
      #   => ok if the event only starts before or only ends after
      # (2) e.start_time < start_day and e.end_time > end_day
      #   => event starts before and ends after the asked period

      q_1 = (
          Q(start_time__gte=start_day) & Q(start_time__lte=end_day)
      ) | Q(
          Q(end_time__gte=start_day) & Q(end_time__lte=end_day)
      )

      q_2 = (Q(start_time__lt=start_day) & Q(end_time__gt=end_day))

      # Final query
      q = q & Q(q_1 | q_2)

      return Event.objects.filter(q).select_related('city', 'city__region').order_by('start_time')


post_save.connect(Event.geocode, sender=Event, dispatch_uid="geocode_event")
post_save.connect(Event.announce, sender=Event, dispatch_uid="announce_event")
