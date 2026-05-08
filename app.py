from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import timedelta
app = Flask(__name__)

# ================= API CONFIG =================
API_KEY = "3276fab6d3079d8589b36216c7a896fd"
ROUTE_URL = "https://capi.busmaps.com:8443/routes"

HEADERS = {
    "capi-key": f"Bearer {API_KEY}",
    "capi-host": "busmaps.com"
}


# ================= HELPER: CITY → LAT,LON =================
def get_latlon(city):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "bus-project-app"
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)

        if res.status_code != 200:
            print("Nominatim error:", res.text)
            return None

        data = res.json()

        if len(data) > 0:
            return f"{data[0]['lat']},{data[0]['lon']}"

    except Exception as e:
        print("LatLon error:", e)

    return None


# ================= HOME PAGE =================
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for(
            'buses',
            origin=request.form['from'],
            destination=request.form['to'],
            date=request.form['date'],
            time=request.form['time']
        ))
    return render_template('home.html')


# ================= BUS LIST PAGE =================
@app.route('/buses')
def buses():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    travel_time = request.args.get('time')  # HH:MM

    # ===== BUS DATA =====
    morning_buses = [
        {"name": "Morning Express", "type": "AC Seater", "departure": "06:00 AM", "arrival": "12:00 PM", "price": 900},
        {"name": "Sunrise Travels", "type": "Non-AC Seater", "departure": "07:00 AM", "arrival": "01:00 PM", "price": 700},
        {"name": "City Morning Ride", "type": "AC Sleeper", "departure": "08:30 AM", "arrival": "02:30 PM", "price": 1000},
    ]

    afternoon_buses = [
        {"name": "Day Rider", "type": "AC Seater", "departure": "12:30 PM", "arrival": "06:30 PM", "price": 950},
        {"name": "Fast Afternoon", "type": "Non-AC Seater", "departure": "02:00 PM", "arrival": "08:00 PM", "price": 750},
        {"name": "Comfort Day Bus", "type": "AC Sleeper", "departure": "03:30 PM", "arrival": "09:30 PM", "price": 1100},
    ]

    night_buses = [
        {"name": "Night Deluxe", "type": "AC Sleeper", "departure": "09:00 PM", "arrival": "05:30 AM", "price": 1350},
        {"name": "Late Night Express", "type": "Non-AC Sleeper", "departure": "10:30 PM", "arrival": "06:30 AM", "price": 800},
        {"name": "Royal Night Rider", "type": "AC Sleeper", "departure": "11:45 PM", "arrival": "07:45 AM", "price": 1400},
    ]

    # ===== TIME FILTER =====
    bus_list = []

    if travel_time:
        hour = int(travel_time.split(":")[0])

        if 5 <= hour < 12:
            bus_list = morning_buses
        elif 12 <= hour < 18:
            bus_list = afternoon_buses
        else:
            bus_list = night_buses

    return render_template(
        'buses.html',
        buses=bus_list,
        origin=origin,
        destination=destination,
        selected_time=travel_time   # ✅ send to UI
    )



# ================= SEAT SELECTION =================
@app.route('/seats', methods=['POST'])
def seats():
    return render_template(
        'seats.html',
        bus=request.form['bus'],
        base_price=int(request.form['price']),
        origin=request.form['origin'],
        destination=request.form['destination']
    )


# ================= ID PROOF PAGE =================
@app.route('/idproof', methods=['POST'])
def idproof():
    seats = request.form.getlist('seats')
    total_price = request.form.get('total_price', 0)

    return render_template(
        'idproof.html',
        seats=seats,
        total_price=total_price,
        origin=request.form['origin'],
        
        destination=request.form['destination']
    )


# ================= ROUTE DISPLAY PAGE =================

@app.route('/route', methods=['POST'])
def route():
    origin_city = request.form['origin']
    dest_city = request.form['destination']

    origin_latlon = get_latlon(origin_city)
    dest_latlon = get_latlon(dest_city)

    stops = []
    duration_text = "Route not found"
    route_coords = []

    if origin_latlon and dest_latlon:
        try:
            # swap to lon,lat for OSRM
            o_lat, o_lon = origin_latlon.split(",")
            d_lat, d_lon = dest_latlon.split(",")

            origin = f"{o_lon},{o_lat}"
            dest = f"{d_lon},{d_lat}"

            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{origin};{dest}?overview=full&geometries=geojson"
            res = requests.get(osrm_url, timeout=10)

            if res.status_code == 200:
                data = res.json()

                if data.get("routes"):
                    route_info = data["routes"][0]

                    # ===== duration =====
                    total_minutes = route_info["duration"] / 60
                    hours = int(total_minutes // 60)
                    minutes = int(total_minutes % 60)
                    duration_text = f"{hours} hr {minutes} min"

                    # ===== geometry coords =====
                    coords = route_info["geometry"]["coordinates"]
                    route_coords = [[lat, lon] for lon, lat in coords]

                    # ===== sample stop points =====
                    sample_points = coords[:: max(1, len(coords)//8)]

                    seen = set()

                    # divide time across stops
                    step_minutes = total_minutes / max(1, len(sample_points))

                    for i, (lon, lat) in enumerate(sample_points):
                        try:
                            rev_url = "https://nominatim.openstreetmap.org/reverse"
                            params = {"lat": lat, "lon": lon, "format": "json"}
                            headers = {"User-Agent": "bus-project-app"}

                            r = requests.get(rev_url, params=params, headers=headers, timeout=5)

                            if r.status_code == 200:
                                address = r.json().get("address", {})

                                name = (
                                    address.get("city")
                                    or address.get("town")
                                    or address.get("village")
                                    or address.get("state_district")
                                )

                                if name and name not in seen:
                                    seen.add(name)

                                    # ===== arrival time =====
                                    arrival = timedelta(minutes=i * step_minutes)
                                    h, m = divmod(arrival.seconds // 60, 60)
                                    time_text = f"{h:02d}:{m:02d}"

                                    stops.append({
                                        "name": name,
                                        "lat": lat,
                                        "lon": lon,
                                        "time": time_text
                                    })

                        except:
                            continue

        except Exception as e:
            print("Route error:", e)

    return render_template(
        "route.html",
        stops=stops,
        duration=duration_text,
        route_coords=route_coords,
        origin=origin_city,
        destination=dest_city
    )

# ================= SUCCESS PAGE =================
@app.route('/success')
def success():
    return render_template('success.html')


# ================= RUN APP =================
if __name__ == '__main__':
    app.run(debug=True)
