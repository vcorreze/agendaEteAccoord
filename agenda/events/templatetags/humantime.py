# -*- encoding:utf-8 -*-
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

from django.template.defaultfilters import stringfilter
from datetime import datetime, timedelta
from django import template
import locale

register = template.Library()


def format_hour(date):
    # Ex: 9h, 9h15
    # Note: old used format was .strftime("%H:%M")
    minute = date.minute
    if minute:
        return '%dh%.2d' % (date.hour, minute)
    else:
        return '%dh' % date.hour


def format_day(date):
    # Exemple : Vendredi 3 juin 2016
    return date.strftime('%A ') \
                + date.strftime('%d ').lstrip('0') \
                + date.strftime('%B %Y')


@register.filter
def event_time(start, end):
    # Hack! get the correct user local from the request
    #loc = locale.getlocale()
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # Force french locale !

    result = ""

    # Note : Don't display "Aujourd'hui " for printing reasons
    # today = datetime.today().date()
    # if start.date() == today:
    #     result += "Aujourd'hui "
    # else:
    #     result += "Le %s " % start.strftime("%A %d %B %Y")

    # Check if there is hours to display

    start_date = start.date()
    has_start_hour = not (start.hour == 0 and start.minute == 0)

    end_date = end.date()
    has_end_hour = not (end.hour == 0 and end.minute == 0)

    has_only_start_hour = has_start_hour and not has_end_hour
    has_only_end_hour = has_end_hour and not has_start_hour
    has_start_and_end_hour = has_start_hour and has_end_hour

    # Example : datetime.datetime(2016, 6, 3, 9, 30) == 03/06/2016 09:30
    # %A => 'Vendredi'
    # %d => '03'
    # %B => 'juin'
    # %Y => '2016'
    # %H => '09'
    # %M => '30'

    if start_date == end_date:
        # start and end are the same days
        result += "%s " % format_day(start)

        if has_only_start_hour:
            result += "à %s " % format_hour(start)

        elif has_only_end_hour:
            result += "jusqu'à %s " % format_hour(end)

        elif has_start_and_end_hour:
            if start.hour == end.hour:
                result += "à %s " % format_hour(start)
            else:
                result += "de %s " % format_hour(start)
                result += "à %s " % format_hour(end)

    else:
        # start and end are different days
        result += "Du %s " % format_day(start)

        if has_start_hour:
            result += "à %s " % format_hour(start)

        result += "au %s " % format_day(end)

        if has_end_hour:
            result += "à %s " % format_hour(end)

    #locale.setlocale(locale.LC_ALL, loc)
    return result

