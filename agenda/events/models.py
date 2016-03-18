# -*- encoding:utf-8 -*-
#
# Copyright (C) 2009 Novopia Solutions Inc.
#
# Author: Pierre-Luc Beaudoin <pierre-luc.beaudoin@novopia.com>
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
    verbose_name = "équipement"
    #ordering = ['name'] Unneeded as cities are inserted in the required order

  name = models.CharField (max_length=200)
  region = models.ForeignKey(Region)
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
                                 help_text="""Décrivez de la manière la plus complète possible votre événement.
                                 Les balises HTML autorisées sont &lt;p&gt;, &lt;b&gt;, &lt;i&gt;, &lt;ul&gt;, &lt;ol&gt;, &lt;li&gt;, &lt;br/&gt;, &lt;a&gt;. Utilisez &lt;h3&gt; jusqu'à &lt;h5&gt; pour diviser votre texte au besoin. Merci d'utiliser ces balises pour formater la description de votre événement. <br/>
Veillez à utiliser les balises &lt;p&gt; pour formater les paragraphes, et non la balise &lt;br/&gt;.""")

  url = models.URLField(verbose_name="site web",
                        blank=True, null=True,
                        help_text="Lien direct vers une page donnant plus d'informations sur l'événement (lieu précis, horaire précis, programme précis...)")
  tags = TagField(help_text="Une liste de mots séparés par un espace. Ne pas mettre de lieu dans les tags. <br/>Exemple: python django")
  start_time = models.DateTimeField()
  end_time = models.DateTimeField(blank=True, null=True)

  submission_time = models.DateTimeField(auto_now_add=True);
  updated_time = models.DateTimeField(auto_now=True);

  venue = models.CharField(max_length=200, blank=True, null=True,
                            verbose_name="Nom de l'endroit",
                            help_text="Optionnel. Nom de l'endroit où se déroule l'événement. <br/>Exemple: Pub chez Moe")

  address = models.CharField(max_length=200, blank=True, null=True,
                             verbose_name="Adresse",
                             help_text="Adresse complète")

  city = models.ForeignKey(City, blank=True, null=True, verbose_name="Équipement")
  latitude = models.FloatField(blank=True, null=True, default=0)
  longitude = models.FloatField(blank=True, null=True, default=0)

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
  moderated = models.BooleanField(default=False)
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

post_save.connect(Event.geocode, sender=Event, dispatch_uid="geocode_event")
post_save.connect(Event.announce, sender=Event, dispatch_uid="announce_event")
