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

from django.conf.urls import url, patterns
from django.views.generic import ListView, DetailView, TemplateView
from agenda.events.models import Event
from agenda.events.feeds import (LatestEntries,
                                 UpcomingEntries,
                                 UpcomingEventCalendar,
                                 LatestEntriesByRegion,
                                 UpcomingEntriesByRegion)


class EventList(ListView):
    model = Event


class EventDetail(DetailView):
    model = Event


class ThanksView(TemplateView):
    template_name = "events/event_thanks.html"


general_info = {
    "queryset": Event.objects.filter(moderated=True),
    "template_object_name": "event",
}

list_info = {
    "paginate_by": 25,
}

event_info = general_info
event_list_info = dict(general_info, **list_info)

feeds = {
    "latest": LatestEntries(),
    "upcoming": UpcomingEntries(),
    "latest_region": LatestEntriesByRegion(),
    "upcoming_region": UpcomingEntriesByRegion(),
}


urlpatterns = patterns(
    "",
    url(r"^$", EventList.as_view()),
    url(r"^new/$", "agenda.events.views.propose", name="propose"),
    url(r"^help/$", "agenda.events.views.help", name="help"),
    url(r"^new/thanks/$", ThanksView.as_view()),
    url(r"^(?P<pk>\d+)/$", EventDetail.as_view(), name="event_detail"),

    url(r"^(?P<event_id>\d+)/edit", "agenda.events.views.edit",
        name="edit"),
    url(r"^(?P<event_id>\d+)/moderate$", "agenda.events.views.moderate",
        name="moderate"),
    url(r"^(?P<event_id>\d+)/unmoderate$", "agenda.events.views.unmoderate",
        name="unmoderate"),
    url(r"^(?P<event_id>\d+)/delete_confirm", "agenda.events.views.delete_confirm",
        name="delete_confirm"),

    url(r"^moderate_my_events/$", "agenda.events.views.moderate_my_events", name="moderate_my_events"),

    url(r"^(?P<year>\d+)/(?P<month>\d+)/$", "agenda.events.views.month",
        name="month_view"),

    url(r"^stats/$", "agenda.events.views.stats", name="stats"),

    url(r"^feeds/$", "agenda.events.views.feed_list", name="feed_list"),
    (r"^feeds/latest/$", LatestEntries()),
    (r"^feeds/upcoming/$", UpcomingEntries()),
    (r"^feeds/latest_region/(?P<region_id>\d+)/$", LatestEntriesByRegion()),
    (r"^feeds/upcoming_region/(?P<region_id>\d+)/$",
     UpcomingEntriesByRegion()),

    (r"^calendar/$", UpcomingEventCalendar()),
    (r"^calendar_region/(?P<region_id>\d+)/$",
     "agenda.events.views.calendar_region"),

)
