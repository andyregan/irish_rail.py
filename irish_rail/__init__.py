"""
Irish Rail API

"""
from xml.etree import ElementTree
from operator import methodcaller

from geopy.distance import vincenty
import requests

class Station:
    """
    An Irish Rail Station

    """
    API = "http://api.irishrail.ie/realtime/realtime.asmx"
    TAG_PREFIX = "{http://api.irishrail.ie/realtime/}"

    def __init__(self,
                 station_id,
                 code,
                 alias,
                 description,
                 latitude,
                 longitude):
        self.station_id = station_id
        self.code = code
        self.alias = alias
        self.description = description
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return self.description

    def __repr__(self):
        return "%s ID: %s, Description: %s" % (self.__class__, self.station_id, self.description)

    def kilometers_from(self, latitude, longitude):
        """
        Kilometers in a straigt line from the given latitude and longitude

        """
        return vincenty((self.latitude, self.longitude), (latitude, longitude)).km

    @classmethod
    def all(cls):
        """
        Returns a list of all Stations

        """
        query = "%s/getAllStationsXML" % cls.API
        all_stations = requests.get(query)
        tree = ElementTree.fromstring(all_stations.content)
        stations = []
        for child in tree:
            stations.append(
                Station(
                    child.find("%sStationId" % cls.TAG_PREFIX).text,
                    child.find("%sStationCode" % cls.TAG_PREFIX).text,
                    child.find("%sStationAlias" % cls.TAG_PREFIX).text,
                    child.find("%sStationDesc" % cls.TAG_PREFIX).text,
                    child.find("%sStationLatitude" % cls.TAG_PREFIX).text,
                    child.find("%sStationLongitude" % cls.TAG_PREFIX).text
                )
            )
        return stations

    @classmethod
    def closest_to(cls, latitude, longitude):
        """
        Return the closest Station in a straight line from
        the given latitude and longitude.

        """
        stations = cls.all()
        stations.sort(key=methodcaller('kilometers_from', latitude, longitude))
        return stations[0]
