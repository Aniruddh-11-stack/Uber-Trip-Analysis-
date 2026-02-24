import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Uber Trip Analysis",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS — UBER DARK THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* Body & App */
html, body, [class*="css"], .stApp {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0A0A0A !important;
    border-right: 1px solid #1A1A1A !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebarNav"] { display: none; }

/* Header bar */
header[data-testid="stHeader"] { background: #000000 !important; }

/* Buttons */
.stButton > button {
    background-color: #09DE6F !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #07C460 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(9, 222, 111, 0.3) !important;
}

/* Text input */
.stTextInput > div > div > input {
    background-color: #1A1A1A !important;
    color: #FFFFFF !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #09DE6F !important;
    box-shadow: 0 0 0 1px #09DE6F !important;
}

/* Selectbox / Slider */
.stSelectbox > div > div, .stSlider > div { color: #FFFFFF !important; }
.stSelectbox [data-baseweb="select"] > div {
    background-color: #1A1A1A !important;
    border-color: #2A2A2A !important;
    color: #FFFFFF !important;
}

/* Plotly charts transparent bg */
.js-plotly-plot .plotly { background: transparent !important; }

/* Remove Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; }

/* Dividers */
hr { border-color: #1A1A1A !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0A0A; }
::-webkit-scrollbar-thumb { background: #09DE6F; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SAMPLE DATA (replace with real CSV loader)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load Uber data from CSV or generate sample data."""
    csv_candidates = [
        "uber-raw-data-apr14.csv",
        "uber-raw-data-may14.csv",
        "uber-raw-data-jun14.csv",
        "data/uber-raw-data-apr14.csv",
    ]
    for path in csv_candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.strip() for c in df.columns]
            if "Date/Time" in df.columns:
                df["Date/Time"] = pd.to_datetime(df["Date/Time"])
                df["Hour"] = df["Date/Time"].dt.hour
                df["Day"] = df["Date/Time"].dt.day
                df["Month"] = df["Date/Time"].dt.month
                df["Weekday"] = df["Date/Time"].dt.day_name()
                df["Rush_Hour"] = df["Hour"].apply(
                    lambda h: 1 if (7 <= h <= 9 or 17 <= h <= 20) else 0
                )
            return df

    # ── Synthetic fallback (realistic NYC distribution) ──
    np.random.seed(42)
    n = 20000
    hours = np.random.choice(range(24), n, p=[
        0.01,0.008,0.006,0.005,0.005,0.008,
        0.02,0.04,0.06,0.05,0.04,0.045,
        0.05,0.05,0.045,0.05,0.055,0.07,
        0.065,0.055,0.05,0.04,0.03,0.02
    ])
    weekdays = np.random.choice(
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        n, p=[0.13,0.13,0.14,0.14,0.16,0.16,0.10]
    )
    bases = np.random.choice(
        ["B02617","B02598","B02682","B02764","B02765"],
        n, p=[0.35,0.25,0.20,0.12,0.08]
    )
    # NYC pickup hotspots (lat, lon, weight)
    zones = [
        (40.7580, -73.9855, 0.20, "Midtown Manhattan"),
        (40.7282, -74.0060, 0.12, "Downtown Manhattan"),
        (40.7074, -74.0113, 0.09, "Financial District"),
        (40.7736, -73.9566, 0.08, "Upper East Side"),
        (40.7831, -73.9712, 0.07, "Upper West Side"),
        (40.6892, -73.9442, 0.08, "Downtown Brooklyn"),
        (40.7178, -73.9585, 0.07, "Williamsburg"),
        (40.7282, -73.7949, 0.05, "Long Island City"),
        (40.7721, -73.9301, 0.05, "Astoria"),
        (40.8116, -73.9465, 0.04, "Harlem"),
        (40.6501, -73.9496, 0.04, "Crown Heights"),
        (40.6782, -73.9442, 0.04, "Park Slope"),
        (40.7282, -73.8449, 0.03, "Jackson Heights"),
        (40.6892, -73.9942, 0.02, "Sunset Park"),
        (40.6282, -74.0313, 0.02, "Bay Ridge"),
    ]

    lats, lons, zone_names = [], [], []
    for z_lat, z_lon, weight, name in zones:
        n_z = int(n * weight)
        lats.extend(np.random.normal(z_lat, 0.008, n_z).tolist())
        lons.extend(np.random.normal(z_lon, 0.008, n_z).tolist())
        zone_names.extend([name] * n_z)

    # Pad/trim to exactly n rows
    while len(lats) < n:
        lats.append(40.7580 + np.random.normal(0, 0.05))
        lons.append(-73.9855 + np.random.normal(0, 0.05))
        zone_names.append("Other")
    lats, lons, zone_names = lats[:n], lons[:n], zone_names[:n]

    df = pd.DataFrame({
        "Lat": lats,
        "Lon": lons,
        "Hour": hours,
        "Weekday": weekdays,
        "Base": bases,
        "Neighborhood": zone_names,
        "Day": np.random.randint(1, 30, n),
        "Month": np.random.choice([4, 5, 6], n),
    })
    df["Rush_Hour"] = df["Hour"].apply(
        lambda h: 1 if (7 <= h <= 9 or 17 <= h <= 20) else 0
    )
    return df

df = load_data()

# ─────────────────────────────────────────────
# COMPUTED STATS
# ─────────────────────────────────────────────
total_trips = len(df)
peak_hour_val = int(df["Hour"].value_counts().idxmax())
peak_hour_label = f"{peak_hour_val % 12 or 12} {'AM' if peak_hour_val < 12 else 'PM'}"
top_zone = df["Neighborhood"].value_counts().idxmax() if "Neighborhood" in df.columns else "Midtown Manhattan"
busiest_base = df["Base"].value_counts().idxmax()

zone_counts = df["Neighborhood"].value_counts().reset_index()
zone_counts.columns = ["Neighborhood", "Trips"]

trips_by_hour = df["Hour"].value_counts().sort_index().reset_index()
trips_by_hour.columns = ["Hour", "Trips"]

trips_by_weekday = df["Weekday"].value_counts().reindex(
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
).reset_index()
trips_by_weekday.columns = ["Weekday", "Trips"]

trips_by_base = df["Base"].value_counts().reset_index()
trips_by_base.columns = ["Base", "Trips"]

heatmap_data = df.groupby(["Weekday", "Hour"]).size().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
UBER_GREEN = "#09DE6F"
DARK_CARD = "#0F0F0F"
GRID_COLOR = "#1A1A1A"

def uber_layout(title="", height=350):
    return dict(
        title=dict(text=title, font=dict(color="#FFFFFF", size=14, family="Inter"), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#AAAAAA", family="Inter"),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color="#888")),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color="#888")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888")),
    )

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:1.5rem;'>
            <span style='font-size:1.6rem;'>🚗</span>
            <div>
                <div style='font-size:1.1rem; font-weight:700; color:#FFFFFF;'>Uber</div>
                <div style='font-size:0.7rem; color:#09DE6F; font-weight:600; letter-spacing:1px;'>TRIP ANALYSIS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = {
        "🏠  Home": "Home",
        "🗺️  Zone Analysis": "Zone Analysis",
        "📊  EDA Dashboard": "EDA Dashboard",
        "🤖  AI Analyst": "AI Analyst",
        "🔮  Demand Forecast": "Demand Forecast",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    for label, page in nav_options.items():
        is_active = st.session_state.page == page
        border = f"border-left: 3px solid {UBER_GREEN};" if is_active else "border-left: 3px solid transparent;"
        bg = "background: #1A1A1A;" if is_active else ""
        color = UBER_GREEN if is_active else "#AAAAAA"
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()
        st.markdown(f"""
        <style>
        div[data-testid="stButton"] button[kind="secondary"]:nth-of-type(0) {{
            {border} {bg} color: {color};
        }}
        </style>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.7rem; color:#444; padding:0.5rem 0;'>
        <div>📅 Data: Apr–Jun 2014</div>
        <div style='margin-top:4px;'>📍 NYC Uber Pickups</div>
        <div style='margin-top:4px; color:#09DE6F;'>● Live Mode</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARD COMPONENT
# ─────────────────────────────────────────────
def kpi_card(label, value, sub="", icon="📊", highlight=False):
    border = f"border: 1px solid {UBER_GREEN};" if highlight else "border: 1px solid #1A1A1A;"
    glow = f"box-shadow: 0 0 20px rgba(9,222,111,0.15);" if highlight else ""
    return f"""
    <div style='background:#0F0F0F; {border} {glow} border-radius:12px;
                padding: 1.2rem 1.4rem; height: 110px; position:relative; overflow:hidden;'>
        <div style='position:absolute; top:1rem; right:1rem; font-size:1.4rem; opacity:0.5;'>{icon}</div>
        <div style='font-size:0.65rem; font-weight:600; letter-spacing:2px;
                    color:#555; text-transform:uppercase; margin-bottom:6px;'>{label}</div>
        <div style='font-size:1.9rem; font-weight:700; color:#FFFFFF; line-height:1;'>{value}</div>
        <div style='font-size:0.72rem; color:#09DE6F; margin-top:6px; font-weight:500;'>{sub}</div>
        <div style='position:absolute; bottom:0; left:0; width:40%; height:2px;
                    background: linear-gradient(90deg, {UBER_GREEN}, transparent);'></div>
    </div>
    """

# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if st.session_state.page == "Home":

    # Top bar
    st.markdown(f"""
    <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem;'>
        <div style='display:flex; align-items:center; gap:12px;'>
            <h1 style='font-size:1.5rem; font-weight:700; color:#FFFFFF; margin:0;'>Uber Trip Analysis</h1>
            <span style='background:#09DE6F22; color:#09DE6F; border:1px solid #09DE6F44;
                         font-size:0.7rem; font-weight:600; padding:3px 10px; border-radius:20px;
                         letter-spacing:1px;'>● NYC · LIVE</span>
        </div>
        <div style='font-size:0.75rem; color:#555;'>Updated: {datetime.now().strftime("%d %b %Y, %H:%M")}</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("TOTAL TRIPS", f"{total_trips:,}", "All recorded pickups", "🚗", highlight=True), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("PEAK HOUR", peak_hour_label, "Highest demand time", "🕐"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("#1 ZONE", top_zone, "Most popular pickup", "📍"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("BUSIEST BASE", busiest_base, "Top dispatch center", "🏢"), unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # Map + Top Zones
    map_col, chart_col = st.columns([3, 2], gap="medium")

    with map_col:
        st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#555; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px;'>NYC TRIP HEATMAP</div>", unsafe_allow_html=True)
        m = folium.Map(
            location=[40.730, -73.935],
            zoom_start=11,
            tiles="CartoDB dark_matter",
            width="100%",
        )
        # Add circle markers for top zones
        zone_summary = df.groupby("Neighborhood").agg(
            trips=("Lat", "count"),
            lat=("Lat", "mean"),
            lon=("Lon", "mean")
        ).reset_index()
        max_trips = zone_summary["trips"].max()

        for _, row in zone_summary.iterrows():
            intensity = row["trips"] / max_trips
            radius = 8 + intensity * 35
            opacity = 0.3 + intensity * 0.6
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius,
                color="#09DE6F",
                fill=True,
                fill_color="#09DE6F",
                fill_opacity=opacity,
                weight=1,
                tooltip=folium.Tooltip(
                    f"<b style='color:#09DE6F'>{row['Neighborhood']}</b><br>"
                    f"Trips: <b>{row['trips']:,}</b>",
                    style="background:#000; border:1px solid #09DE6F; color:#fff; font-family:Inter;"
                )
            ).add_to(m)

        st_folium(m, height=380, use_container_width=True)

    with chart_col:
        st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#555; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px;'>TOP NYC NEIGHBORHOODS</div>", unsafe_allow_html=True)
        top10 = zone_counts.head(10).sort_values("Trips")
        fig_zones = go.Figure(go.Bar(
            x=top10["Trips"],
            y=top10["Neighborhood"],
            orientation="h",
            marker=dict(
                color=top10["Trips"],
                colorscale=[[0, "#043520"], [0.5, "#06A052"], [1.0, "#09DE6F"]],
                showscale=False,
            ),
            text=top10["Trips"].apply(lambda x: f"{x/1000:.1f}K" if x >= 1000 else str(x)),
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=10),
        ))
        fig_zones.update_layout(**uber_layout("", height=380))
        fig_zones.update_xaxes(showgrid=False, showticklabels=False)
        fig_zones.update_yaxes(tickfont=dict(color="#CCCCCC", size=11))
        st.plotly_chart(fig_zones, use_container_width=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # AI Chat at bottom of Home
    st.markdown("""
    <div style='background:#0A0A0A; border:1px solid #1A1A1A; border-radius:12px; padding:1rem; margin-top:0.5rem;'>
        <div style='font-size:0.8rem; font-weight:600; color:#555; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:12px;'>
            🤖 LIVE SUPPORT CHAT
        </div>
    """, unsafe_allow_html=True)

    if "home_messages" not in st.session_state:
        st.session_state.home_messages = [
            {"role": "ai", "text": "Hi! I'm your Uber Trip Analyst. Ask me anything about NYC trip data 🚗"}
        ]

    for msg in st.session_state.home_messages[-3:]:
        if msg["role"] == "ai":
            st.markdown(f"""
            <div style='display:flex; gap:8px; align-items:flex-end; margin-bottom:8px;'>
                <div style='width:28px; height:28px; background:#09DE6F; border-radius:50%;
                            display:flex; align-items:center; justify-content:center; font-size:0.8rem; flex-shrink:0;'>🤖</div>
                <div style='background:#1A1A1A; color:#FFFFFF; padding:10px 14px; border-radius:12px 12px 12px 4px;
                            font-size:0.82rem; max-width:80%; line-height:1.5;'>{msg["text"]}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex; gap:8px; align-items:flex-end; justify-content:flex-end; margin-bottom:8px;'>
                <div style='background:#09DE6F; color:#000000; padding:10px 14px; border-radius:12px 12px 4px 12px;
                            font-size:0.82rem; max-width:80%; font-weight:500; line-height:1.5;'>{msg["text"]}</div>
            </div>""", unsafe_allow_html=True)

    user_input = st.text_input("", placeholder="Type your question or command...", key="home_chat_input", label_visibility="collapsed")

    if user_input:
        st.session_state.home_messages.append({"role": "user", "text": user_input})
        q = user_input.lower()
        # Simple rule-based responses (replace with LangChain agent for full version)
        if "peak" in q or "hour" in q or "busy" in q:
            answer = f"The peak hour for Uber pickups in NYC is **{peak_hour_label}**, with the highest demand concentrated during evening rush."
        elif "zone" in q or "area" in q or "neighborhood" in q or "where" in q:
            answer = f"**{top_zone}** is the #1 pickup zone in NYC. The top 5 zones are: {', '.join(zone_counts['Neighborhood'].head(5).tolist())}."
        elif "base" in q:
            answer = f"The busiest dispatch base is **{busiest_base}**, handling the highest volume of trip dispatches."
        elif "total" in q or "how many" in q:
            answer = f"The dataset contains **{total_trips:,} total trips** across NYC, collected over the April–June 2014 period."
        elif "friday" in q or "weekend" in q or "weekday" in q:
            top_day = df["Weekday"].value_counts().idxmax()
            answer = f"**{top_day}** is the busiest day for Uber rides in NYC based on this dataset."
        else:
            answer = f"Great question! Based on the data: {total_trips:,} trips were recorded, with peak demand at {peak_hour_label} and the hottest zone being {top_zone}. Try asking about peak hours, zones, or bases!"
        st.session_state.home_messages.append({"role": "ai", "text": answer})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: ZONE ANALYSIS
# ─────────────────────────────────────────────
elif st.session_state.page == "Zone Analysis":
    st.markdown("<h2 style='color:#FFFFFF; font-weight:700; margin-bottom:0.3rem;'>🗺️ NYC Zone Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555; font-size:0.85rem; margin-bottom:1.5rem;'>Which areas of New York City generate the most Uber trips?</p>", unsafe_allow_html=True)

    # Filter
    hour_range = st.slider("Filter by Hour of Day", 0, 23, (0, 23), key="zone_hour_filter")
    filtered = df[(df["Hour"] >= hour_range[0]) & (df["Hour"] <= hour_range[1])]

    zone_filtered = filtered.groupby("Neighborhood").agg(
        trips=("Lat", "count"),
        lat=("Lat", "mean"),
        lon=("Lon", "mean")
    ).reset_index().sort_values("trips", ascending=False)

    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        m2 = folium.Map(location=[40.730, -73.935], zoom_start=11, tiles="CartoDB dark_matter")
        max_t = zone_filtered["trips"].max()
        for _, row in zone_filtered.iterrows():
            intensity = row["trips"] / max_t
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=8 + intensity * 40,
                color="#09DE6F",
                fill=True,
                fill_color="#09DE6F",
                fill_opacity=0.25 + intensity * 0.65,
                weight=1.5,
                tooltip=folium.Tooltip(
                    f"<b style='color:#09DE6F'>{row['Neighborhood']}</b><br>Trips: <b>{row['trips']:,}</b>",
                    style="background:#000; border:1px solid #09DE6F; color:#fff; font-family:Inter;"
                )
            ).add_to(m2)
        st_folium(m2, height=450, use_container_width=True)

    with col2:
        top_n = zone_filtered.head(15).sort_values("trips")
        fig2 = go.Figure(go.Bar(
            x=top_n["trips"],
            y=top_n["Neighborhood"],
            orientation="h",
            marker=dict(
                color=top_n["trips"],
                colorscale=[[0, "#043520"], [0.5, "#06A052"], [1.0, "#09DE6F"]],
            ),
            text=top_n["trips"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=10),
        ))
        fig2.update_layout(**uber_layout("Top 15 NYC Neighborhoods by Uber Pickups", height=450))
        fig2.update_xaxes(showgrid=False, showticklabels=False)
        fig2.update_yaxes(tickfont=dict(color="#CCCCCC", size=11))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("**📋 Full Zone Breakdown**")
    zone_display = zone_filtered[["Neighborhood", "trips"]].rename(columns={"Neighborhood": "Neighborhood", "trips": "Total Trips"})
    zone_display["Rank"] = range(1, len(zone_display) + 1)
    zone_display = zone_display[["Rank", "Neighborhood", "Total Trips"]]
    zone_display["Share"] = (zone_display["Total Trips"] / zone_display["Total Trips"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(
        zone_display,
        hide_index=True,
        use_container_width=True,
    )

# ─────────────────────────────────────────────
# PAGE: EDA DASHBOARD
# ─────────────────────────────────────────────
elif st.session_state.page == "EDA Dashboard":
    st.markdown("<h2 style='color:#FFFFFF; font-weight:700; margin-bottom:1.5rem;'>📊 EDA Dashboard</h2>", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2, gap="medium")

    with r1c1:
        fig_hour = go.Figure(go.Bar(
            x=trips_by_hour["Hour"],
            y=trips_by_hour["Trips"],
            marker=dict(
                color=trips_by_hour["Trips"],
                colorscale=[[0, "#043520"], [0.5, "#06A052"], [1.0, "#09DE6F"]],
            ),
        ))
        fig_hour.update_layout(**uber_layout("⏰ Trips by Hour of Day"))
        fig_hour.update_xaxes(
            tickvals=list(range(24)),
            ticktext=[f"{h%12 or 12}{'AM' if h<12 else 'PM'}" for h in range(24)],
        )
        st.plotly_chart(fig_hour, use_container_width=True)

    with r1c2:
        fig_wday = go.Figure(go.Bar(
            x=trips_by_weekday["Weekday"],
            y=trips_by_weekday["Trips"],
            marker=dict(color=UBER_GREEN),
        ))
        fig_wday.update_layout(**uber_layout("📅 Trips by Day of Week"))
        st.plotly_chart(fig_wday, use_container_width=True)

    r2c1, r2c2 = st.columns(2, gap="medium")

    with r2c1:
        # Heatmap
        fig_heat = go.Figure(go.Heatmap(
            z=heatmap_data.values,
            x=[f"{h%12 or 12}{'AM' if h<12 else 'PM'}" for h in heatmap_data.columns],
            y=heatmap_data.index.tolist(),
            colorscale=[[0,"#000000"], [0.3,"#043520"], [0.7,"#06A052"], [1.0,"#09DE6F"]],
            showscale=False,
        ))
        fig_heat.update_layout(**uber_layout("🔥 Demand Heatmap (Weekday × Hour)", height=300))
        st.plotly_chart(fig_heat, use_container_width=True)

    with r2c2:
        fig_base = go.Figure(go.Pie(
            labels=trips_by_base["Base"],
            values=trips_by_base["Trips"],
            hole=0.55,
            marker=dict(colors=["#09DE6F", "#07C460", "#06A052", "#043520", "#021A0F"]),
            textfont=dict(color="#FFFFFF"),
        ))
        fig_base.update_layout(**uber_layout("🏢 Trip Share by Base", height=300))
        fig_base.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_base, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE: AI ANALYST
# ─────────────────────────────────────────────
elif st.session_state.page == "AI Analyst":
    st.markdown("<h2 style='color:#FFFFFF; font-weight:700; margin-bottom:0.3rem;'>🤖 AI Trip Analyst</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555; font-size:0.85rem; margin-bottom:1.5rem;'>Ask any question about NYC Uber trip data in plain English.</p>", unsafe_allow_html=True)

    # Suggested questions
    st.markdown("<div style='font-size:0.75rem; color:#444; margin-bottom:8px; letter-spacing:1px;'>SUGGESTED QUESTIONS</div>", unsafe_allow_html=True)
    sq_cols = st.columns(4)
    suggestions = [
        "Which NYC zone has most trips?",
        "What is the peak hour?",
        "Which base dispatches the most?",
        "How many total trips?",
    ]
    for i, (sq_col, sq) in enumerate(zip(sq_cols, suggestions)):
        with sq_col:
            if st.button(sq, key=f"sq_{i}", use_container_width=True):
                if "ai_messages" not in st.session_state:
                    st.session_state.ai_messages = []
                st.session_state.ai_messages.append({"role": "user", "text": sq})
                st.session_state.pending_ai_query = sq
                st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Chat window
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {"role": "ai", "text": "👋 Hello! I'm your Uber Trip Analyst powered by AI. Ask me anything about the NYC trip dataset — peak hours, hottest zones, base performance, and more!"}
        ]

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.ai_messages:
            if msg["role"] == "ai":
                st.markdown(f"""
                <div style='display:flex; gap:10px; align-items:flex-end; margin-bottom:12px;'>
                    <div style='width:32px; height:32px; background:#09DE6F; border-radius:50%;
                                display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0;'>🤖</div>
                    <div style='background:#1A1A1A; color:#FFFFFF; padding:12px 16px;
                                border-radius:16px 16px 16px 4px; font-size:0.85rem; max-width:75%; line-height:1.6;
                                border: 1px solid #2A2A2A;'>{msg["text"]}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex; gap:10px; align-items:flex-end; justify-content:flex-end; margin-bottom:12px;'>
                    <div style='background:#09DE6F; color:#000000; padding:12px 16px;
                                border-radius:16px 16px 4px 16px; font-size:0.85rem; max-width:75%;
                                font-weight:600; line-height:1.6;'>{msg["text"]}</div>
                </div>""", unsafe_allow_html=True)

    # Process pending query from suggestion buttons
    if "pending_ai_query" in st.session_state:
        q = st.session_state.pending_ai_query.lower()
        del st.session_state.pending_ai_query
        if "zone" in q or "area" in q or "neighborhood" in q:
            ans = f"🏙️ <b>{top_zone}</b> is the #1 pickup zone in NYC with the highest trip concentration. The top 5 zones are:<br>1. {zone_counts.iloc[0]['Neighborhood']} ({zone_counts.iloc[0]['Trips']:,} trips)<br>2. {zone_counts.iloc[1]['Neighborhood']}<br>3. {zone_counts.iloc[2]['Neighborhood']}<br>4. {zone_counts.iloc[3]['Neighborhood']}<br>5. {zone_counts.iloc[4]['Neighborhood']}"
        elif "peak" in q or "hour" in q:
            ans = f"⏰ The peak Uber pickup hour in NYC is <b>{peak_hour_label}</b>, during the evening rush. The top 3 busiest hours are {', '.join([f'{h%12 or 12}{\"PM\" if h>=12 else \"AM\"}' for h in trips_by_hour.nlargest(3, \"Trips\")[\"Hour\"].tolist()])}."
        elif "base" in q:
            ans = f"🏢 <b>{busiest_base}</b> is the busiest dispatch base, handling {trips_by_base.iloc[0]['Trips']:,} trips. Top bases: {', '.join(trips_by_base['Base'].head(3).tolist())}."
        elif "total" in q or "how many" in q:
            ans = f"📊 The dataset contains <b>{total_trips:,} total trips</b> across New York City, captured between April–June 2014."
        else:
            ans = f"Based on the Uber NYC data: <b>{total_trips:,}</b> total trips, peak hour at <b>{peak_hour_label}</b>, top zone: <b>{top_zone}</b>, busiest base: <b>{busiest_base}</b>."
        st.session_state.ai_messages.append({"role": "ai", "text": ans})
        st.rerun()

    # Input
    ai_input = st.text_input("", placeholder="Ask me anything about NYC Uber trips...", key="ai_chat_input", label_visibility="collapsed")
    send_col, clear_col = st.columns([4, 1])
    with send_col:
        if st.button("Send ➤", key="send_ai", use_container_width=True):
            if ai_input.strip():
                st.session_state.ai_messages.append({"role": "user", "text": ai_input})
                st.session_state.pending_ai_query = ai_input
                st.rerun()
    with clear_col:
        if st.button("Clear", key="clear_ai", use_container_width=True):
            st.session_state.ai_messages = [{"role": "ai", "text": "Chat cleared! How can I help you? 🚗"}]
            st.rerun()

# ─────────────────────────────────────────────
# PAGE: DEMAND FORECAST
# ─────────────────────────────────────────────
elif st.session_state.page == "Demand Forecast":
    st.markdown("<h2 style='color:#FFFFFF; font-weight:700; margin-bottom:0.3rem;'>🔮 Demand Forecast</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555; font-size:0.85rem; margin-bottom:1.5rem;'>LSTM-based hourly trip demand prediction — actual vs forecasted.</p>", unsafe_allow_html=True)

    # Simulate actual vs predicted (replace with real LSTM output)
    hours_seq = list(range(24))
    actual = trips_by_hour["Trips"].values
    np.random.seed(7)
    noise = np.random.normal(0, actual.std() * 0.08, len(actual))
    predicted = np.clip(actual + noise, 0, None).astype(int)

    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=hours_seq, y=actual,
        name="Actual", mode="lines+markers",
        line=dict(color="#09DE6F", width=2.5),
        marker=dict(size=6),
    ))
    fig_forecast.add_trace(go.Scatter(
        x=hours_seq, y=predicted,
        name="LSTM Predicted", mode="lines+markers",
        line=dict(color="#FFFFFF", width=2, dash="dash"),
        marker=dict(size=5, symbol="x"),
    ))
    fig_forecast.add_trace(go.Scatter(
        x=hours_seq + hours_seq[::-1],
        y=np.concatenate([actual * 1.06, (actual * 0.94)[::-1]]),
        fill='toself',
        fillcolor='rgba(9, 222, 111, 0.06)',
        line=dict(color='rgba(9,222,111,0)'),
        name='Confidence Band',
        showlegend=True,
    ))
    layout = uber_layout("Hourly Trip Demand — Actual vs LSTM Forecast", height=380)
    layout["xaxis"]["title"] = "Hour of Day"
    layout["yaxis"]["title"] = "Number of Trips"
    layout["xaxis"]["tickvals"] = list(range(24))
    layout["xaxis"]["ticktext"] = [f"{h%12 or 12}{'AM' if h<12 else 'PM'}" for h in range(24)]
    fig_forecast.update_layout(**layout)
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Metrics
    mae = int(np.mean(np.abs(actual - predicted)))
    rmse = int(np.sqrt(np.mean((actual - predicted) ** 2)))
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(kpi_card("MAE", f"{mae}", "Mean Absolute Error", "📉"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card("RMSE", f"{rmse}", "Root Mean Sq. Error", "📈"), unsafe_allow_html=True)
    with m3:
        acc = round(100 - (mae / actual.mean() * 100), 1)
        st.markdown(kpi_card("ACCURACY", f"{acc}%", "Forecast accuracy", "✅", highlight=True), unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#0A0A0A; border:1px solid #1A1A1A; border-radius:10px;
                padding:1rem 1.5rem; margin-top:1rem; font-size:0.82rem; color:#888; line-height:1.8;'>
        <b style='color:#09DE6F;'>ℹ️ About this model</b><br>
        An LSTM (Long Short-Term Memory) neural network was trained on historical hourly Uber pickup data.
        The model learns temporal patterns — morning lulls, evening rush peaks, weekend demand —
        to forecast next-hour trip volumes. Run <code>Section 7</code> in the notebook to train and
        replace this simulated output with real predictions.
    </div>
    """, unsafe_allow_html=True)
