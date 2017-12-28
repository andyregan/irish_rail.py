"""
Irish Rail API

"""
from xml.etree import ElementTree
from operator import methodcaller

from geopy.distance import vincenty
import requests

class ArrivingTrain:
    """
    A Train Arriving to a Station
    """
    def __init__(self,
                 station,
                 code,
                 origin,
                 destination,
                 origin_time,
                 destination_time,
                 status,
                 last_location,
                 minutes_until_due,
                 minutes_late,
                 expected_arrival,
                 expected_departure,
                 scheduled_arrival,
                 scheduled_departure,
                 direction,
                 train_type,
                 location_type):
        self.station = station
        self.code = code
        self.origin = origin
        self.destination = destination
        self.origin_time = origin_time
        self.destination_time = destination_time
        self.status = status
        self.last_location = last_location
        self.due_in_minutes = minutes_until_due
        self.minutes_late = minutes_late
        self.expected_arrival = expected_arrival
        self.expected_departure = expected_departure
        self.scheduled_arrival = scheduled_arrival
        self.scheduled_departure = scheduled_departure
        self.direction = direction
        self.train_type = train_type
        self.location_type = location_type

    def message(self):
        """
        A message about the train's arrival status

        """
        return """
        The {train.direction} {train.origin_time} {train.origin} to {train.destination} service
        is expected to arrive at {train.station.description}
        in {train.due_in_minutes} minutes at {train.expected_arrival}. It is {train.minutes_late} minutes late.
        The status is {train.status}.
        """.format(train=self)


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

    def next_arrivals(self):
        """
        A list of the trains due to arrive at the station in the next 90 minutes.
        Returns [ArrivingTrain]

        """
        query = "%s/getStationDataByNameXML?StationDesc=%s" % (self.API, self.description)
        station_arrivals = requests.get(query)
        tree = ElementTree.fromstring(station_arrivals.content)
        arrivals = []
        for child in tree:
            arrivals.append(
                ArrivingTrain(
                    self,
                    child.find(self.element_tag('Traincode')).text,
                    child.find(self.element_tag('Origin')).text,
                    child.find(self.element_tag('Destination')).text,
                    child.find(self.element_tag('Origintime')).text,
                    child.find(self.element_tag('Destinationtime')).text,
                    child.find(self.element_tag('Status')).text,
                    child.find(self.element_tag('Lastlocation')).text,
                    child.find(self.element_tag('Duein')).text,
                    child.find(self.element_tag('Late')).text,
                    child.find(self.element_tag('Exparrival')).text,
                    child.find(self.element_tag('Expdepart')).text,
                    child.find(self.element_tag('Scharrival')).text,
                    child.find(self.element_tag('Schdepart')).text,
                    child.find(self.element_tag('Direction')).text,
                    child.find(self.element_tag('Traintype')).text,
                    child.find(self.element_tag('Locationtype')).text,
                )
            )
        return arrivals

    def element_tag(self, name):
        """
        Returns an element tag for given name

        """
        return "%s%s" % (self.TAG_PREFIX, name)

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
