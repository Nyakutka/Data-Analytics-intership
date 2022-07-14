# The algorithm for determining speed limit exceedances
## To run script:
    python speeding_events.py "route_filename(route.json)" "road_graph_filename(road_graph.json)" "output_filename(events.json)"
    
## Route
The script gets the route(from generator: https://gitlab.sredasolutions.com:8050/da-internship/2022-summer/smarts-sandbox/-/tree/develop/generator):

## road_graph
The script gets the road_graph: https://gitlab.sredasolutions.com:8050/da-internship/2022-summer/smarts-sandbox/-/blob/develop_road_graph/road_graph.json

## Output
The script generates events of over/under speed limit exceedances - sequence of telematics data consisting of:

Then saves it in json file:
```json
[
    [
        {
            "timestamp": "2022-06-21 14:33:34+00:00"
            "azimuth": 47.6613535
            "point": "POINT (50.240917 53.261877)",
            "over_speed_class": "+(0-20]"
        },
        [
            {
                "timestamp": "2022-06-21 14:33:32+00:00",
                "azimuth": 47.5958395,
                "speed": 43.2,
                "speed_limit": 60,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240492 53.26164)",
                "over_speed_class": null
            },
            ...
            {
                "timestamp": "2022-06-21 14:33:34+00:00",
                "azimuth": 47.6458745,
                "speed": 57.6,
                "speed_limit": 60,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240821 53.261824)",
                "over_speed_class": null
            },
            {
                "timestamp": "2022-06-21 14:33:34+00:00",
                "azimuth": 47.6613535,
                "speed": 61.2,
                "speed_limit": 60,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240917 53.261877)",
                "over_speed_class": "+(0-20]"
            }
        ]
    ],
    [
        {
            "timestamp": "2022-06-21 14:34:27+00:00",
            "azimuth": 319.9258233,
            "point": "POINT (50.240404 53.266883)",
            "over_speed_class": "+(0-20]"
        },
        [
            {
                "timestamp": "2022-06-21 14:34:24+00:00",
                "azimuth": 318.4858583,
                "speed": 40.0,
                "speed_limit": 60,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240669 53.266704)",
                "over_speed_class": null
            },
            ...
            {
                "timestamp": "2022-06-21 14:34:26+00:00",
                "azimuth": 319.2357516,
                "speed": 40.0,
                "speed_limit": 60,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240447 53.266853)",
                "over_speed_class": null
            },
            {
                "timestamp": "2022-06-21 14:34:27+00:00",
                "azimuth": 319.9258233,
                "speed": 40.0,
                "speed_limit": 20,
                "min_speed_limit": 40,
                "geometry": "POINT (50.240404 53.266883)",
                "over_speed_class": "(0-20]"
            }
        ]
    ]
]
```
