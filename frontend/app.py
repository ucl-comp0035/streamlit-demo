import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Paralympics Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL to get all the data
API_URL = "http://127.0.0.1:8000/api/paralympics/all"


# --- 2. Data Fetching & Caching ---
@st.cache_data
def load_data():
    """
    Fetch complete data from the backend REST API and convert it to a DataFrame.
    Uses cache_data to prevent re-requesting the API on every page refresh.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            # Basic data cleaning to fill out NaN values
            for col in df.columns:
                df[col] = df[col].fillna(0)
            return df
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return pd.DataFrame()


# --- 3. Frontend logic mimicking REST API ---
# Write functions in the frontend to mimic API route behavior.

def local_get_all(df):
    """Mimic GET /games: Return all data"""
    return df


def local_get_by_id(df, game_id):
    """Mimic GET /games/{id}: Return data for a specific ID"""
    result = df[df['game_id'] == game_id]
    return result.iloc[0] if not result.empty else None


def local_filter_by_type_and_year(df, event_type=None, min_year=1960, max_year=2030):
    """Mimic GET /games?type=...&year_gt=..."""
    filtered_df = df.copy()
    if event_type and event_type != "All":
        filtered_df = filtered_df[filtered_df['event_type'] == event_type.lower()]

    filtered_df = filtered_df[
        (filtered_df['year'] >= min_year) &
        (filtered_df['year'] <= max_year)
        ]
    return filtered_df


# Helper Functions: City Coordinates for Map
# Since the dataset only has City Names, we need this map to plot points.
HOST_COORDINATES = {
    "Rome": {"lat": 41.9028, "lon": 12.4964},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Tel Aviv": {"lat": 32.0853, "lon": 34.7818},
    "Heidelberg": {"lat": 49.3988, "lon": 8.6724},
    "Toronto": {"lat": 43.65107, "lon": -79.347015},
    "Arnhem": {"lat": 51.9851, "lon": 5.8987},
    "Stoke Mandeville": {"lat": 51.8, "lon": -0.81},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "Barcelona": {"lat": 41.3851, "lon": 2.1734},
    "Atlanta": {"lat": 33.7490, "lon": -84.3880},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Athens": {"lat": 37.9838, "lon": 23.7275},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Rio": {"lat": -22.9068, "lon": -43.1729},
    "Örnsköldsvik": {"lat": 63.2905, "lon": 18.7153},
    "Geilo": {"lat": 60.5333, "lon": 8.2076},
    "Innsbruck": {"lat": 47.2692, "lon": 11.4041},
    "Tignes-Albertville": {"lat": 45.67, "lon": 6.39},
    "Lillehammer": {"lat": 61.1153, "lon": 10.4662},
    "Nagano": {"lat": 36.6486, "lon": 138.1942},
    "Salt Lake City": {"lat": 40.7608, "lon": -111.8910},
    "Torino": {"lat": 45.0703, "lon": 7.6869},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    "Sochi": {"lat": 43.6028, "lon": 39.7342},
    "PyeongChang": {"lat": 37.3704, "lon": 128.3902},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Milan": {"lat": 45.4642, "lon": 9.1900},
    "Brisbane": {"lat": -27.4698, "lon": 153.0251},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "French Alps": {"lat": 45.5, "lon": 6.5},  # Approx
}


def get_lat_lon(host_name):
    # Handle combined hosts like "Stoke Mandeville, New York" -> pick first for map
    first_host = host_name.split(',')[0].strip() if host_name else ""
    if str(first_host) in HOST_COORDINATES:
        return HOST_COORDINATES[first_host]['lat'], HOST_COORDINATES[first_host]['lon']
    return None, None


# --- 4. Streamlit UI Main Program ---

def main():
    # A. Sidebar Control Area
    st.sidebar.title("Filter Control")

    # Load Data
    raw_df = load_data()

    if raw_df.empty:
        st.warning("Please ensure the Backend Server is running")
        return

    # Global Filters
    selected_type = st.sidebar.selectbox("Select Event Type", ["All", "Summer", "Winter"])

    # Handle slider range safely
    min_year = int(raw_df['year'].min())
    max_year = int(raw_df['year'].max())
    year_range = st.sidebar.slider("Select Year Range",
                                   min_year,
                                   max_year,
                                   (1960, max_year))

    # Use simulated API functions to process data
    filtered_df = local_filter_by_type_and_year(raw_df, selected_type, year_range[0], year_range[1])

    # B. Header Area
    st.title("Streamlit Demo")
    st.markdown("Interactive dashboard exploring the data of **Paralympic Games.**")

    # C. Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Games Held", len(filtered_df))
    with col2:
        total_participants = int(filtered_df['participants_total'].sum())
        st.metric("Total Athletes", f"{total_participants:,}")
    with col3:
        total_countries = int(filtered_df['countries_count'].sum())
        st.metric("Total Countries", total_countries)
    with col4:
        latest_game = filtered_df.sort_values('year', ascending=False).iloc[0]
        latest_host = latest_game['host']
        st.metric("Latest Host in Range", latest_host)

    st.markdown("---")

    # D. Tabs Layout
    tab1, tab2, tab3 = st.tabs(["Data Visualization", "Gender Analysis", "Game Details"])

    # --- Tab 1: Games Growth Trend Analysis ---
    with tab1:
        st.markdown("#### Total Participants over Years")

        # 1. Line Chart (Altair) - Participants over time
        chart_participants = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('participants_total:Q', title='Total Participants'),
            color=alt.Color('event_type:N', title='Type',
                            scale=alt.Scale(domain=['summer', 'winter'], range=['#ff7f0e', '#1f77b4'])),
            tooltip=['year', 'host', 'participants_total', 'sports']
        ).properties(
            title="Line Chart Example",
            height=400
        ).interactive()

        st.altair_chart(chart_participants, use_container_width=True)

        col_left, col_right = st.columns(2)

        with col_left:
            # 2. Bubble Chart (Plotly) - Sports vs Countries Count
            st.markdown("#### Sports vs. Countries Counts")
            fig_bubble = px.scatter(
                filtered_df,
                x="countries_count",
                y="sports",
                size="participants_total",
                color="event_type",
                hover_name="host",
                log_x=True,
                size_max=40,
                template="streamlit",
                title="Bubble Chart Example"
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
            st.markdown("*Bubble size represents total participants.*")

        with col_right:
            # 3. Map Visualization
            st.markdown("#### Global Host Locations")

            map_df = filtered_df.copy()
            map_df[['lat', 'lon']] = map_df['host'].apply(
                lambda x: pd.Series(get_lat_lon(x))
            )

            if not map_df.empty:
                fig_map = px.scatter_geo(
                    map_df,
                    lat="lat",
                    lon="lon",
                    color="event_type",
                    hover_name="host",
                    hover_data={
                        "lat": False, "lon": False,
                        "year": True,
                        "participants_total": True,
                        "country": True
                    },
                    size="participants_total",  # Dot size based on size of games
                    projection="natural earth",
                    title="Map Example",
                    template="streamlit"
                )
                fig_map.update_geos(showcountries=True, countrycolor="lightgray")
                fig_map.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("No location data available for current selection.")

    # --- Tab 2: Gender Parity Analysis ---
    with tab2:
        st.subheader("Gender Parity Analysis")
        st.markdown("Comparing Male vs Female participation numbers over the years.")

        # Prepare stacked data
        gender_df = filtered_df[['year', 'event_type', 'participants_m', 'participants_f']].copy()
        gender_df = gender_df.melt(id_vars=['year', 'event_type'],
                                   value_vars=['participants_m', 'participants_f'],
                                   var_name='Gender', value_name='Count')

        gender_df['Gender'] = gender_df['Gender'].replace({'participants_m': 'Male', 'participants_f': 'Female'})

        # Stacked Area Chart
        chart_gender = alt.Chart(gender_df).mark_area(opacity=0.6).encode(
            x="year:O",
            y=alt.Y("Count:Q", stack="center"),
            color=alt.Color("Gender:N", scale=alt.Scale(domain=['Male', 'Female'], range=['#1f77b4', '#e377c2'])),
            column="event_type:N",
            tooltip=["year", "Gender", "Count"]
        ).properties(width=350)

        st.altair_chart(chart_gender)

    # --- Tab 3: Game Details  ---
    with tab3:
        st.subheader("Explore Specific Games")

        # 1. Selectbox gets all available Games, formatted as "Year - Host"
        game_options = {f"{row['year']} - {row['host']} ({row['event_type']})": row['game_id']
                        for index, row in raw_df.sort_values('year', ascending=False).iterrows()}

        selected_label = st.selectbox("Select a Game to view details:", list(game_options.keys()))
        selected_id = game_options[selected_label]

        # 2. Call the "Mimic API Function" to get single row
        game_detail = local_get_by_id(raw_df, selected_id)

        if game_detail is not None:
            # Use Expander to show details
            with st.expander("📄 View Full Game Report", expanded=True):
                c1, c2 = st.columns([1, 2])

                with c1:
                    st.info(f"**Host City:** {game_detail['host']}")
                    st.write(f"**Country:** {game_detail['country']}")
                    st.write(f"**Dates:** {game_detail['start_date']} to {game_detail['end_date']}")
                    st.write(f"**Disabilities Included:**")
                    # Convert comma-separated string to tags
                    disabilities = str(game_detail.get('disabilities', '')).split(',')
                    st.write(", ".join([f"`{d.strip()}`" for d in disabilities if d]))

                with c2:
                    st.success(f"**Highlights:** {game_detail['highlights']}")
                    if game_detail['url']:
                        st.markdown(f"[🔗 Official IPC Page]({game_detail['url']})")

                    st.write("**Participation Stats:**")
                    stats_data = pd.DataFrame({
                        'Metric': ['Events', 'Sports', 'Countries'],
                        'Value': [game_detail['events'], game_detail['sports'], game_detail['countries_count']]
                    })
                    st.dataframe(stats_data.set_index('Metric').T, hide_index=True)

    # Footer
    st.markdown("---")
    st.caption("Streamlit Demo for COMP0035")


if __name__ == "__main__":
    main()