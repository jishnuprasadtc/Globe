import json

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
    locations = df.to_dict(orient="records")

    # Create the Plotly figure
    fig = go.Figure()

    # Add the scatter markers for cities and villages
    fig.add_trace(go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        text = df['name'] + '<br>Type: ' + df['type'] + '<br>Pop: ' + df['pop'],
        customdata = df[['name', 'type', 'pop']].to_numpy(),
        marker = dict(
            size = 8,
            color = '#d65a3a',
            line = dict(
                width = 1,
                color = '#fffaf0'
            ),
            symbol = 'circle'
        ),
        hoverinfo = 'text',
        name = 'Locations'
    ))

    fig.update_layout(
        geo = dict(
            projection_type = 'orthographic', # This makes it a 3D globe
            showcoastlines = True,
            coastlinecolor = "#728b78",
            showland = True,
            landcolor = "#c8d8ad",
            showocean = True,
            oceancolor = "#83bfd2",
            showlakes = True,
            lakecolor = "#83bfd2",
            showcountries = True,
            countrycolor = "#9cab8b",
            countrywidth = 0.5,
            bgcolor = 'rgba(0,0,0,0)',
            
            # Initial view configuration (centered on India/Asia)
            projection_rotation = dict(lon=-78, lat=-20, roll=0),
        ),
        paper_bgcolor = '#eaf3f1',
        plot_bgcolor = '#eaf3f1',
        autosize = True,
        margin = dict(l=0, r=0, t=0, b=0)
    )

    output_file = 'index.html'
    print(f"Generating 3D globe and saving to {output_file}...")
    
    post_script = """
    (() => {
      const plot = document.getElementById("{plot_id}");
      const locations = __LOCATIONS__;
      const style = document.createElement("style");
      style.textContent = `
        body { margin: 0; background: #eaf3f1; font-family: Arial, sans-serif; }
        .globe-search {
          position: fixed; z-index: 10; top: 22px; left: 22px; width: min(370px, calc(100vw - 44px));
          box-sizing: border-box; padding: 18px; border: 1px solid #d6e2dc; border-radius: 16px;
          background: rgba(250, 252, 247, .96); box-shadow: 0 8px 28px rgba(38, 65, 67, .18);
        }
        .globe-search h1 { margin: 0 0 5px; color: #243746; font-size: 19px; }
        .globe-search p { margin: 0 0 13px; color: #61736e; font-size: 13px; }
        .globe-search form { display: flex; gap: 8px; }
        .globe-search input {
          min-width: 0; flex: 1; padding: 11px 12px; border: 1px solid #c5d4cd; border-radius: 9px;
          background: #fff; color: #243746; font-size: 14px; outline-color: #538e80;
        }
        .globe-search button {
          padding: 0 14px; border: 0; border-radius: 9px; background: #477e70;
          color: white; font-size: 14px; font-weight: 600; cursor: pointer;
        }
        .globe-search button:hover { background: #35695c; }
        .globe-result { min-height: 20px; margin-top: 12px; color: #405a53; font-size: 13px; line-height: 1.5; }
        .globe-result strong { color: #243746; font-size: 15px; }
        @media (max-width: 520px) { .globe-search { top: 10px; left: 10px; width: calc(100vw - 20px); padding: 13px; } }
      `;
      document.head.appendChild(style);

      const panel = document.createElement("section");
      panel.className = "globe-search";
      panel.innerHTML = `
        <h1>Explore the globe</h1>
        <p>Search a listed city, town, or village to view its details.</p>
        <form>
          <input type="search" list="globe-locations" placeholder="Try Tokyo or Munnar" aria-label="Search locations" />
          <datalist id="globe-locations"></datalist>
          <button type="submit">Search</button>
        </form>
        <div class="globe-result" role="status" aria-live="polite">Search a location or select a marker on the globe.</div>
      `;
      document.body.appendChild(panel);

      const form = panel.querySelector("form");
      const input = panel.querySelector("input");
      const suggestions = panel.querySelector("datalist");
      const result = panel.querySelector(".globe-result");
      locations.forEach((location) => {
        const option = document.createElement("option");
        option.value = location.name;
        suggestions.appendChild(option);
      });

      const showLocation = (location) => {
        input.value = location.name;
        result.innerHTML = "";
        const heading = document.createElement("strong");
        heading.textContent = location.name;
        const details = document.createElement("div");
        details.textContent = `${location.type} · Population ${location.pop} · ${Number(location.lat).toFixed(4)}°, ${Number(location.lon).toFixed(4)}°`;
        result.append(heading, details);
        Plotly.relayout(plot, {
          "geo.projection.rotation.lon": -Number(location.lon),
          "geo.projection.rotation.lat": -Number(location.lat)
        });
      };

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const query = input.value.trim().toLocaleLowerCase();
        const match = locations.find((location) => location.name.toLocaleLowerCase() === query)
          || locations.find((location) => location.name.toLocaleLowerCase().includes(query));
        if (match) {
          showLocation(match);
        } else {
          result.textContent = query
            ? `No listed location matches “${input.value.trim()}”. Try one of the suggestions.`
            : "Enter a location name to search.";
        }
      });

      plot.on("plotly_click", (event) => {
        const point = event.points && event.points[0];
        if (!point || !point.customdata) return;
        const location = locations.find((item) => item.name === point.customdata[0]);
        if (location) showLocation(location);
      });
    })();
    """.replace("__LOCATIONS__", json.dumps(locations, ensure_ascii=False))

    # Write the result to a self-contained HTML file
    fig.write_html(
        output_file, 
        auto_open=False, 
        post_script=post_script,
        config={
            'displayModeBar': False,
            'scrollZoom': True,
            'responsive': True,
        }
    )
    print("Done! You can now open the HTML file in any web browser.")

if __name__ == "__main__":
    create_interactive_globe()
