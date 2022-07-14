import json
import csv
import math
import datetime
from math import cos, sin, pi, atan2
import utm
import argparse

def new_point(latitude, longitude, speed, azimuth, tickrate_time, acceleration):
    Vx = speed * math.cos(azimuth)
    Vy = speed * math.sin(azimuth)
    utm_xy = utm.from_latlon(latitude, longitude)
    new_x = utm_xy[0] + Vx * tickrate_time.total_seconds() + 0.5 * acceleration * math.cos(azimuth) * (tickrate_time.total_seconds()** 2)
    new_y = utm_xy[1] + Vy * tickrate_time.total_seconds() + 0.5 * acceleration * math.sin(azimuth) * (tickrate_time.total_seconds()** 2)
    new_xy = utm.to_latlon(new_x, new_y, utm_xy[2], utm_xy[3])
    return new_xy[0], new_xy[1]

def get_bearing(coord_1, coord_2):
    lat_1_r = coord_1[0] * pi / 180
    lat_2_r = coord_2[0] * pi / 180
    dlon = (coord_2[1] - coord_1[1]) * pi / 180
    y = sin(dlon) * cos(lat_2_r)
    x = cos(lat_1_r) * sin(lat_2_r) - \
        sin(lat_1_r) * cos(lat_2_r) * cos(dlon)

    theta = atan2(y, x)

    bearing = (theta * 180) / pi
    if bearing < 0:
        return bearing + 360
    return bearing

def save_to_file(output_fname, format, telematic_data):
    if format == 'JSON':
        with open(output_fname + '.json', 'w') as outfile:
            json.dump(telematic_data, outfile)
    elif format == 'CSV':
        with open(output_fname + '.csv', 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'latitude', 'longitude', 'azimuth', 'speed']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for point in telematic_data:
                writer.writerow({'timestamp': point['timestamp'],
                                 'latitude': point['latitude'], 
                                 'longitude': point['longitude'],
                                 'azimuth': point['azimuth'],
                                 'speed': point['speed']
                                })
def generate(config_fname, output_fname):
    with open(config_fname) as config:
        config_data = json.load(config)

    latitude = config_data['start']['latitude']
    longitude = config_data['start']['longitude']
    speed = 0
    current_time = datetime.datetime.strptime(config_data['start']['time'], '%Y-%m-%dT%H:%M:%S%z')
    telematic_data = []

    for point in config_data['points']:
        tickrate_time = datetime.timedelta(seconds=1 / config_data['frequency'])
        acceleration = point['max_acceleraion'] / 12960

        azimuth = get_bearing([latitude, longitude], [point['latitude'], point['longitude']])
        direction = math.radians(90 - azimuth)
        new_latitude, new_longitude = new_point(latitude, longitude, speed, direction, tickrate_time, acceleration)
        utm_point = utm.from_latlon(new_latitude, new_longitude)
        utm_destination = utm.from_latlon(point['latitude'], point['longitude'])
        distance = math.sqrt(((utm_point[0]-utm_destination[0])**2)+((utm_point[1]-utm_destination[1])**2))
        point_speed = point['speed'] / 3.6
        while not(math.isclose(distance, 0, abs_tol=0.1)):
            azimuth = get_bearing([latitude, longitude], [point['latitude'], point['longitude']])
            direction = math.radians(90 - azimuth)
            if (point_speed > speed):
                if (point_speed - speed) / tickrate_time.total_seconds() > acceleration:
                    speed += acceleration * tickrate_time.total_seconds()
                elif (point_speed - speed) / tickrate_time.total_seconds() < acceleration:
                    acceleration = (point_speed - speed) / tickrate_time.total_seconds()
                    speed += acceleration * tickrate_time.total_seconds()
            elif (point_speed < speed):
                if (speed - point_speed) / tickrate_time.total_seconds() > acceleration:
                    speed -= acceleration * tickrate_time.total_seconds()
                elif (speed - point_speed) / tickrate_time.total_seconds() < acceleration:
                    acceleration = (speed - point_speed) / tickrate_time.total_seconds()
                    speed -= acceleration * tickrate_time.total_seconds()
            else:
                acceleration = 0
            new_latitude, new_longitude = new_point(latitude, longitude, speed, direction, tickrate_time, acceleration)
            next_azimuth = get_bearing([new_latitude, new_longitude], [point['latitude'], point['longitude']])
            if not(math.isclose(next_azimuth, azimuth, abs_tol=5)):
                distance = math.sqrt(((utm_point[0]-utm_destination[0])**2)+((utm_point[1]-utm_destination[1])**2))
                tickrate_time = datetime.timedelta(seconds=distance / speed)
                new_latitude, new_longitude = new_point(latitude, longitude, speed, direction, tickrate_time, acceleration)
            current_time += tickrate_time
            telematic_data.append({
                'timestamp': str(current_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
                'latitude': round(new_latitude, 7),
                'longitude': round(new_longitude, 7),
                'azimuth': round(azimuth, 7),
                'speed': round(speed * 3.6, 2)
            })
            latitude, longitude = new_latitude, new_longitude
            utm_point = utm.from_latlon(new_latitude, new_longitude)
            distance = math.sqrt(((utm_point[0]-utm_destination[0])**2)+((utm_point[1]-utm_destination[1])**2))

        latitude = point['latitude']
        longitude = point['longitude']

    save_to_file(output_fname, config_data['format'], telematic_data)
    
def main():
    parser = argparse.ArgumentParser(description='Generate telematic data')
    parser.add_argument('config_fname', type=str, help='Input config')
    parser.add_argument('output_fname', type=str, help='Output filename without file extension')
    args = parser.parse_args()
    generate(args.config_fname, args.output_fname)
    
if __name__ == "__main__":
        main()