import plotly.graph_objects as go
import pandas as pd

def fetch_city_data():
    """
    Returns a small, predefined dataset of major cities and smaller settlements.

    The data is static; this function does not call GeoNames or another API.
    """
    print("Loading geographic data...")
    # A robust starter dataset of major cities worldwide
    cities = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "pop": "20.96M", "type": "City"},
        {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "pop": "32.94M", "type": "Capital"},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "pop": "13.19M", "type": "City"},
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "pop": "37.27M", "type": "Capital"},
        {"name": "London", "lat": 51.5074, "lon": -0.1278, "pop": "8.98M", "type": "Capital"},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060, "pop": "8.38M", "type": "City"},
        {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "pop": "5.31M", "type": "City"},
        {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241, "pop": "4.61M", "type": "City"},
        {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "pop": "6.74M", "type": "City"},
        {"name": "Dubai", "lat": 25.2048, "lon": 55.2708, "pop": "3.33M", "type": "City"},
        # Adding some smaller towns/villages as requested
        {"name": "Munnar", "lat": 10.0892, "lon": 77.0597, "pop": "32k", "type": "Town"},
        {"name": "Kaza", "lat": 32.2276, "lon": 78.0700, "pop": "3.2k", "type": "Village"},
        {"name": "Zermatt", "lat": 46.0207, "lon": 7.7491, "pop": "5.8k", "type": "Town"},
    ]
    return pd.DataFrame(cities)

def create_interactive_globe():
    df = fetch_city_data()

    # Create the Plotly figure
    fig = go.Figure()

    # Add the scatter markers for cities and villages
    fig.add_trace(go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        text = df['name'] + '<br>Type: ' + df['type'] + '<br>Pop: ' + df['pop'],
        marker = dict(
            size = 8,
            color = 'rgb(56, 189, 248)', # Light blue color for the dots
            line = dict(
                width = 1,
                color = 'rgba(255, 255, 255, 0.8)'
            ),
            symbol = 'circle'
        ),
        hoverinfo = 'text',
        name = 'Locations'
    ))

    fig.update_layout(
        title = dict(
            text = 'Interactive 3D Globe Viewer<br><sup>Drag to rotate, scroll to zoom. Hover for details.</sup>',
            font = dict(family="Arial", size=24, color="white"),
            x=0.5, y=0.95
        ),
        geo = dict(
            projection_type = 'orthographic', # This makes it a 3D globe
            showcoastlines = True,
            coastlinecolor = "rgba(100, 116, 139, 0.8)",
            showland = True,
            landcolor = "rgba(15, 23, 42, 1)",      # Dark land mass
            showocean = True,
            oceancolor = "rgba(2, 6, 23, 1)",       # Very dark ocean
            showlakes = True,
            lakecolor = "rgba(2, 6, 23, 1)",
            showcountries = True,
            countrycolor = "rgba(51, 65, 85, 0.5)",
            countrywidth = 0.5,
            bgcolor = 'rgba(0,0,0,0)', # Transparent background for the globe itself
            
            # Initial view configuration (centered on India/Asia)
            projection_rotation = dict(lon=78, lat=20, roll=0),
        ),
        paper_bgcolor = '#020617', # Overall background color (Slate 950)
        plot_bgcolor = '#020617',
        autosize = True,
        margin = dict(l=0, r=0, t=0, b=0)
    )

    output_file = 'interactive_globe.html'
    print(f"Generating 3D globe and saving to {output_file}...")
    
    # Write the result to a self-contained HTML file
    fig.write_html(
        output_file, 
        auto_open=False, 
        config={
            'displayModeBar': False,
            'scrollZoom': True,
            'responsive': True,
        }
    )
    print("Done! You can now open the HTML file in any web browser.")

if __name__ == "__main__":
    create_interactive_globe()
