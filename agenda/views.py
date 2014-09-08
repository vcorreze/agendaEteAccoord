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
from django.shortcuts import render_to_response
from django.views.generic import TemplateView, RedirectView
from datetime import date


class IndexView(RedirectView):
    today = date.today()
    url = "/event/%d/%d/" % (today.year, today.month)


class AboutView(TemplateView):
    template = 'about.html'


def construction(request):
    return render_to_response("construction.html", dict())


def settings(request):
    return render_to_response('events/settings.html', dict())
