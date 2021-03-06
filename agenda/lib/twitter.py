# -*- encoding:utf-8 -*-
#
# Copyright (C) 2014 Mathieu Leduc-Hamel
#
# Author: Mathieu Leduc-Hamel <marrakis@gmail.com>
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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import twitter

from django.conf import settings as s


class EventTweeter(object):
    """
    Object responsible at creating the link between twitter and an
    event.
    """
    def __init__(self):
        self.auth = twitter.oauth.OAuth(s.TWITTER_OAUTH_TOKEN,
                                        s.TWITTER_OAUTH_TOKEN_SECRET,
                                        s.TWITTER_CONSUMER_KEY,
                                        s.TWITTER_CONSUMER_SECRET)

        self.api = twitter.Twitter(auth=self.auth)

    def tweet(self, message):
        """ Send the message to twitter """
        self.api.statuses.update(status=message)
