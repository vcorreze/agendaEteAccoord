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

from collections import OrderedDict
from datetime import date, timedelta

from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from django.template.response import TemplateResponse
from django.template.loader import render_to_string

from django.http import HttpResponseNotFound

from agenda.events.forms import EventForm, RegionFilterForm
from agenda.events.models import Region, City, Event
from agenda.events.feeds import UpcomingEventCalendarByRegion
from agenda.events.utils import mail_moderators

from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.conf import settings


@login_required
def propose(request, template_name="events/event_new.html"):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            e = form.save()
            moderator = e.city.region.moderator
            if settings.ENABLE_MAIL and moderator is not None:
                msg = render_to_string("events/mail.html", {
                    "event": e
                })
                moderators = [moderator]
                mail_moderators(u"Nouvel événement en attente de modération",
                                msg, moderators)
            return HttpResponseRedirect("/event/new/thanks/")
    else:
        form = EventForm()
    return TemplateResponse(request, template_name, {
        "form": form,
    })


@login_required
def edit(request, event_id, template_name="events/event_edit.html"):
    try:
        event = Event.objects.get(pk=event_id)
    except Region.DoesNotExist:
        return HttpResponseNotFound()

    # action reserved to the region's moderator
    if event.city.region.moderator != request.user:
        raise PermissionDenied()

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            e = form.save()
            return HttpResponseRedirect(reverse("event_detail", args=[event_id]))
    else:
        form = EventForm(instance=event)
    return TemplateResponse(request, template_name, {
        "form": form,
        "event": event
    })


@login_required
def delete_confirm(request, event_id, template_name="events/event_delete_confirm.html"):
    try:
        event = Event.objects.get(pk=event_id)
    except Region.DoesNotExist:
        return HttpResponseNotFound()

    # action reserved to the region's moderator
    if event.city.region.moderator != request.user:
        raise PermissionDenied()

    if request.method == "POST":
        # delete event
        event.delete()
        return HttpResponseRedirect(reverse("index"))

    return TemplateResponse(request, template_name, {
        'event': event
    })


def region_cmp (a, b):
    return a["value"] - b["value"]


def stats(request):
    total = (Event.objects
             .filter(moderated=True)
             .aggregate(Count("id"))["id__count"])
    total_to_moderate = (Event.objects
                         .filter(moderated=False)
                         .aggregate(Count("id"))["id__count"])

    region_list = []
    regions = Region.objects.all()
    for region in regions:
        region_list.append({
            "name": region.name,
            "value": (Event.objects
                      .filter(moderated=True,city__region=region)
                      .aggregate(Count("id"))["id__count"])
        })
    region_list.sort(region_cmp, reverse=True)

    return render_to_response("events/stats.html", {
        "region_list": region_list,
        "total": total,
        "total_to_moderate": total_to_moderate,
        "user": request.user
    })


def feed_list(request):
    region_list = Region.objects.all()

    return render_to_response("events/feeds.html", {
        "region_list": region_list,
        "user": request.user
    })


def help(request, template_name="events/help.html"):
    return TemplateResponse(request, template_name)


@login_required
def moderate(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Region.DoesNotExist:
        return HttpResponseNotFound()

    # action reserved to the region's moderator
    if event.city.region.moderator != request.user:
        raise PermissionDenied()

    event.moderated = True
    event.moderator = request.user
    event.save()
    return HttpResponseRedirect(reverse("event_detail", args=[event_id]))


@login_required
def unmoderate(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Region.DoesNotExist:
        return HttpResponseNotFound()

    # action reserved to the region's moderator
    if event.city.region.moderator != request.user:
        raise PermissionDenied()

    event.moderated = False
    event.moderator = request.user
    event.save()
    return HttpResponseRedirect(reverse("event_detail", args=[event_id]))


def calendar_region(request, region_id):
    try:
        region = Region.objects.get(pk=region_id)
    except Region.DoesNotExist:
        return HttpResponseNotFound()
    callable = UpcomingEventCalendarByRegion(region)
    return callable(request)


def month(request, year, month,
          template_name="events/event_archive_month.html"):
    month = date(int(year), int(month), 1)
    previous = month - timedelta(days=15)
    next = month + timedelta(days=45)

    form = RegionFilterForm(request)

    region = None
    city = None
    if request.method == "GET":
        form = RegionFilterForm(request.GET)
        if form.is_valid():
            region = form.cleaned_data["region"]
            city = form.cleaned_data["city"]
            # limit city to the selection region
            form.fields['city'].queryset = City.objects.filter(region=region).all()
    else:
        form = RegionFilterForm()

    return TemplateResponse(request, template_name, {
        "month": month,
        "previous_month": previous,
        "next_month": next,
        "form": form,
        "region": region,
        "city": city,
        "regions": Region.objects.all()
    })

@login_required
def moderate_my_events(request):
    """ List all my events I have to moderate """
    events = Event.objects.filter(
        moderated=False,
        city__region__moderator=request.user
    ).select_related('city__region'
    ).order_by('city__region', 'city')

    # Group our events by region then by city, using OrderedDict structures
    # { region_obj1: { eq_obj1: [event1, event2, ...],
    #                 ...
    #                },
    #   ...
    # }
    result = OrderedDict()

    for event in events:

        # New region ? (quartier)
        region = event.city.region
        if region not in result:
            result[region] = OrderedDict()  # equipments
        r_region = result[region]

        # New city ? (équipement)
        equipment = event.city
        if equipment not in r_region:
            r_region[equipment] = []  # events
        r_equipment = r_region[equipment]

        # Add our event
        r_equipment.append(event)

    return TemplateResponse(request, 'events/moderate_my_events.html', {
        'events_struct': result
    })
