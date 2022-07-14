# Telematic data generator
## To run script:

    python generator.py "config_filename(config.json)" "output_filename(output)"
    
## Config
The script gets the configuration file(json) with next configurations:
```json
    "format": "CSV", // or JSON
    "frequency": "1", // per second
    "start": {
        "latitude": "53.261382",
        "longitude": "50.240032",
        "time": "2022-06-21T14:33:26+0000"
    },
    "points":[
        {
            "latitude": "53.264023",
            "longitude": "50.244857",
            "speed": "60",      //km/h
            "max_acceleraion": "25920" //km/h^2
        },
        {
            "latitude": "53.266883",
            "longitude": "50.240405",
            "speed": "40",
            "max_acceleraion": "25920"
        }
    ]
}
```

## Output
The script generates a root - sequence of telematics data consisting of:
* Timestamp in ISO format
* Pairs of coordinates(latitude, longitude)
* Azimuth
* Speed

Then saves it in json/csv file:
### JSON
```json
{
    "point": [
        {
            "timestamp": "2022-06-21T14:33:26+00:00",
            "latitude": 53.2613881,
            "longitude": 50.240043,
            "azimuth": 47.5367871,
            "speed": 7.2
        },
        {
            "timestamp": "2022-06-21T14:33:27+00:00",
            "latitude": 53.2614066,
            "longitude": 50.2400758,
            "azimuth": 47.5383939,
            "speed": 14.4
        },
        ...
```
### CSV
```csv
timestamp,latitude,longitude,azimuth,speed
2022-06-21T14:33:27+0000,53.2613881,50.240043,47.5367871,7.2
2022-06-21T14:33:28+0000,53.2614066,50.2400758,47.5383939,14.4
...
```
