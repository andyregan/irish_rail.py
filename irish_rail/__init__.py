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

    def __str__(self):
        return self.code

    def __repr__(self):
        return "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              self.__dict__)

    @property
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
        return "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              self.__dict__)

    @property
    def next_arrivals(self):
        """
        A list of the trains due to arrive at the station in the next 90 minutes.
        Returns [ArrivingTrain]

        """
        query = "%s/getStationDataByNameXML?StationDesc=%s" % (self.API, self.description)
        result = requests.get(query)
        return self.station_arrivals_from_query(result.content)

    def kilometers_from(self, latitude, longitude):
        """
        Kilometers in a straigt line from the given latitude and longitude

        """
        return vincenty((self.latitude, self.longitude), (latitude, longitude)).km

    def station_arrivals_from_query(self, query_result):
        """
        Returns a list of ArrivingTrain instances from query_result

        """
        tree = ElementTree.fromstring(query_result)
        arrivals = []
        for child in tree:
            arrivals.append(
                ArrivingTrain(
                    self,
                    self.child_text(child, 'Traincode'),
                    self.child_text(child, 'Origin'),
                    self.child_text(child, 'Destination'),
                    self.child_text(child, 'Origintime'),
                    self.child_text(child, 'Destinationtime'),
                    self.child_text(child, 'Status'),
                    self.child_text(child, 'Lastlocation'),
                    self.child_text(child, 'Duein'),
                    self.child_text(child, 'Late'),
                    self.child_text(child, 'Exparrival'),
                    self.child_text(child, 'Expdepart'),
                    self.child_text(child, 'Scharrival'),
                    self.child_text(child, 'Schdepart'),
                    self.child_text(child, 'Direction'),
                    self.child_text(child, 'Traintype'),
                    self.child_text(child, 'Locationtype'),
                )
            )
        return arrivals

    @classmethod
    def child_text(cls, child, name):
        """
        Returns the text of the given ElementTree child

        """
        return child.find(cls.element_tag(name)).text

    @classmethod
    def element_tag(cls, name):
        """
        Returns an element tag for given name

        """
        return "%s%s" % (cls.TAG_PREFIX, name)

    @classmethod
    def stations_from_query(cls, query_result):
        """
        Returns a list of Station instances from a
        query result

        """
        stations = []
        tree = ElementTree.fromstring(query_result)
        for child in tree:
            stations.append(
                Station(
                    cls.child_text(child, 'StationId'),
                    cls.child_text(child, 'StationCode'),
                    cls.child_text(child, 'StationAlias'),
                    cls.child_text(child, 'StationDesc'),
                    cls.child_text(child, 'StationLatitude'),
                    cls.child_text(child, 'StationLongitude')
                )
            )
        return stations

    @classmethod
    def all(cls):
        """
        Returns a list of all Stations

        """
        query = "%s/getAllStationsXML" % cls.API
        result = requests.get(query)
        return cls.stations_from_query(result.content)

    @classmethod
    def by_name(cls, name):
        """
        Returns an instance of Station for given name

        """
        stations = [
            station for station in cls.all()
            if station.description.lower() == name.lower()
        ]
        return stations[0]

    @classmethod
    def closest_to(cls, latitude, longitude):
        """
        Return the closest Station in a straight line from
        the given latitude and longitude.

        """
        stations = cls.all()
        stations.sort(key=methodcaller('kilometers_from', latitude, longitude))
        return stations[0]
