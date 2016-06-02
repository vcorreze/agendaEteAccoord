# -*- coding: utf-8 -*-
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

from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.utils.feedgenerator import Rss201rev2Feed
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.utils.encoding import smart_unicode, force_unicode, smart_str

from agenda.events.models import Event, Region

from datetime import date, timedelta

import vobject
import re
import locale


def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

EVENT_ITEMS = (
    ('uid', 'uid'),
    ('dtstart', 'start'),
    ('dtend', 'end'),
    ('summary', 'summary'),
    ('url', 'url'),
    ('description', 'description'),
    ('location', 'location'),
    ('last_modified', 'last_modified'),
    ('created', 'created'),
)


class ICalendarFeed(object):

    def __call__(self, *args, **kwargs):
        response = HttpResponse()

        cal = vobject.iCalendar()
        cal.add('X-WR-CALNAME').value = getattr(self, "name")()
        cal.add('X-WR-CALDESC').value = getattr(self, "description")()
        cal.add('X-WR-TIMEZONE').value = getattr(self, "timezone")()
        cal.add('CALSCALE').value = "GREGORIAN"
        cal.add('METHOD').value = "PUBLISH"

        for item in self.items():

            event = cal.add('vevent')

            for vkey, key in EVENT_ITEMS:
                value = getattr(self, 'item_' + key)(item)
                if isinstance(value, str):
                    value = smart_unicode(value)
                if value:
                    event.add(vkey).value = value

        locale.setlocale(locale.LC_ALL, 'fr_CA.UTF8')
        response = HttpResponse(cal.serialize())
        response['Content-Type'] = 'application/octet-stream; charset=utf-8'
        return response

    def name(self):
        return ""

    def description(self):
        return ""

    def timezone(self):
        return ""

    def items(self):
        return []

    def item_uid(self, item):
        pass

    def item_start(self, item):
        pass

    def item_end(self, item):
        pass

    def item_summary(self, item):
        return str(item)

    def item_location(self, item):
        pass

    def item_last_modified(self, item):
        pass

    def item_description(self, item):
        pass

    def item_created(self, item):
        pass

    def item_url(self, item):
        pass


class UpcomingEventCalendar(ICalendarFeed):
    def name(self):
        return u"L'Agenda de l'Accoord"

    def description(self):
        return u"Tous les événements de l'Agenda de l'Accoord"

    def timezone(self):
        return u"Europe/Paris"

    def items(self):
        start = date.today() - timedelta(days=30)
        end = date.today() + timedelta(days=60)
        return (Event.objects
                .filter(moderated=True)
                .filter(start_time__gte=start)
                .filter(start_time__lte=end))

    def item_uid(self, item):
        return str(item.id) + "@agenda.accoord.fr"

    def item_start(self, item):
        return item.start_time

    def item_end(self, item):
        return item.end_time

    def item_location(self, item):
        return item.address + ", " + item.city.name

    def item_description(self, item):
        return remove_html_tags(item.description)

    def item_url(self, item):
        return item.url


class UpcomingEventCalendarByRegion (ICalendarFeed):

    def __init__(self, region):
        self.region = region

    def name(self):
        return u"L'Agenda de l'Accoord (" + self.region.name + ")"

    def description(self):
        return (u"Tous les événements de l'Accoord pour le quartier "
                + self.region.name)

    def timezone(self):
        return u"Europe/Paris"

    def items(self):
        start = date.today() - timedelta(days=30)
        end = date.today() + timedelta(days=60)

        if self.region is not None:
            q = Q(city__region=self.region)
        else:
            q = Q()

        return (Event.objects
                .filter(q)
                .filter(moderated=True)
                .filter(start_time__gte=start, start_time__lte=end))

    def item_uid(self, item):
        return str(item.id) + "@agenda.accoord.fr"

    def item_start(self, item):
        return item.start_time

    def item_end(self, item):
        return item.end_time

    def item_location(self, item):
        return (item.address + ", " + item.city.name + ", "
                + item.city.region.name)

    def item_description(self, item):
        return remove_html_tags(item.description)

    def item_url(self, item):
        return item.url


class LatestEntries(Feed):
    title = "Agenda.accoord.fr nouveaux évenements"
    link = "/event/"
    description = "Flux à jour des derniers événements ajoutés"

    def items(self):
        return (Event.objects
                .filter(moderated=True)
                .order_by('-submission_time')[:10])

    def item_pubdate(self, item):
        return item.start_time


class LatestEntriesByRegion(LatestEntries):
    link = "/event/"

    def items_title(self, obj):
        return (u"Agenda.accoord.fr: Nouveaux événements pour %s"
                % obj.name)

    def items_description(self, obj):
        return (u"Événements de l'association Accoord"
                u" pour %s"
                % obj.name)

    def get_object(self, request, region_id):
        return get_object_or_404(Region, pk=region_id)

    def items(self, region):
        if region is not None:
            q = Q(city__region=region)
        else:
            q = Q()

        return (Event.objects
                .filter(q)
                .filter(moderated=True)
                .order_by('-submission_time')[:10])


class UpcomingEntries(LatestEntries):
    title = "Agenda.accoord.fr prochains événements"
    link = "/event/"
    description = "Flux à jour des événements à venir"

    def items(self):
        today = date.today()
        return (Event.objects
                .filter(moderated=True)
                .filter(start_time__gte=today)
                .order_by('start_time')[:10])


class UpcomingEntriesByRegion(UpcomingEntries):
    link = "/event/"

    def title(self, obj):
        return (u"Agenda.accoord.fr: Événements à venir pour %s"
                % obj.name)

    def description(self, obj):
        return (u"Événements de l'association Accoord pour %s"  # noqa
                % obj.name)

    def get_object(self, request, region_id):
        return get_object_or_404(Region, pk=region_id)

    def items(self, region=None):
        if region is not None:
            q = Q(city__region=region)
        else:
            q = Q()
        return (Event.objects
                .filter(q)
                .filter(moderated=True)
                .order_by('-start_time')[:10])
