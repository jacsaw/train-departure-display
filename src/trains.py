import csv
import requests
import whenever
from google.transit import gtfs_realtime_pb2


# Move to config.py?
BEACON_STOP = {"id": "46", "code": "0BC", "name": "Beacon"}

URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr"

HUDSON_LINE_ROUTE_ID = "1"
BEACON_STOP = {"id": "46", "code": "0BC", "name": "Beacon"}
GRAND_CENTRAL_STOP = {"id": "1", "code": "0NY", "name": "Grand Central Terminal"}
PEEKSKILL_STOP = {"id": "39", "code": "0PE", "name": "Peekskill"}
COLDSPRING_STOP = {"id": "43", "code": "0CS", "name": "Cold Spring"}
NEWHAMBURGH_STOP = {"id": "49", "code": "0NH", "name": "New Hamburg"}
POUGHKEEPSIE_STOP = {"id": "51", "code": "0PK", "name": "Poughkeepsie"}

with open("src/data/mnr/stops.txt", "r") as file:
    reader = csv.DictReader(file)
    stop_list = [row for row in reader]
    STOPS = {stop["stop_id"]: stop["stop_name"] for stop in stop_list}

def ProcessDepartures(journeyConfig, feed):
    # This function processes the API output and returns a list of departures
    show_individual_departure_time = journeyConfig["individualStationDepartureTime"]

    now = whenever.ZonedDateTime.now("America/New_York")

    print(f"Current Time: {now.timestamp()}")

    # print("GTFS Realtime Data:")
    departures = []
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            # Display Only Hudson Line Trips
            if entity.trip_update.trip.route_id == HUDSON_LINE_ROUTE_ID:
                trip_stops = {stu.stop_id: stu for stu in entity.trip_update.stop_time_update}
                if BEACON_STOP["id"] in trip_stops:
                    departure_time = whenever.Instant.from_timestamp(trip_stops[BEACON_STOP["id"]].departure.time)
                    # arrival time at beacon
                    if departure_time > now:
                        trip_update = entity.trip_update
                        # print(f"Trip ID: {trip_update.trip.trip_id}") # don't care about this, api/internal use only I think
                        trip_direction = "Northbound" if trip_update.stop_time_update[0].stop_id == GRAND_CENTRAL_STOP["id"] else "Southbound"
                        service = {
                            "destination": STOPS[trip_update.stop_time_update[-1].stop_id],
                            "direction": trip_direction,
                            "stopping_at": [],
                            "departure_time": trip_stops[BEACON_STOP["id"]].departure.time,
                            "delay": trip_stops[BEACON_STOP["id"]].departure.delay,
                        }
                        
                        stops = []
                        if trip_direction == "Northbound":
                            for stop in trip_update.stop_time_update:
                                if stop.stop_id in [NEWHAMBURGH_STOP["id"], POUGHKEEPSIE_STOP["id"]]:
                                    stops.append(stop)
                        else:
                            
                            for stop in trip_update.stop_time_update:
                                if stop.stop_id not in [BEACON_STOP["id"], NEWHAMBURGH_STOP["id"], POUGHKEEPSIE_STOP["id"]]:
                                    stops.append(stop)
                        service["stopping_at"] = ", ".join([STOPS[x.stop_id] for x in stops if x.stop_id != BEACON_STOP["id"]])
                        departures.append(service)
    
    return sorted(departures, key=lambda dep: dep["departure_time"])

def fetch_gtfs_data():
    """Fetch GTFS Realtime data from MTA API."""
    # headers = {"x-api-key": API_KEY}  # MTA API requires the x-api-key header # no longer required for MTA API
    headers = {}
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        return response.content  # Return raw Protobuf data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def loadDeparturesForStation(journeyConfig, apiKey=None, rows=0):
    data = fetch_gtfs_data()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)  # Decode Protobuf

    now = whenever.Instant.now()

    if journeyConfig["departureStation"] == "":
        raise ValueError(
            "Please configure the departureStation environment variable")

    departureStationName = BEACON_STOP["name"]

    Departures = ProcessDepartures(journeyConfig, feed)

    return Departures, departureStationName
