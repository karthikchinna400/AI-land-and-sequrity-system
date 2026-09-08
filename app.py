import streamlit as st
import requests
import math
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Landslide Risk Monitoring",
    page_icon="🌍",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #07111c;
    color: white;
}

.title {
    font-size: 44px;
    font-weight: 800;
}

.subtitle {
    color: #36d399;
    font-size: 19px;
    font-weight: bold;
}

.location-box {
    background: #102330;
    border: 1px solid #36d399;
    border-radius: 15px;
    padding: 22px;
    margin: 20px 0;
}

.card {
    background: #102330;
    border: 1px solid #294253;
    border-radius: 15px;
    padding: 22px;
    text-align: center;
    min-height: 175px;
}

.icon {
    font-size: 38px;
}

.card-title {
    color: #b9c7d0;
    font-size: 16px;
}

.value {
    color: #36d399;
    font-size: 30px;
    font-weight: bold;
    margin: 8px;
}

.small {
    color: #8295a4;
    font-size: 13px;
}

.risk-box {
    background: #102330;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
}

.risk-high {
    color: #ff4d4d;
    font-size: 65px;
    font-weight: bold;
}

.risk-medium {
    color: #f5a623;
    font-size: 65px;
    font-weight: bold;
}

.risk-low {
    color: #36d399;
    font-size: 65px;
    font-weight: bold;
}

.footer {
    text-align: center;
    color: #718493;
    padding: 40px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCTIONS
# =========================================================

def find_location(place):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": place,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    return data["results"][0]


def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "wind_speed_10m"
        ),

        "hourly": (
            "precipitation,"
            "rain,"
            "soil_moisture_0_to_1cm"
        ),

        "forecast_days": 1,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_elevations(latitude, longitude):

    # Center + four nearby points
    points = [
        (latitude, longitude),
        (latitude + 0.001, longitude),
        (latitude - 0.001, longitude),
        (latitude, longitude + 0.001),
        (latitude, longitude - 0.001)
    ]

    latitudes = ",".join(str(p[0]) for p in points)
    longitudes = ",".join(str(p[1]) for p in points)

    url = "https://api.open-meteo.com/v1/elevation"

    params = {
        "latitude": latitudes,
        "longitude": longitudes
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data["elevation"]


def calculate_slope(elevations):

    center = elevations[0]

    north = elevations[1]
    south = elevations[2]
    east = elevations[3]
    west = elevations[4]

    # Approximate distance for 0.001 degree
    distance = 111.0

    north_south_difference = abs(north - south)
    east_west_difference = abs(east - west)

    ns_slope = north_south_difference / (2 * distance)

    ew_slope = east_west_difference / (2 * distance)

    gradient = math.sqrt(
        ns_slope ** 2 +
        ew_slope ** 2
    )

    slope_angle = math.degrees(
        math.atan(gradient)
    )

    return round(slope_angle, 1)


def normalize(value, minimum, maximum):

    value = max(minimum, min(maximum, value))

    return (
        (value - minimum) /
        (maximum - minimum)
    ) * 100


def calculate_risk(
    rainfall,
    soil_moisture,
    slope,
    crack_score
):

    # Rainfall risk
    rainfall_risk = normalize(
        rainfall,
        0,
        10
    )

    # Soil moisture risk
    soil_risk = normalize(
        soil_moisture,
        0.05,
        0.60
    )

    # Slope risk
    slope_risk = normalize(
        slope,
        0,
        45
    )

    # Camera crack risk
    crack_risk = crack_score

    risk = (
        rainfall_risk * 0.35 +
        soil_risk * 0.30 +
        slope_risk * 0.25 +
        crack_risk * 0.10
    )

    risk = round(
        max(0, min(100, risk)),
        1
    )

    if risk >= 65:
        level = "HIGH RISK"
        message = (
            "🚨 High risk conditions detected. "
            "Further field verification is recommended."
        )

    elif risk >= 35:
        level = "MEDIUM RISK"
        message = (
            "⚠️ Moderate risk detected. "
            "Continue monitoring."
        )

    else:
        level = "LOW RISK"
        message = (
            "✅ Current indicators show relatively low risk."
        )

    return risk, level, message


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">🌍 AI Landslide Risk Monitoring System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI + Location Data + Camera + Sensor Fusion</div>',
    unsafe_allow_html=True
)

st.write(
    "Enter any location to retrieve location-specific "
    "environmental data and calculate a landslide risk score."
)

st.divider()


# =========================================================
# LOCATION INPUT
# =========================================================

st.sidebar.header("📍 Location")

place = st.sidebar.text_input(
    "Enter any place",
    placeholder="Example: Ooty, Tirupati, Kerala..."
)

search_button = st.sidebar.button(
    "🔍 Analyze Location"
)


# =========================================================
# SESSION STATE
# =========================================================

if "location_data" not in st.session_state:
    st.session_state.location_data = None


# =========================================================
# SEARCH LOCATION
# =========================================================

if search_button:

    if not place.strip():

        st.sidebar.error(
            "Please enter a location."
        )

    else:

        with st.spinner(
            "Finding location and collecting data..."
        ):

            try:

                location = find_location(place)

                if location is None:

                    st.error(
                        "❌ Location not found. "
                        "Try adding state or country."
                    )

                else:

                    latitude = location["latitude"]
                    longitude = location["longitude"]

                    weather = get_weather(
                        latitude,
                        longitude
                    )

                    elevations = get_elevations(
                        latitude,
                        longitude
                    )

                    slope = calculate_slope(
                        elevations
                    )

                    st.session_state.location_data = {
                        "location": location,
                        "weather": weather,
                        "slope": slope
                    }

            except Exception as e:

                st.error(
                    "Unable to retrieve location data."
                )

                st.caption(
                    f"Technical details: {e}"
                )


# =========================================================
# DISPLAY DATA
# =========================================================

if st.session_state.location_data:

    data = st.session_state.location_data

    location = data["location"]
    weather = data["weather"]
    slope = data["slope"]

    current = weather["current"]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # -----------------------------------------------------
    # LOCATION NAME
    # -----------------------------------------------------

    country = location.get(
        "country",
        ""
    )

    admin = location.get(
        "admin1",
        ""
    )

    location_name = location.get(
        "name",
        place
    )

    full_location = location_name

    if admin:
        full_location += ", " + admin

    if country:
        full_location += ", " + country


    st.markdown(
        f"""
        <div class="location-box">

        <h2>📍 Selected Monitoring Location</h2>

        <h3>{full_location}</h3>

        <p>
        Latitude: {latitude:.4f} |
        Longitude: {longitude:.4f}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # CURRENT VALUES
    # -----------------------------------------------------

    temperature = current.get(
        "temperature_2m",
        0
    )

    humidity = current.get(
        "relative_humidity_2m",
        0
    )

    precipitation = current.get(
        "precipitation",
        0
    )

    rain = current.get(
        "rain",
        0
    )

    wind = current.get(
        "wind_speed_10m",
        0
    )


    # -----------------------------------------------------
    # SOIL MOISTURE
    # -----------------------------------------------------

    hourly = weather.get(
        "hourly",
        {}
    )

    soil_values = hourly.get(
        "soil_moisture_0_to_1cm",
        []
    )

    if soil_values:

        soil_moisture = soil_values[0]

    else:

        soil_moisture = 0


    # -----------------------------------------------------
    # CAMERA CRACK SCORE
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "📷 Upload terrain image for crack analysis",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            caption="Uploaded Terrain",
            use_container_width=True
        )

        st.success(
            "Image uploaded. Connect a trained computer-vision "
            "model here for real crack detection."
        )

        # Demo placeholder until a trained model is connected
        crack_score = 10

    else:

        crack_score = 0


    # -----------------------------------------------------
    # RISK
    # -----------------------------------------------------

    risk, level, message = calculate_risk(
        rain,
        soil_moisture,
        slope,
        crack_score
    )


    # =====================================================
    # ENVIRONMENTAL PARAMETERS
    # =====================================================

    st.header("📡 Live Environmental Parameters")


    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.markdown(
            f"""
            <div class="card">

            <div class="icon">🌧️</div>

            <div class="card-title">
            Current Rain
            </div>

            <div class="value">
            {rain:.1f} mm
            </div>

            <div class="small">
            Previous hour
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="card">

            <div class="icon">💧</div>

            <div class="card-title">
            Soil Moisture
            </div>

            <div class="value">
            {soil_moisture:.2f}
            </div>

            <div class="small">
            m³/m³
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="card">

            <div class="icon">📐</div>

            <div class="card-title">
            Terrain Slope
            </div>

            <div class="value">
            {slope}°
            </div>

            <div class="small">
            Estimated from elevation
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            f"""
            <div class="card">

            <div class="icon">🌡️</div>

            <div class="card-title">
            Temperature
            </div>

            <div class="value">
            {temperature}°C
            </div>

            <div class="small">
            Current
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col5:

        st.markdown(
            f"""
            <div class="card">

            <div class="icon">💨</div>

            <div class="card-title">
            Wind Speed
            </div>

            <div class="value">
            {wind} km/h
            </div>

            <div class="small">
            Current
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # ADDITIONAL INFORMATION
    # =====================================================

    st.subheader("🌦️ Additional Conditions")

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Humidity",
            f"{humidity}%"
        )

    with b:
        st.metric(
            "Precipitation",
            f"{precipitation} mm"
        )

    with c:
        st.metric(
            "Elevation",
            f"{location.get('elevation', 0)} m"
        )


    # =====================================================
    # AI RISK
    # =====================================================

    st.divider()

    st.header("🤖 AI Landslide Risk Analysis")


    risk_col, alert_col = st.columns(2)


    with risk_col:

        if risk >= 65:

            risk_class = "risk-high"

        elif risk >= 35:

            risk_class = "risk-medium"

        else:

            risk_class = "risk-low"


        st.markdown(
            f"""
            <div class="risk-box">

            <p>LANDSLIDE RISK SCORE</p>

            <div class="{risk_class}">
            {risk}%
            </div>

            <h2>{level}</h2>

            </div>
            """,
            unsafe_allow_html=True
        )


    with alert_col:

        st.subheader("🚨 Automatic Assessment")

        if risk >= 65:

            st.error(message)

        elif risk >= 35:

            st.warning(message)

        else:

            st.success(message)


    st.subheader("📊 Risk Probability")

    st.progress(
        int(risk)
    )


    # =====================================================
    # DATA TABLE
    # =====================================================

    st.subheader(
        "📋 Location Data Used by AI"
    )

    table = pd.DataFrame({

        "Parameter": [
            "Rain",
            "Soil Moisture",
            "Terrain Slope",
            "Temperature",
            "Humidity",
            "Wind Speed",
            "Camera Crack Score"
        ],

        "Value": [
            f"{rain:.1f} mm",
            f"{soil_moisture:.2f} m³/m³",
            f"{slope}°",
            f"{temperature}°C",
            f"{humidity}%",
            f"{wind} km/h",
            f"{crack_score}%"
        ]

    })

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # MAP
    # =====================================================

    st.subheader(
        "🗺️ Selected Location"
    )

    st.map(
        pd.DataFrame({
            "latitude": [latitude],
            "longitude": [longitude]
        }),
        zoom=10
    )


else:

    st.info(
        "👈 Enter any location in the sidebar "
        "and click **Analyze Location**."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">

    🌍 <b>AI Landslide Risk Monitoring System</b>

    <br><br>

    Location-based environmental monitoring

    <br><br>

    Data services: Open-Meteo / Copernicus DEM

    </div>
    """,
    unsafe_allow_html=True
)