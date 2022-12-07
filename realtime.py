"Module to get bus data for a particular stop. "
from urllib import request
from google.transit import gtfs_realtime_pb2
from datetime import datetime, timedelta
from dateutil import tz
import os
from dotenv import load_dotenv
load_dotenv()


NZ_TIMEZONE = tz.gettz('Pacific/Auckland')

class Bus_Line:
    "A bus route, consisting of its code, name, and colour, e.g. (100, The Palms)"
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.colour = "000000"
        with open('./gtfs_static/routes.txt', 'r') as routes:
            stripped = (line.strip() for line in routes)
            lines = list(line.split(',') for line in stripped if line)
            i = 0
            while lines[i][0] != id and i < len(lines):
                i += 1
            if i < len(lines):
                self.colour = lines[i][7]

    def __eq__(self, other):
        if other == None:
            return self.id == None or self.name == None
        return self.id == other.id and self.name == other.name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'[{self.id}] {self.name}'

class Bus:
    "A bus arrival, with a trip id, the bus line that the bus is on, and the arrival time"
    def __init__(self, trip_id=None, bus_line=None, arrival_time=None):
        self.trip_id = trip_id
        self.bus_line = bus_line
        self.arrival_time = arrival_time

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{{trip id: {self.trip_id}, route: {self.bus_line}, arrival time: {self.arrival_time}}}'
    

def nextBus(stop_id):
    buses = []
    canceled = []
    to_delete = []
    data = ["Stop not found", []]

    "Returns a list of the next buses to arrive at the stop."
    stop_id = str(stop_id)

    with open('./gtfs_static/stops.txt', 'r') as stops:
        stripped = (line.strip() for line in stops)
        lines = list(line.split(',') for line in stripped if line)
        i = 0
        while lines[i][0] != stop_id:
            i+=1
            if (i >= len(lines)):
                data[0] = "Bus stop not found"
                return data
        data[0] = lines[i][2]

    # Get realtime buses
    try:
        url = 'https://apis.metroinfo.co.nz/rti/gtfsrt/v1/trip-updates.pb'

        hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': os.environ.get('metro_api_token'),
        }

        # Request data and parse to feed message
        req = request.Request(url, headers=hdr)
        req.get_method = lambda: 'GET'
        response = request.urlopen(req)
        message = response.read()
        feedMessage = gtfs_realtime_pb2.FeedMessage()
        feedMessage.ParseFromString(message)

        for entity in feedMessage.entity:
            status = entity.trip_update.trip.schedule_relationship

            # Check if timetabled bus has been canceled
            if status == 3:
                canceled.append(entity.trip_update.trip.trip_id)
            else:
                for update in entity.trip_update.stop_time_update:
                    if str(update.stop_id) == stop_id:
                        trip_id = entity.trip_update.trip.trip_id
                        bus = Bus()
                        bus.trip_id = trip_id
                        time = datetime.fromtimestamp(update.arrival.time, NZ_TIMEZONE)
                        bus.arrival_time = time
                        buses.append(bus)

    except Exception as e:
        print(e)
        return data
        
    # Get scheduled buses
    with open('./gtfs_static/stop_times.txt', 'r') as trips:
        stripped = (line.strip() for line in trips)
        lines = list(line.split(',') for line in stripped if line)
        for line in lines:
            if line[3] == stop_id:
                # Custom comparison, as Metro provides times such as '24:18:41' to denote the same day
                current_time = datetime.now(tz=tz.gettz('Pacific/Auckland')).time()
                if ((int(line[1][0:2]) > current_time.hour) or 
                    ((int(line[1][0:2]) == current_time.hour) and (int(line[1][3:5]) > current_time.minute)) or 
                    ((int(line[1][0:2]) == current_time.hour) and (int(line[1][3:5]) == current_time.minute) and (int(line[1][6:8]) > current_time.second))):
                    bus = Bus()
                    bus.trip_id = line[0]
                    arrival_time = list(map(int, line[1].split(':')))
                    now = datetime.now(NZ_TIMEZONE)
                    if arrival_time[0] >= 24:
                        arrival_time[0] -= 24
                        arrival_time = datetime(now.year, now.month, now.day, arrival_time[0], arrival_time[1], arrival_time[2], 0, NZ_TIMEZONE)
                        arrival_time += timedelta(days=1)
                    else:
                        arrival_time = datetime(now.year, now.month, now.day, arrival_time[0], arrival_time[1], arrival_time[2], 0, NZ_TIMEZONE)

                    bus.arrival_time = arrival_time
                    if bus.trip_id not in [b.trip_id for b in buses]:
                        buses.append(bus)

    if buses:
        buses.sort(key=lambda x: x.arrival_time)
        weekdate = int(datetime.now(tz=tz.gettz('Pacific/Auckland')).weekday()) + 1
        with open('./gtfs_static/trips.txt', 'r') as trips:
            stripped = (line.strip() for line in trips)
            lines = list(line.split(',') for line in stripped if line)
            for bus in buses:
                i = 0
                while lines[i][2] != bus.trip_id and i < len(lines):
                    i+=1
                with open('./gtfs_static/calendar.txt', 'r') as calendar:
                    strippedc = (linec.strip() for linec in calendar)
                    linesc = list(linec.split(',') for linec in strippedc if linec)
                    if linesc[int(lines[i][1])][weekdate] == '1':
                        bus.bus_line = Bus_Line(lines[i][0], lines[i][3])
                    else:
                        to_delete.append(bus)
        
        for bus in buses:
            difference = (bus.arrival_time - datetime.now(NZ_TIMEZONE)).total_seconds()
            if difference <= 60:
                bus.arrival_time = "DUE"
            elif difference <= 1800:
                bus.arrival_time = f"{int(difference/60)} min"
            else:
                bus.arrival_time = bus.arrival_time.strftime('%I:%M %p')

    data[1] = [bus for bus in buses if bus not in to_delete]
    return data

if __name__ == '__main__':
    for bus in nextBus(17461)[0:10]:
        print(bus)