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
LOCAL_KANYAKUMARI_BUSES = {
    "Kanyakumari": [
        # Add your Kanyakumari routes here if needed
        {
            "name": "TNSTC Route 1 / Ordinary Town Bus",
            "route": "Kanyakumari ↔ Nagercoil (via Suchindram)",
            "frequency": "Every 10-20 minutes",
            "time_range": "05:00 AM - 10:00 PM",
            "duration": "~30-40 min",
            "price": "₹20-40",
            "stops": [
                {"name": "Kanyakumari Bus Stand", "time": "0 min"},
                {"name": "Vivekananda Rock Memorial / Suchindram Jn", "time": "~5-8 min"},
                {"name": "Suchindram Temple Jn", "time": "~12 min"},
                {"name": "Kottar", "time": "~20 min"},
                {"name": "Vadasery Omni Bus Stand", "time": "~28 min"},
                {"name": "Nagercoil Old Bus Stand", "time": "~30-40 min"}
            ],
            "note": "Main local route - very frequent."
        },
    ],
    "Nagercoil": [
        # Add Nagercoil routes if needed
    ],
    "Thuckalay": [
        {
            "name": "TNSTC Ordinary / Local (Route 7G / 11 series variant)",
            "route": "Thuckalay ↔ Vadasery (Nagercoil)",
            "frequency": "Every 10-25 minutes (peak: every 10 min)",
            "time_range": "05:00 AM - 10:00 PM",
            "duration": "~20-35 min",
            "price": "₹15-30",
            "stops": [
                {"name": "Thuckalay Bus Stand / Jn", "time": "0 min"},
                {"name": "Thuckalay Market / Post Office", "time": "~2 min"},
                {"name": "Thuckalay Temple / Church area", "time": "~3-4 min"},
                {"name": "Kaliyankadu Jn / Cross", "time": "~5-7 min"},
                {"name": "Parvathipuram / Parvathipuram Jn", "time": "~8-11 min"},
                {"name": "Parvathipuram Market stop", "time": "~10 min"},
                {"name": "Kattaiyanvilai / Kattathurai link", "time": "~13-15 min"},
                {"name": "Vettunirmadam / Vettunir Madom Cross", "time": "~16-19 min"},
                {"name": "Vettunirmadam Temple area", "time": "~18 min"},
                {"name": "Krishnancoil / Krishnan Coil Jn", "time": "~20-23 min"},
                {"name": "Krishnancoil Small stop", "time": "~22 min"},
                {"name": "Vadasery (Nagercoil Omni Bus Stand)", "time": "~25-35 min"}
            ],
            "note": "Super frequent short local route; full during school/office hours. Stops often on request at tiny spots."
        },
        {
            "name": "TNSTC Local Extended (Thuckalay to Nagercoil Old Stand)",
            "route": "Thuckalay ↔ Nagercoil (Old Bus Stand / Meenashipuram)",
            "frequency": "Every 15-30 minutes",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~30-45 min",
            "price": "₹20-35",
            "stops": [
                {"name": "Thuckalay Bus Stand", "time": "0 min"},
                {"name": "Thuckalay Jn / Temple", "time": "~3 min"},
                {"name": "Kaliyankadu", "time": "~6 min"},
                {"name": "Parvathipuram Jn", "time": "~9 min"},
                {"name": "Vettunirmadam Cross", "time": "~15 min"},
                {"name": "Krishnancoil", "time": "~20 min"},
                {"name": "Vadasery Omni Stand", "time": "~25 min"},
                {"name": "Meenashipuram area", "time": "~30 min"},
                {"name": "Nagercoil Old Bus Stand / Town", "time": "~35-45 min"}
            ],
            "note": "Continues into old Nagercoil town; good for market/shopping areas."
        },
        {
            "name": "TNSTC Ordinary / Local",
            "route": "Thuckalay ↔ Marthandam",
            "frequency": "Every 10-25 minutes",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~15-25 min",
            "price": "₹10-20",
            "stops": [
                {"name": "Thuckalay Bus Stand / Jn", "time": "0 min"},
                {"name": "Thuckalay Market area", "time": "~2 min"},
                {"name": "Azhagiyamandapam Jn", "time": "~6-8 min"},
                {"name": "Azhagiyamandapam Temple stop", "time": "~9 min"},
                {"name": "Marthandam Bus Stand", "time": "~15-25 min"}
            ],
            "note": "Very frequent short route connecting Thuckalay and Marthandam."
        },

        {
            "name": "TNSTC Local / Ordinary",
            "route": "Thuckalay ↔ Kaliyakkavilai",
            "frequency": "Every 20-40 minutes",
            "time_range": "06:00 AM - 08:30 PM",
            "duration": "~25-40 min",
            "price": "₹20-35",
            "stops": [
                {"name": "Thuckalay Bus Stand", "time": "0 min"},
                {"name": "Azhagiyamandapam", "time": "~7 min"},
                {"name": "Marthandam Bus Stand", "time": "~15 min"},
                {"name": "Kaliyakkavilai Jn / Bus Stand", "time": "~25-40 min"}
            ],
            "note": "Common route via Marthandam; many services continue to Kaliyakkavilai."
        },

        {
            "name": "TNSTC Ordinary / Coastal",
            "route": "Thuckalay ↔ Karungal",
            "frequency": "Every 30-60 minutes",
            "time_range": "06:30 AM - 08:00 PM",
            "duration": "~35-55 min",
            "price": "₹25-45",
            "stops": [
                {"name": "Thuckalay Bus Stand", "time": "0 min"},
                {"name": "Azhagiyamandapam", "time": "~8 min"},
                {"name": "Monday Market / Puthukkadai", "time": "~20 min"},
                {"name": "Colachel Bus Stand", "time": "~30 min"},
                {"name": "Karungal Bus Stand", "time": "~35-55 min"}
            ],
            "note": "Via Colachel; frequency lower than main routes."
        }
        
    ],
    "Azhagiyamandapam": [
        {
            "name": "TNSTC Local / Ordinary (Route 16D variant)",
            "route": "Azhagiyamandapam ↔ Colachel",
            "frequency": "Every 30-60 minutes (peak higher)",
            "time_range": "06:00 AM - 08:30 PM",
            "duration": "~40-65 min",
            "price": "₹30-55",
            "stops": [
                {"name": "Azhagiyamandapam Bus Stop / Jn", "time": "0 min"},
                {"name": "Azhagiyamandapam Temple / Church", "time": "~3 min"},
                {"name": "Swamiyarmadam / Samiyarmadam Cross", "time": "~6-10 min"},
                {"name": "Swamiyarmadam Small stop", "time": "~8 min"},
                {"name": "Kattuthurai / Kattathurai Jn", "time": "~12-15 min"},
                {"name": "Kattuthurai Village", "time": "~14 min"},
                {"name": "Attoor / Atoor Village", "time": "~18-22 min"},
                {"name": "Attoor Temple area", "time": "~20 min"},
                {"name": "Unnamalaikadai / Unnamalai Kadai", "time": "~25-28 min"},
                {"name": "Payanam / Payyanam Jn", "time": "~30 min"},
                {"name": "Sirayankuzhi / Sirayan Kuzhi", "time": "~33-35 min"},
                {"name": "Monday Market / Puthukkadai Guram Jn", "time": "~40-45 min"},
                {"name": "Puthukkadai Small market", "time": "~42 min"},
                {"name": "Colachel Bus Stand", "time": "~45-65 min"}
            ],
            "note": "Rural-coastal path; stops at panchayat/small village points."
        },
        # Add the second variant if you want
    ],
    "Vadasery": [
       {
            "name": "TNSTC Route 1 / Ordinary",
            "route": "Vadasery ↔ Nagercoil Old Bus Stand / Town",
            "frequency": "Every 5-15 minutes",
            "time_range": "05:00 AM - 10:30 PM",
            "duration": "~5-12 min",
            "price": "₹10-15",
            "stops": [
                {"name": "Vadasery Omni Bus Stand", "time": "0 min"},
                {"name": "Vadasery Jn / Link Road", "time": "~2 min"},
                {"name": "Meenashipuram area", "time": "~4-6 min"},
                {"name": "Nagercoil Old Bus Stand / Town Center", "time": "~7-12 min"}
            ],
            "note": "Ultra-short shuttle within Nagercoil area - extremely frequent."
        },

        {
            "name": "TNSTC Ordinary / Main Connector",
            "route": "Vadasery ↔ Kanyakumari",
            "frequency": "Every 10-20 minutes",
            "time_range": "05:00 AM - 10:00 PM",
            "duration": "~30-40 min",
            "price": "₹20-40",
            "stops": [
                {"name": "Vadasery Omni Bus Stand", "time": "0 min"},
                {"name": "Meenashipuram", "time": "~5 min"},
                {"name": "Kottar", "time": "~10 min"},
                {"name": "Suchindram Bye Pass", "time": "~18 min"},
                {"name": "Kanyakumari Bus Stand", "time": "~30-40 min"}
            ],
            "note": "Main route to Kanyakumari tourist area."
        },

        {
            "name": "TNSTC Local / Ordinary",
            "route": "Vadasery ↔ Marthandam",
            "frequency": "Every 15-30 minutes",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~35-50 min",
            "price": "₹25-40",
            "stops": [
                {"name": "Vadasery Omni Stand", "time": "0 min"},
                {"name": "Krishnancoil", "time": "~5 min"},
                {"name": "Vettunirmadam", "time": "~12 min"},
                {"name": "Thuckalay Jn", "time": "~25 min"},
                {"name": "Marthandam Bus Stand", "time": "~35-50 min"}
            ],
            "note": "Via Thuckalay to Marthandam."
        },

        {
            "name": "TNSTC Ordinary",
            "route": "Vadasery ↔ Colachel",
            "frequency": "Every 20-40 minutes",
            "time_range": "Early morning to evening",
            "duration": "~45-65 min",
            "price": "₹30-50",
            "stops": [
                {"name": "Vadasery Omni Stand", "time": "0 min"},
                {"name": "Monday Market / Puthukkadai", "time": "~20 min"},
                {"name": "Karungal Jn", "time": "~30 min"},
                {"name": "Colachel Bus Stand", "time": "~45-65 min"}
            ],
            "note": "Coastal route to Colachel."
        },

        {
            "name": "TNSTC Local / Extended",
            "route": "Vadasery ↔ Kaliyakkavilai",
            "frequency": "Every 30-60 minutes",
            "time_range": "06:00 AM - 08:00 PM",
            "duration": "~50-75 min",
            "price": "₹40-60",
            "stops": [
                {"name": "Vadasery Omni Stand", "time": "0 min"},
                {"name": "Thuckalay", "time": "~20 min"},
                {"name": "Marthandam", "time": "~35 min"},
                {"name": "Kaliyakkavilai Bus Stand", "time": "~50-75 min"}
            ],
            "note": "Extended route via Marthandam."
        },
    ],
    "Parvathipuram": [
        {
            "name": "TNSTC Local Segment / Pass-through",
            "route": "Parvathipuram ↔ Nagercoil (Vadasery / Old Stand)",
            "frequency": "Every 10-30 minutes (as part of main route)",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~15-25 min",
            "price": "₹10-25",
            "stops": [
                {"name": "Parvathipuram Jn / Stop", "time": "0 min"},
                {"name": "Parvathipuram Market area", "time": "~2-3 min"},
                {"name": "Vettunirmadam Cross", "time": "~8-10 min"},
                {"name": "Krishnancoil", "time": "~12-15 min"},
                {"name": "Vadasery Omni Bus Stand", "time": "~20-25 min"}
            ],
            "note": "Frequently passed point on Thuckalay–Nagercoil route."
        },

        {
            "name": "TNSTC Local Segment",
            "route": "Parvathipuram ↔ Marthandam / Thuckalay",
            "frequency": "Every 15-35 minutes",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~20-35 min",
            "price": "₹15-30",
            "stops": [
                {"name": "Parvathipuram", "time": "0 min"},
                {"name": "Kattaiyanvilai Jn", "time": "~5 min"},
                {"name": "Thuckalay Bus Stand", "time": "~12-15 min"},
                {"name": "Azhagiyamandapam", "time": "~18 min"},
                {"name": "Marthandam Bus Stand", "time": "~25-35 min"}
            ],
            "note": "Common segment toward Marthandam side."
        },

        {
            "name": "TNSTC Ordinary (via Parvathipuram)",
            "route": "Parvathipuram ↔ Colachel / Karungal",
            "frequency": "Every 30-60 minutes",
            "time_range": "06:00 AM - 08:00 PM",
            "duration": "~40-65 min",
            "price": "₹30-50",
            "stops": [
                {"name": "Parvathipuram", "time": "0 min"},
                {"name": "Thuckalay Jn", "time": "~10 min"},
                {"name": "Monday Market / Puthukkadai", "time": "~25 min"},
                {"name": "Colachel Bus Stand", "time": "~40 min"},
                {"name": "Karungal Bus Stand", "time": "~45-65 min"}
            ],
            "note": "Via Thuckalay to coastal side."
        },
    ],
    "Marthandam": [
        {
            "name": "TNSTC Ordinary / Local",
            "route": "Marthandam ↔ Nagercoil (main stand)",
            "frequency": "Every 15-30 minutes",
            "time_range": "05:30 AM - 09:30 PM",
            "duration": "~30-45 min",
            "price": "₹20-35",
            "stops": [
                {"name": "Marthandam Bus Stand", "time": "0 min"},
                {"name": "Azhagiyamandapam", "time": "~8 min"},
                {"name": "Thuckalay Jn", "time": "~15 min"},
                {"name": "Vadasery (Nagercoil main stand)", "time": "~30-45 min"}
            ],
            "note": "Frequent route to Nagercoil."
        },

        {
            "name": "TNSTC Ordinary",
            "route": "Marthandam ↔ Kanyakumari",
            "frequency": "Every 20-40 minutes",
            "time_range": "06:00 AM - 08:30 PM",
            "duration": "~45-65 min",
            "price": "₹30-50",
            "stops": [
                {"name": "Marthandam Bus Stand", "time": "0 min"},
                {"name": "Thuckalay", "time": "~10 min"},
                {"name": "Thengampudur", "time": "~20 min"},
                {"name": "Kanyakumari Bus Stand", "time": "~45-65 min"}
            ],
            "note": "Via Thuckalay to Kanyakumari main stand."
        },

        {
            "name": "TNSTC Local",
            "route": "Marthandam ↔ Colachel",
            "frequency": "Every 30-60 minutes",
            "time_range": "Morning to evening",
            "duration": "~45-70 min",
            "price": "₹35-55",
            "stops": [
                {"name": "Marthandam Bus Stand", "time": "0 min"},
                {"name": "Azhagiyamandapam", "time": "~8 min"},
                {"name": "Thuckalay", "time": "~15 min"},
                {"name": "Monday Market / Puthukkadai", "time": "~30 min"},
                {"name": "Colachel Bus Stand", "time": "~45-70 min"}
            ],
            "note": "Via Thuckalay to Colachel."
        },

        {
            "name": "TNSTC Fast / Ordinary",
            "route": "Marthandam ↔ Kaliyakkavilai",
            "frequency": "Every 20-45 minutes",
            "time_range": "06:00 AM - 08:00 PM",
            "duration": "~20-35 min",
            "price": "₹15-30",
            "stops": [
                {"name": "Marthandam Bus Stand", "time": "0 min"},
                {"name": "Kaliyakkavilai Jn / Bus Stand", "time": "~20-35 min"}
            ],
            "note": "Short direct route."
        },
    ],
    "Colachel": [
       {
            "name": "TNSTC Local Loop / Ordinary",
            "route": "Colachel ↔ Monday Market / Puthukkadai / Colachel Guram",
            "frequency": "Every 20-45 minutes",
            "time_range": "06:00 AM - 08:30 PM",
            "duration": "~10-25 min",
            "price": "₹10-20",
            "stops": [
                {"name": "Colachel Bus Stand", "time": "0 min"},
                {"name": "Colachel Market / Church area", "time": "~3 min"},
                {"name": "Monday Market Jn", "time": "~6-8 min"},
                {"name": "Puthukkadai / Guram area", "time": "~10 min"},
                {"name": "Colachel Guram stop", "time": "~12-15 min"},
                {"name": "Colachel Bus Stand (loop back)", "time": "~15-25 min"}
            ],
            "note": "Short circular/local route connecting Colachel town area."
        },

        {
            "name": "TNSTC Ordinary",
            "route": "Colachel ↔ Nagercoil (main stand)",
            "frequency": "Every 20-40 minutes",
            "time_range": "05:30 AM - 09:00 PM",
            "duration": "~40-60 min",
            "price": "₹30-50",
            "stops": [
                {"name": "Colachel Bus Stand", "time": "0 min"},
                {"name": "Monday Market / Puthukkadai", "time": "~6 min"},
                {"name": "Thingal Nagar", "time": "~12 min"},
                {"name": "Karungal Jn", "time": "~18 min"},
                {"name": "Vadasery (Nagercoil main stand)", "time": "~40-60 min"}
            ],
            "note": "Main route to Nagercoil Vadasery Omni Bus Stand."
        },

        {
            "name": "TNSTC Local / Ordinary",
            "route": "Colachel ↔ Kanyakumari",
            "frequency": "Every 30-60 minutes",
            "time_range": "06:00 AM - 08:00 PM",
            "duration": "~50-75 min",
            "price": "₹40-60",
            "stops": [
                {"name": "Colachel Bus Stand", "time": "0 min"},
                {"name": "Rajakkamangalam", "time": "~10 min"},
                {"name": "Manakudy / Anjugramam", "time": "~20 min"},
                {"name": "Chothavilai Beach Jn", "time": "~30 min"},
                {"name": "Kanyakumari Bus Stand", "time": "~50-75 min"}
            ],
            "note": "Coastal route to Kanyakumari main stand."
        },

        {
            "name": "TNSTC Ordinary via Marthandam",
            "route": "Colachel ↔ Marthandam",
            "frequency": "Every 40-70 minutes",
            "time_range": "Morning to evening",
            "duration": "~45-70 min",
            "price": "₹35-55",
            "stops": [
                {"name": "Colachel Bus Stand", "time": "0 min"},
                {"name": "Monday Market", "time": "~8 min"},
                {"name": "Karungal", "time": "~15 min"},
                {"name": "Thuckalay Jn", "time": "~30 min"},
                {"name": "Azhagiyamandapam", "time": "~40 min"},
                {"name": "Marthandam Bus Stand", "time": "~45-70 min"}
            ],
            "note": "Via Karungal & Thuckalay to Marthandam."
        },
    ],
    "default": [
        {
            "name": "No detailed data available",
            "route": "",
            "frequency": "",
            "time_range": "",
            "duration": "",
            "price": "",
            "stops": [],
            "note": "Sorry, we don't have specific local bus information for this place yet. Try popular places like Thuckalay, Nagercoil, Kanyakumari, Colachel or visit the nearest TNSTC bus stand."
        }
    ]
}


def get_coordinates(place_name):
    """
    Free geocoding using Nominatim (OpenStreetMap)
    Returns (lat, lon) or (None, None) if not found
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{place_name}, Kanyakumari, Tamil Nadu, India",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ZestRide-App/1.0 (your.email@example.com)"  # Required by Nominatim policy
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None
    except Exception as e:
        print(f"Geocoding error for {place_name}: {e}")
        return None, None
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
        {"name": "Sunrise Travels", "type": "Non-AC Seater", "departure": "07:00 AM", "arrival": "01:00 PM", "price": 1000},
        {"name": "City Morning Ride", "type": "AC Sleeper", "departure": "08:30 AM", "arrival": "02:30 PM", "price": 1400},
    ]

    afternoon_buses = [
        {"name": "Day Rider", "type": "AC Seater", "departure": "12:30 PM", "arrival": "06:30 PM", "price": 950},
        {"name": "Fast Afternoon", "type": "Non-AC Seater", "departure": "02:00 PM", "arrival": "08:00 PM", "price": 750},
        {"name": "Comfort Day Bus", "type": "AC Sleeper", "departure": "03:30 PM", "arrival": "09:30 PM", "price": 2000},
    ]

    night_buses = [
        {"name": "Night Deluxe", "type": "AC Sleeper", "departure": "09:00 PM", "arrival": "05:30 AM", "price": 1350},
        {"name": "Late Night Express", "type": "Non-AC Sleeper", "departure": "10:30 PM", "arrival": "06:30 AM", "price": 800},
        {"name": "Royal Night Rider", "type": "AC Sleeper", "departure": "11:45 PM", "arrival": "07:45 AM", "price": 1500},
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
# ================= NEW SEPARATE ROUTE FOR LOCAL SEARCH =================
@app.route('/local')
def local():
    place = request.args.get('place', '').strip().title()
    
    if not place:
        place = "Kanyakumari"  # default if nothing entered

    bus_list = LOCAL_KANYAKUMARI_BUSES.get(place, LOCAL_KANYAKUMARI_BUSES["default"])

    return render_template(
        'local.html',
        place=place,
        buses=bus_list,
        is_local=True
    )
# ================= stop details =================
@app.route('/stops')
def stops():
    place = request.args.get('place', '').strip().title()
    route_name = request.args.get('route', '').strip()

    bus_list = LOCAL_KANYAKUMARI_BUSES.get(place, [])
    selected_bus = next((bus for bus in bus_list if bus['route'] == route_name), None)

    if not selected_bus or not selected_bus.get('stops'):
        return render_template('stops.html', place=place, route=route_name, stops=[])

    # Enrich stops with real coordinates
    enriched_stops = []
    for stop in selected_bus['stops']:
        lat, lon = get_coordinates(stop['name'])
        enriched_stop = stop.copy()
        enriched_stop['lat'] = lat
        enriched_stop['lon'] = lon
        enriched_stops.append(enriched_stop)

    return render_template(
        'stops.html',
        place=place,
        route=route_name,
        stops=enriched_stops
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
