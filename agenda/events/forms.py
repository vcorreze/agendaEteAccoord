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

from captcha.fields import ReCaptchaField

from django import forms
from agenda.events.models import Event, City, Region
from agenda.events.widgets import SplitSelectDateTimeWidget
from django.forms.util import ErrorList
from django.conf import settings
from datetime import datetime


class EventCityChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return u'{} / {}'.format(unicode(obj.region), unicode(obj))


class EventForm(forms.ModelForm):
    year = datetime.today().year
    years = [year,
             year + 1,
             year + 2]

    start_time = forms.DateTimeField(label="Débute le", \
        widget=SplitSelectDateTimeWidget(hour_step=1, \
        minute_step=15, second_step=30, twelve_hr=False, years=years))

    end_time = forms.DateTimeField(label="Se termine le", \
        widget=SplitSelectDateTimeWidget(hour_step=1, \
        minute_step=15, second_step=30, twelve_hr=False, years=years))

    city = EventCityChoiceField(
        City.objects.all().order_by('region__name', 'name'),
        empty_label=None,
        label="Équipement"
    )

    captcha = ReCaptchaField(attrs={'theme' : 'clean'})

    class Meta:
      model = Event
      exclude = ("submission_time", "updated_time", "decision_time",
                 "moderator", "moderated", "latitude", "longitude",
                 "banner", "spotlight", "announced", "twitter")

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        if not settings.RECAPTCHA_ENABLE:
            del self.fields['captcha']

    def clean(self):
      cleaned_data = self.cleaned_data
      start_time = cleaned_data.get("start_time")
      end_time = cleaned_data.get("end_time")

      if not (start_time and end_time):
        return cleaned_data

      if start_time >= end_time:
        msg = u"L'événement ne peut se terminer avant son début"
        self._errors["start_time"] = ErrorList([msg])
        self._errors["end_time"] = ErrorList([msg])

        del cleaned_data["start_time"]
        del cleaned_data["end_time"]

      elif start_time < datetime.today():
        msg = u"Seul les événements à venir sont acceptés"
        self._errors["start_time"] = ErrorList([msg])

        del cleaned_data["start_time"]

      return cleaned_data


class RegionFilterForm(forms.Form):

    region = forms.ModelChoiceField(
        Region.objects.all(),
        empty_label=u"Tous les quartiers",
        required=False,
        label=u"Quartier",
        widget=forms.Select(
            attrs={
                #"onchange":"document.getElementById('filter').submit();"
                "style": "visibility: hidden"
            }
        )
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label=u"Tous les équipements",
        required=False,
        label=u"Équipements",
        widget=forms.Select(attrs={"onchange":"document.getElementById('filter').submit();"})
    )
