from influxdb import InfluxDBClient
from geopy.geocoders import Nominatim
from time import sleep
import requests
import config

geolocator = Nominatim(user_agent="myapp")
points = config.points

LOCATIONS = []
for i in points:
    location = geolocator.geocode(i)
    location = str(location.longitude) + ',' + str(location.latitude)
    location = [location, i]
    LOCATIONS.append(location)

CLID = config.clid
APIKEY = config.apikey

INFLUXDBSERVER = config.influxdb_server
INFLUXDBPORT = config.influxdb_port
INFLUXDBUSER = config.influxdb_user
INFLUXDBPASS = config.influxdb_pass
INFLUXDBBASE = config.influxdb_base


def get_price(point_a: list, point_b: list):
    response = requests.get('https://taxi-routeinfo.taxi.yandex.net/taxi_info',
                            params={'clid': CLID,
                                    'apikey': APIKEY,
                                    'rll': point_a[0] + '~' + point_b[0]
                                    }
                            ).json()
    price = response.get('options')[0].get('price')
    json_body = [
        {
            "measurement": "yataxi_price",
            "tags": {
                "source": point_a[1],
                "destination": point_b[1]
            },
            "fields": {
                "value": price
            }
        }
    ]
    client = InfluxDBClient(INFLUXDBSERVER, INFLUXDBPORT, INFLUXDBUSER, INFLUXDBPASS, INFLUXDBBASE)
    client.create_database(INFLUXDBBASE)
    client.write_points(json_body)


def main():
    while True:
        get_price(LOCATIONS[0], LOCATIONS[1])
        get_price(LOCATIONS[1], LOCATIONS[0])
        sleep(300)


if __name__ == '__main__':
    main()
