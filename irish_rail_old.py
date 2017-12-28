#!/usr/bin/env python
import urllib

import requests
from xml.dom import minidom


STATION_TYPE_TO_CODE_DICT = {
    'mainline': 'M',
    'suburban': 'S',
    'dart': 'D'
}


def _get_minidom_tag_value(station, tag_name):
    tag = station.getElementsByTagName(tag_name)[0].firstChild
    if tag:
        return tag.nodeValue
    else:
        return None


def _parse(url, obj_name, attr_map):
    data = requests.get(url).content
    parsed_xml = minidom.parseString(data)
    parsed_objects = []
    for obj in parsed_xml.getElementsByTagName(obj_name):
        parsed_obj = {}
        for (py_name, xml_name) in attr_map.iteritems():
            print xml_name, py_name
            parsed_obj[py_name] = _get_minidom_tag_value(obj, xml_name)
        parsed_objects.append(parsed_obj)
    return parsed_objects


def _parse_station_list(url):
    attr_map = {
        'name': 'StationDesc',
        'alias': 'StationAlias',
        'lat': 'StationLatitude',
        'long': 'StationLongitude',
        'code': 'StationCode',
        'id': 'StationId',
    }
    return _parse(url, 'objStation', attr_map)


def _parse_station_data(url):
    attr_map = {
        'code': 'Traincode',
        'origin': 'Origin',
        'destination': 'Destination',
        'origin_time': 'Origintime',
        'destination_time': 'Destinationtime',
        'due_in_mins': 'Duein',
        'late_mins': 'Late',
        'expected_arrival_time': 'Exparrival',
        'expected_departure_time': 'Expdepart',
        'scheduled_arrival_time': 'Scharrival',
        'scheduled_departure_time': 'Schdepart',
        'type': 'Traintype',
        'direction': 'Direction',
        'location_type': 'Locationtype',
    }
    return _parse(url, 'objStationData', attr_map)


def _parse_all_train_data(url):
    attr_map = {
        'status': 'TrainStatus',
        'latitude': 'TrainLatitude',
        'longitude': 'TrainLongitude',
        'code': 'TrainCode',
        'date': 'TrainDate',
        'message': 'PublicMessage',
        'direction': 'Direction'
    }
    return _parse(url, 'objTrainPositions', attr_map)


def get_all_stations(station_type=None):
    '''Returns information of all stations.

    @param<optional> station_type: ['mainline', 'suburban', 'dart']
    '''
    if station_type and station_type in STATION_TYPE_TO_CODE_DICT:
        url = 'http://api.irishrail.ie/realtime/realtime.asmx/getAllStationsXML_WithStationType?'
        param_dict = {
            'stationType': STATION_TYPE_TO_CODE_DICT[station_type]
        }
        url = url + urllib.urlencode(param_dict)
    else:
        url = 'http://api.irishrail.ie/realtime/realtime.asmx/getAllStationsXML'
    return _parse_station_list(url)


def get_all_current_trains(train_type=None):
    '''Returns all trains that are due to start in the next 10 minutes

    @param train_type: ['mainline', 'suburban', 'dart']
    '''
    if train_type:
        url = 'http://api.irishrail.ie/realtime/realtime.asmx/getCurrentTrainsXML_WithTrainType'
        param_dict = {
            'TrainType': STATION_TYPE_TO_CODE_DICT[train_type]
        }
        url = url + urllib.urlencode(param_dict)
    else:
        url = 'http://api.irishrail.ie/realtime/realtime.asmx/getCurrentTrainsXML'
    return _parse_all_train_data(url)


def get_station_by_name(station_name, num_minutes=None):
    '''Returns all trains due to serve station `station_name`.

    @param station_name
    @param num_minutes
    '''
    url = 'http://api.irishrail.ie/realtime/realtime.asmx/getStationDataByNameXML?'
    param_dict = {
        'StationDesc': station_name
    }
    if num_minutes:
        param_dict['NumMins'] = num_minutes
    url = url + urllib.urlencode(param_dict)
    return _parse_station_data(url)


def get_station_by_code(station_code, num_minutes=None):
    '''Returns all trains due to serve station with code `station code`.

    '''
    url = 'http://api.irishrail.ie/realtime/realtime.asmx/getStationDataByCodeXML?'
    param_dict = {
        'StationCode': station_code
    }
    if num_minutes:
        param_dict['NumMins'] = num_minutes
    url = url + urllib.urlencode(param_dict)
    return _parse_station_data(url)
