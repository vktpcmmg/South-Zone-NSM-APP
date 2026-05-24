import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from math import radians, sin, cos, asin, sqrt
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

import base64
def get_current_location():
    components.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const latitude = Number(position.coords.latitude.toFixed(6));
                const longitude = Number(position.coords.longitude.toFixed(6));

                const params = new URLSearchParams(window.location.search);
                params.set("lat", lat);
                params.set("lon", lon);

                window.location.search = params.toString();
            },
            (err) => {
                const params = new URLSearchParams(window.location.search);
                params.set("lat", "ERROR");
                window.location.search = params.toString();
            }
        );
        </script>
        """,
        height=0,
    )

def load_logo():
    with open("tata_logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = load_logo()

st.markdown(
    f"""
    <div style="text-align:center; padding-top:10px; padding-bottom:5px;">
        <img src="data:image/png;base64,{logo_base64}" 
             style="width:160px; max-width:90%; height:auto;">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Non-Smart Meter Data Search App",
    page_icon="🔍",
    layout="wide"
)


# --- Title & Subtitle for Consumer App ---
st.markdown(
    """
    <h1 style='text-align: center; color: #0F172A; font-weight: 900;'>
        🔍 Consumer Search App
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h4 style='text-align: center; color: #6b7280; margin-top: -10px;'>
        <span style='color:#0072C6; font-weight:700;'>Tata Power - MIT South & City Zone</span> | Non-Smart Meter Consumer Data Search & Navigation 
    </h4>
    <br>
    """,
    unsafe_allow_html=True
)

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    /* Center main block */
    .main-container {
        max-width: 1100px;
        margin: 0 auto;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    /* Big title card */
    .hero-card {
        background: linear-gradient(135deg, #f5f7ff, #eef3ff);
        padding: 2rem 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        margin-bottom: 2.5rem;
        text-align: left;
    }
    .hero-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
    }
    .record-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background-color: #111827;
        color: #f9fafb;
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.8rem;
        margin-top: 0.75rem;
    }

    /* Section title */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.75rem 0 0.5rem 0;
        color: #111827;
    }

    /* Result card */
    .result-card {
        background: #ffffff;
        border-radius: 1.25rem;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.10);
        border: 1px solid #e5e7eb;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }
    .result-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        color: #111827;
    }
    .field-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        margin-bottom: 0.1rem;
    }
    .field-value {
        font-size: 0.98rem;
        font-weight: 500;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    /* Google Maps button */
    .map-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background-color: #2563eb;
        color: #f9fafb !important;
        text-decoration: none !important;
        padding: 0.55rem 0.95rem;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .map-btn:hover {
        background-color: #1d4ed8;
        color: #f9fafb !important;
    }
    .map-icon {
        font-size: 1.1rem;
    }

    /* Download button area */
    .download-caption {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.35rem;
    }

    /* Reduce default padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- SIMPLE LOGIN LAYER (ADDED) ----------

# ---------- GOOGLE SHEET LOGGING SETUP ----------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope,
)

client = gspread.authorize(creds)
sheet = client.open("App_Access_Log").sheet1

# ---------- LOG FUNCTION (INDIAN TIME) ----------

def log_activity(user, action):
    ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    sheet.append_row([
        ist_time.strftime("%d-%m-%Y %I:%M:%S %p IST"),
        user,
        action
    ])

#--------------Download Limit Function-------------
MAX_DOWNLOADS_PER_DAY = 15

def check_download_limit(user):
    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y")

    records = sheet.get_all_values()
    count = 0

    for row in records:
        if row[0].startswith(today) and row[1] == user and row[2] == "Download":
            count += 1

    return count

# ---------- MULTI USER LOGIN SYSTEM ----------

USERS = {
    "user7": {"password": "MIT@123"},
    "user8": {"password": "MIT@234"},
    "user9": {"password": "MIT@345"},
    "admin": {"password": "MITSZ@123"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

def show_login():
    st.title("🔐 Secure Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username

            log_activity(username, "Login")

            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    show_login()
    st.stop()

# ---------- SHOW DOWNLOAD USAGE ----------

download_count = check_download_limit(st.session_state.user)
remaining_downloads = MAX_DOWNLOADS_PER_DAY - download_count

st.markdown("### 🔐 Download Usage Today")

if remaining_downloads > 0:
    st.success(
        f"User: {st.session_state.user} | "
        f"Downloads used: {download_count} / {MAX_DOWNLOADS_PER_DAY} | "
        f"Remaining: {remaining_downloads}"
    )
else:
    st.error("⚠ Daily download limit reached (15 downloads).")





# ---------- DATA LOADING ----------
@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_excel("bigfile.xlsx")
    df.columns = df.columns.str.strip()

    if "Logitude" in df.columns:
        df = df.rename(columns={"Logitude": "Longitude"})

    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    return df


df = load_data()

total_records = len(df)

# ---------- ROUTE PLANNER LIMITS ----------
MAX_METERS_TOTAL = 100        # absolute cap for any route planning
MAX_METERS_PER_ROUTE = 9      # meters per route (start + 9 = 10 stops in Google Maps)


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points (km)."""
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def build_route(start_lat, start_lon, meters_df):
    """Greedy nearest-neighbour route starting from given point."""
    remaining = meters_df.copy()
    current_lat, current_lon = float(start_lat), float(start_lon)
    route_rows = []
    total_dist = 0.0
    step = 1

    while not remaining.empty:
        remaining["__dist__"] = remaining.apply(
            lambda r: haversine_km(
                current_lat,
                current_lon,
                r["Latitude"],
                r["Longitude"],
            ),
            axis=1,
        )
        next_idx = remaining["__dist__"].idxmin()
        next_row = remaining.loc[next_idx]
        step_dist = float(next_row["__dist__"])
        total_dist += step_dist

        route_rows.append(
            {
                "Order": step,
                "Meter No.": next_row.get("Meter No.", ""),
                "CA No.": next_row.get("CA No.", ""),
                "Address": next_row.get("Address", ""),
                "Latitude": next_row["Latitude"],
                "Longitude": next_row["Longitude"],
                "Distance from previous (km)": round(step_dist, 2),
                "Cumulative distance (km)": round(total_dist, 2),
            }
        )

        current_lat, current_lon = next_row["Latitude"], next_row["Longitude"]
        remaining = remaining.drop(index=next_idx)
        step += 1

    return pd.DataFrame(route_rows)


# ---------- SAFETY LIMITS ----------
# Maximum number of rows we allow for a single search.
# If a search returns more than this, we ask the user to refine it.
SAFE_MAX_ROWS = 50_000   # you can adjust this (e.g. 30_000 or 100_000)

def chunk_rows(df_rows, chunk_size):
    """
    Split a DataFrame into chunks of size <= chunk_size.
    Returns a list of smaller DataFrames.
    """
    chunks = []
    for start in range(0, len(df_rows), chunk_size):
        chunks.append(df_rows.iloc[start:start + chunk_size])
    return chunks

# ---------- LAYOUT START ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# HERO CARD
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">Consumer Search App</div>
        <div class="hero-subtitle">
            Search any consumer using Meter No., CA No., MF, Portion and more – 
            see full details and jump directly to Google Maps.
        </div>
        <div class="record-pill">
            <span>🧾</span>
            <span><strong>Total records:</strong> {total_records:,}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- SEARCH SECTION ----------
st.markdown('<div class="section-title">Search consumer data</div>', unsafe_allow_html=True)

col_search1, col_search2, col_search3 = st.columns([1.2, 1.2, 0.6])
# ✅ Allowed search columns only
SEARCH_COLUMNS = [
    "Meter No.",
    "Building ID",
    "Building Name",
    "MRU",
]

SEARCH_COLUMNS = [c for c in SEARCH_COLUMNS if c in df.columns]

with col_search1:
    selected_column = st.selectbox(
        "Select column to search",
        options=SEARCH_COLUMNS,
        index=0,  # Default = Meter No.
        key="column_select",
    )


with col_search2:
    search_value = st.text_input(
        f"Enter value for '{selected_column}'",
        key="search_value",
    )

with col_search3:
    st.write("")  # spacing
    st.write("")
    do_search = st.button("🔍 Search", use_container_width=True)

filtered_df = pd.DataFrame()

if do_search:
    if not search_value.strip():
        st.warning("Please enter a value to search.")
    else:
        # Build mask
        mask = (
            df[selected_column]
            .astype(str)
            .str.strip()
            .str.contains(search_value.strip(), case=False, na=False)
        )

        match_count = int(mask.sum())

        if match_count == 0:
            st.error("No records found for the given value.")
        elif match_count > SAFE_MAX_ROWS:
            # Too many rows – block this search
            st.error(
                f"Your search returned **{match_count:,}** records, "
                f"which is above the safe limit of **{SAFE_MAX_ROWS:,}**.\n\n"
                "Please narrow your search (e.g. use full Meter No., CA No., "
                "or add more characters)."
            )
            filtered_df = pd.DataFrame()  # keep empty so rest of app does nothing
        else:
            filtered_df = df[mask]
            st.success(
                f"Found **{match_count:,}** matching record(s). "
                "Showing the first one below."
            )


# ---------- RESULT CARD ----------
if not filtered_df.empty:
    # take first row for the card view
    row = filtered_df.iloc[0]

    lat = row.get("Latitude", None)
    lon = row.get("Longitude", None)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">Result</div>', unsafe_allow_html=True)

    # Arrange fields in columns
    c1, c2 = st.columns(2)

    with c1:

        st.markdown('<div class="field-label">Consumer Category</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Consumer Category", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Consumer Name</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Consumer Name", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Contracted Load</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Contracted Load", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Meter No.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Meter No.", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">Cons Mobile</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Cons Mobile", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Building Name</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Building Name", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">MRU</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("MRU", "")}</div>', unsafe_allow_html=True)


    with c2:
        st.markdown('<div class="field-label">Consumer type</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Consumer type", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Zone</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Zone", "")}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Latitude</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{lat}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Longitude</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{lon}</div>', unsafe_allow_html=True)

        st.markdown('<div class="field-label">Device Location Description</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Device Location Description", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">Building ID</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Building ID", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="field-label">Meter Type</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row.get("Meter Type", "")}</div>', unsafe_allow_html=True)
        


    # Address full width
    st.markdown('<div class="field-label">Address</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value">{row.get("Address", "")}</div>', unsafe_allow_html=True)

    # Google Maps button
    if pd.notna(lat) and pd.notna(lon):
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        st.markdown(
            f"""
            <a href="{maps_url}" target="_blank" class="map-btn">
                <span class="map-icon">📍</span>
                <span>Open in Google Maps</span>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)  # close result-card

    # ---------- DOWNLOAD SECTION ----------
    # ---------- DOWNLOAD SECTION ----------
        # ---------- DOWNLOAD SECTION ----------
    st.markdown("#### Download filtered result")

    download_df = filtered_df.copy()

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        download_df.to_excel(writer, index=False, sheet_name="Filtered Data")
    buffer.seek(0)

    if remaining_downloads > 0:
        st.download_button(
            label="⬇️ Download filtered result as Excel",
            data=buffer,
            file_name="filtered_consumer_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            on_click=log_activity,
            args=(st.session_state.user, "Download"),
        )
    else:
        st.warning("Download limit reached for today.")

    st.markdown(
        '<div class="download-caption">File will contain all matching rows with the same columns as your original Excel.</div>',
        unsafe_allow_html=True,
    )

    MAX_DISPLAY_ROWS = 10_000

    with st.expander(
        f"See first {min(len(download_df), MAX_DISPLAY_ROWS):,} "
        f"of {len(download_df):,} matching rows"
    ):
        st.dataframe(download_df.head(MAX_DISPLAY_ROWS), use_container_width=True)

        
# ---------- ROUTE PLANNER SECTION ----------
# ---------- ROUTE PLANNER (AUTO-GROUP ONLY) ----------
st.markdown(
    '<div class="section-title">Plan field visit route (auto-group)</div>',
    unsafe_allow_html=True,
)

with st.expander("🗺️ Route planner (auto-group up to 100 meters)"):

    # ---- start / office coordinates ----
    c1, c2 = st.columns(2)
    with c1:
        start_lat = st.number_input(
            "Start latitude", format="%.6f", value=19.076090  # example: Mumbai
        )
    with c2:
        start_lon = st.number_input(
            "Start longitude", format="%.6f", value=72.877426  # example
        )

    st.caption(
        "Tip: copy your office / sub-station coordinates from Google Maps and paste here."
    )

    # ---- meters input ----
    meter_input = st.text_area(
        "Enter Meter Nos. (comma separated) – max 100 meters",
        placeholder="LSC000841, LSC000842, LSC000843 ...",
        key="auto_group_input",
        height=100,
    )

    if st.button("Create auto-grouped route", key="btn_auto_group"):
        if not meter_input.strip():
            st.warning("Please enter at least one Meter No.")
        else:
            # Turn text into list of meter IDs
            meter_list = [m.strip() for m in meter_input.split(",") if m.strip()]

            # 🔒 100-meter safety cap
            if len(meter_list) > MAX_METERS_TOTAL:
                st.warning(
                    f"You entered {len(meter_list)} meters. "
                    f"Only the first {MAX_METERS_TOTAL} will be used."
                )
                meter_list = meter_list[:MAX_METERS_TOTAL]

            # Filter main dataframe for these meters
            meters_df = df[df["Meter No."].astype(str).isin(meter_list)].copy()

            if meters_df.empty:
                st.error("No matching meters found in data for the given Meter Nos.")
            else:
                # Need coordinates to build a route
                meters_df = meters_df.dropna(subset=["Latitude", "Longitude"])
                if meters_df.empty:
                    st.error("Selected meters do not have Latitude/Longitude data.")
                else:
                    # ---- build ONE continuous route for all meters ----
                    full_route = build_route(start_lat, start_lon, meters_df)

                    st.success(
                        f"Route calculated for {len(full_route)} meter(s). "
                        f"Auto-grouping into chunks of up to {MAX_METERS_PER_ROUTE} meters."
                    )

                    # Split the ordered route into groups of up to MAX_METERS_PER_ROUTE
                    route_groups = chunk_rows(full_route, MAX_METERS_PER_ROUTE)

                    # We’ll keep track of our position in the full route
                    start_index = 0

                    for i, group_df in enumerate(route_groups, start=1):
                        # Starting point for this group:
                        #   - group 1: office / start_lat, start_lon
                        #   - other groups: last meter of previous group
                        if i == 1:
                            seg_start_lat, seg_start_lon = start_lat, start_lon
                        else:
                            prev_row = full_route.iloc[start_index - 1]
                            seg_start_lat = prev_row["Latitude"]
                            seg_start_lon = prev_row["Longitude"]

                        with st.expander(f"Route {i} – {len(group_df)} meter(s)"):
                            # Show the ordered meters with distance columns
                            st.dataframe(
                                group_df[
                                    [
                                        "Order",
                                        "Meter No.",
                                        "CA No.",
                                        "Address",
                                        "Latitude",
                                        "Longitude",
                                        "Distance from previous (km)",
                                        "Cumulative distance (km)",
                                    ]
                                ],
                                use_container_width=True,
                            )

                            # Build Google Maps URL for this segment
                            coord_strings = [f"{seg_start_lat},{seg_start_lon}"] + [
                                f"{row.Latitude},{row.Longitude}"
                                for row in group_df.itertuples()
                            ]
                            maps_url = (
                                "https://www.google.com/maps/dir/"
                                + "/".join(coord_strings)
                            )

                            st.markdown(
                                f"""
                                <a href="{maps_url}" target="_blank" class="map-btn">
                                    <span class="map-icon">🗺️</span>
                                    <span>Open this route segment in Google Maps</span>
                                </a>
                                """,
                                unsafe_allow_html=True,
                            )

                        # Move start index forward for the next group
                        start_index += len(group_df)
                        
#--------------------------------Current Location Logic-----------------------------------                       
# -------------------------------- Current Location Logic --------------------------------
st.markdown(
    '<div class="section-title">📍 Nearest meters from my location</div>',
    unsafe_allow_html=True,
)

with st.expander("Show nearest 100 meters on map"):

    # ================== FILTERS (BEFORE LOCATION) ==================
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        meter_type_options = ["All"] + sorted(
            df["Meter Type"].dropna().unique().tolist()
        )
        selected_meter_type = st.selectbox(
            "Select Meter Type",
            meter_type_options,
        )

    with col_f2:
        consumer_type_options = ["All"] + sorted(
            df["Consumer type"].dropna().unique().tolist()
        )
        selected_consumer_type = st.selectbox(
            "Select Consumer Type",
            consumer_type_options,
        )

    st.divider()

    # ================== LOCATION INPUT ==================
# ================== AUTO + MANUAL LOCATION INPUT ==================

st.markdown("### 📍 Location Input")

# ---------- AUTO FETCH BUTTON ----------
if st.button("📡 Auto Fetch My Current Location"):
    get_current_location()

# ---------- READ URL PARAMS ----------
query_params = st.query_params

auto_lat = 0.0
auto_lon = 0.0

try:
    if "lat" in query_params and "lon" in query_params:
        auto_lat = float(query_params["lat"])
        auto_lon = float(query_params["lon"])

        st.success(
            f"Location fetched successfully → "
            f"Lat: {auto_lat:.6f}, Lon: {auto_lon:.6f}"
        )

except:
    st.warning("Location permission denied or GPS unavailable.")

# ---------- MANUAL ENTRY ----------
col1, col2 = st.columns(2)

with col1:
    user_lat = st.number_input(
        "Your current latitude",
        format="%.6f",
        value=auto_lat,
        help="Auto-filled from GPS OR enter manually",
        key="user_latitude",
    )

with col2:
    user_lon = st.number_input(
        "Your current longitude",
        format="%.6f",
        value=auto_lon,
        help="Auto-filled from GPS OR enter manually",
        key="user_longitude",
    )
    

    # ================== ACTION ==================
    if st.button("📍 Find nearest 100 meters"):

        if user_lat == 0 or user_lon == 0:
            st.warning("Please enter valid latitude and longitude.")

        else:
            # ------------------ Base data with coordinates ------------------
            meters_filtered = df.dropna(
                subset=["Latitude", "Longitude"]
            ).copy()

            # ------------------ APPLY FILTERS ------------------
            if selected_meter_type != "All":
                meters_filtered = meters_filtered[
                    meters_filtered["Meter Type"] == selected_meter_type
                ]

            if selected_consumer_type != "All":
                meters_filtered = meters_filtered[
                    meters_filtered["Consumer type"] == selected_consumer_type
                ]

            if meters_filtered.empty:
                st.error("No meters found for selected filters.")
                st.stop()

            # ------------------ Distance calculation ------------------
            meters_filtered["Distance_km"] = meters_filtered.apply(
                lambda r: haversine_km(
                    user_lat,
                    user_lon,
                    r["Latitude"],
                    r["Longitude"],
                ),
                axis=1,
            )

            # ------------------ Nearest 100 ------------------
            nearest_100 = (
                meters_filtered
                .sort_values("Distance_km")
                .head(100)
                .reset_index(drop=True)
            )

            # ================== MAP SECTION ==================
            st.subheader("🗺️ Nearest 100 meters (map)")

            map_df = nearest_100.copy()
            map_df["Latitude"] = pd.to_numeric(map_df["Latitude"], errors="coerce")
            map_df["Longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")
            map_df = map_df.dropna(subset=["Latitude", "Longitude"])

            map_df = map_df.rename(
                columns={
                    "Latitude": "lat",
                    "Longitude": "lon",
                }
            )

            if map_df.empty:
                st.warning("Map cannot be shown: no valid latitude/longitude found.")
            else:
                st.map(map_df[["lat", "lon"]])

            # ================== LIST SECTION ==================
            st.subheader("📋 Nearest 100 meters list")

            show_df = nearest_100[
                [
                    "Meter No.",
                    "Consumer Name",
                    "Building ID",
                    "Building Name",
                    "Consumer type",
                    "Meter Type",
                    "Address",
                    "Distance_km",
                ]
            ].copy()

            show_df.insert(0, "Sr No.", range(1, len(show_df) + 1))
            show_df["Distance_km"] = show_df["Distance_km"].round(2)

            # Google Maps link
            show_df["Google Maps"] = nearest_100.apply(
                lambda r: f'<a href="https://www.google.com/maps?q={r["Latitude"]},{r["Longitude"]}" target="_blank">📍 Open Map</a>',
                axis=1,
            )

            st.markdown(
                show_df[
                    [
                        "Sr No.",
                        "Meter No.",
                        "Building Name",
                        "Building ID",
                        "Distance_km",
                        "Consumer Name",
                        "Consumer type",
                        "Meter Type",
                        "Address",
                        "Google Maps",
                    ]
                ].to_html(index=False, escape=False),
                unsafe_allow_html=True,
            )

            # ================== DOWNLOAD ==================
            from io import BytesIO

            download_df = show_df.copy()
            download_df["Google Maps"] = download_df["Google Maps"].str.extract(
                r'href="([^"]+)"'
            )

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                download_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Nearest_100_Meters",
                )

            buffer.seek(0)

            if remaining_downloads > 0:
                st.download_button(
                    "⬇️ Download Nearest 100 Meters List (Excel)",
                    data=buffer,
                    file_name="nearest_100_meters.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    on_click=log_activity,
                    args=(st.session_state.user, "Download"),
                )
            else:
                st.warning("Download limit reached for today.")

st.markdown("</div>", unsafe_allow_html=True)  # close main-container
