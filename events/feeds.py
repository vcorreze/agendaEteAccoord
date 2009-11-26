# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from agenda.events.models import Event, Region
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import date, timedelta
import vobject
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Q

EVENT_ITEMS = (
    ('uid', 'uid'),
    ('dtstart', 'start'),
    ('dtend', 'end'),
    ('summary', 'summary'),
    ('description', 'description'),
    ('location', 'location'),
    ('last_modified', 'last_modified'),
    ('created', 'created'),
)

class ICalendarFeed(object):

    def __call__(self, *args, **kwargs):

        cal = vobject.iCalendar()

        for item in self.items():

            event = cal.add('vevent')

            for vkey, key in EVENT_ITEMS:
                value = getattr(self, 'item_' + key)(item)
                if value:
                    event.add(vkey).value = value

        response = HttpResponse(cal.serialize())
        response['Content-Type'] = 'text/calendar'

        return response

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


class UpcomingEventCalendar(ICalendarFeed):

    def items(self):
        start = date.today() - timedelta (days=30)
        end = date.today() + timedelta (days=60)
        return Event.objects.filter(moderated=True,start_time__gte=start,start_time__lte=end)

    def item_uid(self, item):
        return str(item.id)

    def item_start(self, item):
        return item.start_time

    def item_end(self, item):
        return item.end_time

    def item_location(self, item):
        return item.address + ", " + item.city.name + ", " + item.city.region.name

    def item_description(self, item):
        return item.description


class UpcomingEventCalendarByRegion (ICalendarFeed):

    def __init__(self, region):
        self.region = region

    def items(self):
        start = date.today() - timedelta (days=30)
        end = date.today() + timedelta (days=60)

        if self.region != None:
          print self.region
          q = Q(city__region=self.region,scope="L") | Q(scope="I") | Q(scope="N")
        else:
          q = Q()

        return Event.objects.filter(q).filter(moderated=True,start_time__gte=start,start_time__lte=end)

    def item_uid(self, item):
        return str(item.id)

    def item_start(self, item):
        return item.start_time

    def item_end(self, item):
        return item.end_time

    def item_location(self, item):
        return item.address + ", " + item.city.name + ", " + item.city.region.name

    def item_description(self, item):
        return item.description

class LatestEntries(Feed):
    title = "Agendadulibre.qc.ca nouveaux évenements"
    link = "/event/"
    description = "Flux à jour des derniers évènements ajoutés"

    def items(self):
        return Event.objects.filter(moderated=True).order_by('-submission_time')[:10]

    def item_pubdate(self, item):
        return item.start_time

class LatestEntriesByRegion(LatestEntries):
    link = "/event/"

    def title(self, obj):
        return u"Agendadulibre.qc.ca: Nouveaux évènements pour %s (Québec)" % obj[0].name

    def description(self, obj):
        return u"Évènements relatif aux logiciels libre récemment ajouté pour %s (Québec) et à plus grande portée" % obj[0].name

    def get_object(self, params):
        if len(params) != 1:
            raise ObjectDoesNotExist

        r = Region.objects.filter(pk__exact=params[0])

        if r:
            return r
        else:
            raise ObjectDoesNotExist

    def items(self, region):
        if region != None:
          print region
          q = Q(city__region=region,scope="L") | Q(scope="I") | Q(scope="N")
        else:
          q = Q()

        return Event.objects.filter(q).filter(moderated=True).order_by('-submission_time')[:10]


class UpcomingEntries(LatestEntries):
    title = "Agendadulibre.qc.ca prochains évenements"
    link = "/event/"
    description = "Flux à jour des évènements à venir"

    def items(self):
        today = date.today ()
        return Event.objects.filter(moderated=True,start_time__gte=today).order_by('start_time')[:10]

class UpcomingEntriesByRegion(UpcomingEntries):
    link = "/event/"

    def title(self, obj):
        return u"Agendadulibre.qc.ca: Évènements à venir pour %s (Québec)" % obj[0].name

    def description(self, obj):
        return u"Évènements relatif aux logiciels libre à venir pour %s (Québec) et à plus grande portée" % obj[0].name

    def get_object(self, params):
        if len(params) != 1:
            raise ObjectDoesNotExist

        r = Region.objects.filter(pk__exact=params[0])

        if r:
            return r
        else:
            raise ObjectDoesNotExist

    def items(self, region):
        if region != None:
          print region
          q = Q(city__region=region,scope="L") | Q(scope="I") | Q(scope="N")
        else:
          q = Q()

        return Event.objects.filter(q).filter(moderated=True).order_by('start_time')[:10]
