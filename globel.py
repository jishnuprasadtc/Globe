import json
from pathlib import Path


def fetch_city_data():
    """Return GeoNames place coordinates for the locations shown on the globe."""
    return [
        {"name": "Mumbai", "lat": 19.07283, "lon": 72.88261, "country": "India", "countryISO3": "IND", "type": "City"},
        {"name": "New Delhi", "lat": 28.62137, "lon": 77.21480, "country": "India", "countryISO3": "IND", "type": "Capital"},
        {"name": "Bengaluru", "lat": 12.97194, "lon": 77.59369, "country": "India", "countryISO3": "IND", "type": "City"},
        {"name": "Tokyo", "lat": 35.68950, "lon": 139.69171, "country": "Japan", "countryISO3": "JPN", "type": "Capital"},
        {"name": "London", "lat": 51.50853, "lon": -0.12574, "country": "United Kingdom", "countryISO3": "GBR", "type": "Capital"},
        {"name": "New York", "lat": 40.71427, "lon": -74.00597, "country": "United States", "countryISO3": "USA", "type": "City"},
        {"name": "Sydney", "lat": -33.86785, "lon": 151.20732, "country": "Australia", "countryISO3": "AUS", "type": "City"},
        {"name": "Cape Town", "lat": -33.92584, "lon": 18.42322, "country": "South Africa", "countryISO3": "ZAF", "type": "City"},
        {"name": "Rio de Janeiro", "lat": -22.90642, "lon": -43.18223, "country": "Brazil", "countryISO3": "BRA", "type": "City"},
        {"name": "Dubai", "lat": 25.07725, "lon": 55.30927, "country": "United Arab Emirates", "countryISO3": "ARE", "type": "City"},
        {"name": "Munnar", "lat": 10.08818, "lon": 77.06240, "country": "India", "countryISO3": "IND", "type": "Town"},
        {"name": "Kaza", "lat": 32.22440, "lon": 78.07230, "country": "India", "countryISO3": "IND", "type": "Town"},
        {"name": "Zermatt", "lat": 46.01999, "lon": 7.74863, "country": "Switzerland", "countryISO3": "CHE", "type": "Town"},
    ]


CONTINENTS = [
    {"name": "Africa", "lat": 0, "lon": 20},
    {"name": "Antarctica", "lat": -78, "lon": 0},
    {"name": "Asia", "lat": 38, "lon": 95},
    {"name": "Europe", "lat": 50, "lon": 15},
    {"name": "North America", "lat": 42, "lon": -105},
    {"name": "South America", "lat": -18, "lon": -60},
    {"name": "Oceania", "lat": -25, "lon": 135},
]


def build_admin_index():
    """Build an ADM1/ADM2 name index from GeoNames' official text exports."""
    country_by_code = {}
    with open("countryInfo.txt", encoding="utf-8") as source:
        for line in source:
            if not line.strip() or line.startswith("#"):
                continue
            columns = line.rstrip("\n").split("\t")
            if len(columns) >= 5:
                country_by_code[columns[0]] = {
                    "iso3": columns[1],
                    "name": columns[4],
                }

    admin1_by_code = {}
    regions = [{
        "name": country["name"],
        "ascii": country["name"],
        "country": country["name"],
        "countryISO3": country["iso3"],
        "level": 0,
        "parent": "",
    } for country in country_by_code.values()]
    with open("admin1CodesASCII.txt", encoding="utf-8") as source:
        for line in source:
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 4:
                continue
            full_code, name, ascii_name, geoname_id = columns[:4]
            parts = full_code.split(".", 1)
            if len(parts) != 2 or parts[0] not in country_by_code:
                continue
            country_code, code = parts
            country = country_by_code[country_code]
            admin1_by_code[(country_code, code)] = name
            regions.append({
                "name": name,
                "ascii": ascii_name,
                "country": country["name"],
                "countryISO3": country["iso3"],
                "level": 1,
                "parent": "",
            })

    with open("admin2Codes.txt", encoding="utf-8") as source:
        for line in source:
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 4:
                continue
            full_code, name, ascii_name, geoname_id = columns[:4]
            parts = full_code.split(".")
            if len(parts) < 3 or parts[0] not in country_by_code:
                continue
            country_code, admin1_code, admin2_code = parts[:3]
            country = country_by_code[country_code]
            regions.append({
                "name": name,
                "ascii": ascii_name,
                "country": country["name"],
                "countryISO3": country["iso3"],
                "level": 2,
                "parent": admin1_by_code.get((country_code, admin1_code), ""),
            })

    regions.sort(key=lambda item: (item["name"].casefold(), item["level"], item["country"].casefold()))
    Path("admin-regions.json").write_text(
        json.dumps(regions, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return len(regions)


PAGE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#050a13">
  <title>Earth — Interactive 3D Globe</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: #050a13; }
    body { color: #edf4ff; }
    #globe { position: fixed; inset: 0; width: 100%; height: 100%; display: block; touch-action: none; }
    .panel { position: fixed; z-index: 2; top: max(22px, env(safe-area-inset-top)); left: max(22px, env(safe-area-inset-left)); width: min(410px, calc(100vw - 44px)); max-height: min(82vh, 720px); overflow: auto; padding: 20px; border: 1px solid #ffffff1c; border-radius: 18px; background: #0b1422ed; box-shadow: 0 18px 60px #0008; backdrop-filter: blur(18px); }
    .eyebrow { color: #79c9dc; font-size: 10px; font-weight: 750; letter-spacing: .2em; text-transform: uppercase; }
    h1 { margin: 8px 0 5px; font-size: 23px; letter-spacing: -.04em; }
    .sub { margin: 0 0 17px; color: #9aacc1; font-size: 13px; line-height: 1.5; }
    form { display: flex; gap: 8px; }
    input { min-width: 0; flex: 1; padding: 11px 12px; border: 1px solid #34445a; border-radius: 9px; outline: none; background: #07101c; color: #f4f7fb; font: inherit; font-size: 13px; }
    input:focus { border-color: #6cc9dd; box-shadow: 0 0 0 3px #6cc9dd25; }
    button { padding: 0 15px; border: 0; border-radius: 9px; background: #4aa9b7; color: #041018; font: inherit; font-size: 13px; font-weight: 750; cursor: pointer; }
    button:hover { background: #79d5df; }
    .result { min-height: 38px; margin-top: 12px; color: #b6c5d4; font-size: 12px; line-height: 1.5; }
    .result strong { color: #fff; font-size: 14px; }
    .suggestions { display: grid; gap: 5px; margin-top: 8px; }
    .suggestions:empty { display: none; }
    .suggestion { width: 100%; padding: 9px 10px; border: 1px solid #25374b; border-radius: 8px; background: #101e2e; color: #edf4ff; text-align: left; font-size: 12px; font-weight: 500; }
    .suggestion small { display: block; margin-top: 3px; color: #91a5bb; font-size: 10px; }
    .boundary-status { margin-top: 7px; color: #8095ac; font-size: 10px; line-height: 1.45; }
    .hint { position: fixed; z-index: 1; right: max(22px, env(safe-area-inset-right)); bottom: max(20px, env(safe-area-inset-bottom)); padding: 9px 12px; border: 1px solid #ffffff1a; border-radius: 999px; background: #09111dbb; color: #b2c1d0; font-size: 11px; backdrop-filter: blur(12px); }
    .credit { position: fixed; z-index: 1; left: max(22px, env(safe-area-inset-left)); bottom: max(20px, env(safe-area-inset-bottom)); color: #72849a; font-size: 10px; }
    .credit a { color: inherit; }
    .credit a:hover { color: #d5e7f5; }
    .loading { position: fixed; inset: 0; display: grid; place-items: center; color: #9db3c8; font-size: 13px; pointer-events: none; transition: opacity .5s; }
    .loading.hidden { opacity: 0; }
    @media (max-width: 600px) {
      .panel { top: max(12px, env(safe-area-inset-top)); left: max(12px, env(safe-area-inset-left)); width: min(100% - 24px, 390px); padding: 15px; }
      h1 { font-size: 20px; }
      .sub { margin-bottom: 12px; }
      .credit { bottom: max(54px, calc(env(safe-area-inset-bottom) + 42px)); left: 13px; }
      .hint { right: 12px; bottom: max(12px, env(safe-area-inset-bottom)); font-size: 10px; }
    }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; } }
  </style>
  <script type="importmap">
    {"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}
  </script>
</head>
<body>
  <canvas id="globe" aria-label="Interactive 3D Earth globe"></canvas>
  <section class="panel">
    <div class="eyebrow">Blue Marble · Earth</div>
    <h1>Explore our planet</h1>
  <p class="sub">Search states, provinces, districts, counties, cities, or continents worldwide.</p>
    <form id="search-form">
      <input id="search" type="search" autocomplete="off" placeholder="Try California or Kaza" aria-label="Search countries and regions worldwide">
      <button type="submit">Find</button>
    </form>
    <div class="suggestions" id="suggestions" role="listbox" aria-label="Search results"></div>
    <div class="result" id="result" role="status" aria-live="polite">Drag to rotate · scroll or pinch to zoom</div>
    <div class="boundary-status" id="boundary-status">India state boundaries load on startup; district boundaries appear as you zoom in.</div>
  </section>
  <div class="credit">Names: <a href="https://www.geonames.org/" target="_blank" rel="noreferrer">GeoNames</a> · Boundaries: <a href="https://www.geoboundaries.org/" target="_blank" rel="noreferrer">geoBoundaries</a> · Earth: <a href="https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-topography/" target="_blank" rel="noreferrer">NASA Blue Marble</a></div>
  <div class="hint">Drag to rotate · Scroll to zoom</div>
  <div class="loading" id="loading">Loading Earth texture…</div>
  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

    const locations = @@LOCATIONS@@;
    const continents = @@CONTINENTS@@;
    const canvas = document.querySelector('#globe');
    const result = document.querySelector('#result');
    const loading = document.querySelector('#loading');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#050a13');
    const camera = new THREE.PerspectiveCamera(36, innerWidth / innerHeight, 0.1, 100);
    camera.position.set(0, 0, 4.15);
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(innerWidth, innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.12;

    scene.add(new THREE.AmbientLight(0x9eb9dc, 1.05));
    const sunlight = new THREE.DirectionalLight(0xffffff, 2.7);
    sunlight.position.set(-4, 2, 5);
    scene.add(sunlight);

    const globe = new THREE.Group();
    scene.add(globe);
    const earthGeometry = new THREE.SphereGeometry(1, 128, 96);
    const earthMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.94, metalness: 0.02 });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    globe.add(earth);

    new THREE.TextureLoader().load('./earth-texture.jpg', (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
      earthMaterial.map = texture;
      earthMaterial.needsUpdate = true;
      loading.classList.add('hidden');
    }, undefined, () => {
      loading.textContent = 'Earth texture could not load. Keep earth-texture.jpg beside index.html.';
    });

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(1.025, 96, 72),
      new THREE.ShaderMaterial({
        vertexShader: `varying vec3 vNormal; varying vec3 vView; void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); vNormal=normalize(normalMatrix*normal); vView=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }`,
        fragmentShader: `varying vec3 vNormal; varying vec3 vView; void main(){ float rim=pow(1.0-max(dot(normalize(vNormal),normalize(vView)),0.0),3.1); gl_FragColor=vec4(0.18,0.56,0.92,rim*0.72); }`,
        blending: THREE.AdditiveBlending, side: THREE.BackSide, transparent: true, depthWrite: false
      })
    );
    globe.add(atmosphere);

    function surfacePoint(lat, lon, radius = 1.012) {
      const latitude = THREE.MathUtils.degToRad(lat);
      const longitude = THREE.MathUtils.degToRad(lon);
      return new THREE.Vector3(
        radius * Math.cos(latitude) * Math.sin(longitude),
        radius * Math.sin(latitude),
        -radius * Math.cos(latitude) * Math.cos(longitude)
      );
    }

    function makeLabel(text) {
      const labelCanvas = document.createElement('canvas');
      labelCanvas.width = 640;
      labelCanvas.height = 128;
      const context = labelCanvas.getContext('2d');
      context.font = '700 48px Arial';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.lineJoin = 'round';
      context.strokeStyle = 'rgba(3, 10, 19, 0.88)';
      context.lineWidth = 12;
      context.strokeText(text.toUpperCase(), 320, 65, 610);
      context.fillStyle = '#ffffff';
      context.fillText(text.toUpperCase(), 320, 65, 610);
      const texture = new THREE.CanvasTexture(labelCanvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: true, depthWrite: false, sizeAttenuation: true }));
      const scale = text.length > 11 ? 1.0 : 0.76;
      sprite.scale.set(scale * 1.8, scale * 0.36, 1);
      sprite.renderOrder = 2;
      return sprite;
    }

    continents.forEach((continent) => {
      const label = makeLabel(continent.name);
      label.position.copy(surfacePoint(continent.lat, continent.lon, 1.014));
      globe.add(label);
    });

    const cityMeshes = [];
    const cityGeometry = new THREE.SphereGeometry(0.012, 12, 10);
    const cityMaterial = new THREE.MeshBasicMaterial({ color: 0xffc36b });
    locations.forEach((place) => {
      const marker = new THREE.Mesh(cityGeometry, cityMaterial);
      marker.position.copy(surfacePoint(place.lat, place.lon, 1.012));
      marker.userData.place = place;
      globe.add(marker);
      cityMeshes.push(marker);
    });

    const starPositions = [];
    for (let i = 0; i < 1300; i++) {
      const radius = 18 + Math.random() * 32;
      const theta = Math.random() * Math.PI * 2;
      const z = Math.random() * 2 - 1;
      const ring = Math.sqrt(1 - z * z);
      starPositions.push(radius * ring * Math.cos(theta), radius * z, radius * ring * Math.sin(theta));
    }
    const starGeometry = new THREE.BufferGeometry();
    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starPositions, 3));
    const stars = new THREE.Points(starGeometry, new THREE.PointsMaterial({ color: 0x93a9c8, size: 0.045, transparent: true, opacity: 0.66, sizeAttenuation: true }));
    scene.add(stars);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 1.65;
    controls.maxDistance = 7;
    controls.rotateSpeed = 0.55;
    controls.zoomSpeed = 0.72;
    globe.rotation.y = THREE.MathUtils.degToRad(78 + 180);
    globe.rotation.x = THREE.MathUtils.degToRad(20);

    const allPlaces = [...locations, ...continents.map((place) => ({ ...place, type: 'Continent' }))];
    const suggestions = document.querySelector('#suggestions');
    const input = document.querySelector('#search');
    const boundaryStatus = document.querySelector('#boundary-status');
    const boundaryCache = new Map();
    let regionIndex = [];
    let activeCountryISO3 = 'IND';
    let admin1Lines = null;
    let admin2Lines = null;
    let admin1Labels = null;
    let districtLoadPending = false;

    function normalizeName(value) {
      return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase()
        .replace(/&/g, 'and').replace(/[^a-z0-9]+/g, ' ').trim()
        .replace(/\b(district|county|province|state|region|municipality|prefecture|division|governorate)\b/g, '')
        .replace(/\s+/g, ' ').trim();
    }

    async function getBoundaryLevel(countryISO3, level) {
      const key = `${countryISO3}-ADM${level}`;
      if (boundaryCache.has(key)) return boundaryCache.get(key);
      const request = (async () => {
        const metadataResponse = await fetch(`https://www.geoboundaries.org/api/current/gbOpen/${countryISO3}/ADM${level}/`);
        if (!metadataResponse.ok) return null;
        const metadata = await metadataResponse.json();
        const sourceURL = metadata.simplifiedGeometryGeoJSON || metadata.gjDownloadURL;
        if (!sourceURL) return null;
        const rawURL = sourceURL.replace(/^https:\/\/github\.com\/([^/]+)\/([^/]+)\/raw\//,
          'https://raw.githubusercontent.com/$1/$2/');
        const geometryResponse = await fetch(rawURL);
        if (!geometryResponse.ok) return null;
        const geojson = await geometryResponse.json();
        return { metadata, geojson };
      })().catch(() => null);
      boundaryCache.set(key, request);
      return request;
    }

    function featurePolygons(feature) {
      const geometry = feature && feature.geometry;
      if (!geometry) return [];
      if (geometry.type === 'Polygon') return [geometry.coordinates];
      if (geometry.type === 'MultiPolygon') return geometry.coordinates;
      return [];
    }

    function ringCenter(ring) {
      if (!ring || ring.length < 3) return null;
      const originLon = ring[0][0];
      const points = ring.map(([lon, lat]) => {
        while (lon - originLon > 180) lon -= 360;
        while (lon - originLon < -180) lon += 360;
        return [lon, lat];
      });
      let twiceArea = 0;
      let x = 0;
      let y = 0;
      for (let i = 0; i < points.length - 1; i++) {
        const cross = points[i][0] * points[i + 1][1] - points[i + 1][0] * points[i][1];
        twiceArea += cross;
        x += (points[i][0] + points[i + 1][0]) * cross;
        y += (points[i][1] + points[i + 1][1]) * cross;
      }
      if (Math.abs(twiceArea) < 1e-8) {
        const interior = points.slice(0, -1);
        return [interior.reduce((sum, point) => sum + point[0], 0) / interior.length,
          interior.reduce((sum, point) => sum + point[1], 0) / interior.length];
      }
      return [x / (3 * twiceArea), y / (3 * twiceArea)];
    }

    function featureCenter(feature) {
      let largest = null;
      let largestArea = -1;
      for (const polygon of featurePolygons(feature)) {
        const center = ringCenter(polygon[0]);
        if (!center) continue;
        const ring = polygon[0];
        let area = 0;
        for (let i = 0; i < ring.length - 1; i++) {
          area += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1];
        }
        if (Math.abs(area) > largestArea) {
          largest = center;
          largestArea = Math.abs(area);
        }
      }
      if (!largest) return null;
      return { lon: ((largest[0] + 540) % 360) - 180, lat: largest[1] };
    }

    function makeBoundaryLines(features, color, opacity) {
      const positions = [];
      for (const feature of features || []) {
        for (const polygon of featurePolygons(feature)) {
          for (const ring of polygon) {
            for (let i = 0; i < ring.length - 1; i++) {
              const [lon1, lat1] = ring[i];
              const [lon2, lat2] = ring[i + 1];
              if (Math.abs(lon2 - lon1) > 180) continue;
              const a = surfacePoint(lat1, lon1, 1.007);
              const b = surfacePoint(lat2, lon2, 1.007);
              positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
            }
          }
        }
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      const lines = new THREE.LineSegments(geometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthTest: true }));
      lines.frustumCulled = false;
      return lines;
    }

    function clearBoundaryGroup(group) {
      if (!group) return;
      globe.remove(group);
      group.traverse((object) => {
        object.geometry?.dispose();
        object.material?.map?.dispose();
        object.material?.dispose();
      });
    }

    function replaceBoundaryLayers(states, districts) {
      clearBoundaryGroup(admin1Lines);
      clearBoundaryGroup(admin2Lines);
      clearBoundaryGroup(admin1Labels);
      admin1Lines = states?.features?.length ? makeBoundaryLines(states.features, '#e9f6ff', 0.72) : null;
      admin2Lines = districts?.features?.length ? makeBoundaryLines(districts.features, '#7ed7ec', 0.56) : null;
      admin1Labels = new THREE.Group();
      for (const feature of states?.features || []) {
        const center = featureCenter(feature);
        const name = feature.properties?.shapeName;
        if (!center || !name) continue;
        const label = makeLabel(name);
        label.position.copy(surfacePoint(center.lat, center.lon, 1.012));
        label.scale.multiplyScalar(0.56);
        admin1Labels.add(label);
      }
      if (admin1Lines) globe.add(admin1Lines);
      if (admin2Lines) globe.add(admin2Lines);
      globe.add(admin1Labels);
      updateBoundaryVisibility();
    }

    function updateBoundaryVisibility() {
      const distance = camera.position.length();
      if (admin1Lines) admin1Lines.visible = true;
      if (admin1Labels) admin1Labels.visible = distance < 3.35;
      if (admin2Lines) admin2Lines.visible = distance < 2.7;
      if (distance < 2.7 && activeCountryISO3 && !admin2Lines && !districtLoadPending) {
        districtLoadPending = true;
        loadCountryBoundaries(activeCountryISO3, true).finally(() => { districtLoadPending = false; });
      }
    }

    async function loadCountryBoundaries(countryISO3, includeDistricts = false) {
      if (!countryISO3) return null;
      activeCountryISO3 = countryISO3;
      const [stateData, districtData] = await Promise.all([
        getBoundaryLevel(countryISO3, 1),
        includeDistricts ? getBoundaryLevel(countryISO3, 2) : Promise.resolve(null),
      ]);
      if (countryISO3 !== activeCountryISO3) return null;
      replaceBoundaryLayers(stateData?.geojson, districtData?.geojson);
      const stateCount = stateData?.geojson?.features?.length || 0;
      const districtCount = districtData?.geojson?.features?.length || 0;
      const stateYear = stateData?.metadata?.boundaryYearRepresented || 'year not provided';
      const districtYear = districtData?.metadata?.boundaryYearRepresented || 'not available';
      boundaryStatus.textContent = stateCount
        ? `${stateCount} ADM1 boundaries (${stateYear}); ${districtCount ? `${districtCount} ADM2 boundaries (${districtYear})` : `ADM2 data (${districtYear}) loads on closer zoom`}.`
        : `No ADM1 boundary layer is available for ${countryISO3} in geoBoundaries.`;
      return { stateData, districtData };
    }

    function animateTo(lat, lon, distance = 2.7) {
      const targetX = THREE.MathUtils.degToRad(lat);
      const targetY = THREE.MathUtils.degToRad(lon + 180);
      const startX = globe.rotation.x;
      const startY = globe.rotation.y;
      const startDistance = camera.position.length();
      const deltaY = THREE.MathUtils.euclideanModulo(targetY - startY + Math.PI, Math.PI * 2) - Math.PI;
      const started = performance.now();
      const duration = 950;
      function move(now) {
        const t = Math.min((now - started) / duration, 1);
        const eased = t * t * (3 - 2 * t);
        globe.rotation.x = THREE.MathUtils.lerp(startX, targetX, eased);
        globe.rotation.y = startY + deltaY * eased;
        camera.position.setLength(THREE.MathUtils.lerp(startDistance, distance, eased));
        controls.update();
        if (t < 1) requestAnimationFrame(move);
      }
      requestAnimationFrame(move);
    }

    function showResult(name, detail) {
      result.replaceChildren();
      const heading = document.createElement('strong');
      heading.textContent = name;
      const description = document.createElement('div');
      description.textContent = detail;
      result.append(heading, description);
    }

    async function focusAdminRegion(region) {
      suggestions.replaceChildren();
      result.textContent = `Loading ${region.name} boundary…`;
      boundaryStatus.textContent = `Loading ADM1/ADM2 boundaries for ${region.country}…`;
      const levels = await loadCountryBoundaries(region.countryISO3, region.level !== 0);
      if (!levels) {
        result.textContent = `Boundary data could not be loaded for ${region.country}.`;
        return;
      }
      if (region.level === 0) {
        const stateFeatures = levels.stateData?.geojson?.features || [];
        const centers = stateFeatures.map(featureCenter).filter(Boolean);
        if (centers.length) {
          const center = centers.reduce((sum, point) => ({ lat: sum.lat + point.lat / centers.length, lon: sum.lon + point.lon / centers.length }), { lat: 0, lon: 0 });
          animateTo(center.lat, center.lon, 3.25);
          showResult(region.name, `Country · ${stateFeatures.length} ADM1 regions loaded where available.`);
        } else {
          showResult(region.name, 'Country found. geoBoundaries does not provide an ADM1 layer here, so the country outline cannot be drawn.');
        }
        return;
      }
      const layer = region.level === 1 ? levels.stateData : levels.districtData;
      const features = layer?.geojson?.features || [];
      const targetName = normalizeName(region.name);
      const exactMatches = features.filter((item) => normalizeName(item.properties?.shapeName || '') === targetName);
      const partialMatches = features.filter((item) => {
        const featureName = normalizeName(item.properties?.shapeName || '');
        return targetName.length >= 4 && featureName
          && (featureName.includes(targetName) || targetName.includes(featureName));
      });
      const feature = exactMatches.length === 1 ? exactMatches[0]
        : exactMatches.length === 0 && partialMatches.length === 1 ? partialMatches[0] : null;
      if (exactMatches.length > 1 || (!exactMatches.length && partialMatches.length > 1)) {
        showResult(region.name, `Multiple polygons match in ${region.country}; refine the search with its parent region.`);
        return;
      }
      if (!feature) {
        showResult(region.name, `${region.level === 1 ? 'ADM1' : 'ADM2'} name found in GeoNames, but no matching polygon is present in this country’s geoBoundaries layer.`);
        return;
      }
      const center = featureCenter(feature);
      if (!center) {
        showResult(region.name, 'The boundary source does not provide a usable polygon center.');
        return;
      }
      animateTo(center.lat, center.lon, region.level === 2 ? 2.15 : 2.65);
      const layerYear = layer.metadata.boundaryYearRepresented || 'year not provided';
      const hierarchy = region.level === 2 && region.parent ? `${region.parent}, ` : '';
      showResult(region.name, `${region.level === 1 ? 'ADM1 region' : 'ADM2 region'} · ${hierarchy}${region.country} · boundary vintage ${layerYear}`);
    }

    function focusPlace(place) {
      if (place.countryISO3) loadCountryBoundaries(place.countryISO3, false);
      if (Number.isFinite(place.lat) && Number.isFinite(place.lon)) {
        animateTo(place.lat, place.lon, place.type === 'Continent' ? 3.1 : 2.7);
      }
      showResult(place.name, place.type === 'Continent'
        ? 'Continent · Search a region or rotate the globe to explore.'
        : `${place.type} · ${place.country} · ${place.lat.toFixed(5)}°, ${place.lon.toFixed(5)}°`);
    }

    function renderSuggestions(query) {
      suggestions.replaceChildren();
      if (query.length < 2) return;
      const normalized = normalizeName(query);
      const regionMatches = [];
      for (const region of regionIndex) {
        const name = normalizeName(region.name);
        const ascii = normalizeName(region.ascii || '');
        if (!name.includes(normalized) && !ascii.includes(normalized)) continue;
        regionMatches.push(region);
      }
      regionMatches.sort((a, b) => {
        const aName = normalizeName(a.name);
        const bName = normalizeName(b.name);
        return Number(!aName.startsWith(normalized)) - Number(!bName.startsWith(normalized))
          || a.level - b.level || a.country.localeCompare(b.country);
      });
      const cityMatches = allPlaces.filter((place) => normalizeName(place.name).includes(normalized));
      const matches = [...cityMatches, ...regionMatches].slice(0, 8);
      for (const place of matches) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'suggestion';
        button.setAttribute('role', 'option');
        button.textContent = place.name;
        const scope = document.createElement('small');
        if (place.level) {
        scope.textContent = `${place.level === 0 ? 'Country' : place.level === 1 ? 'ADM1' : 'ADM2'}${place.parent ? ` · ${place.parent}` : ''} · ${place.country}`;
        } else {
          scope.textContent = place.type === 'Continent' ? 'Continent' : `${place.type} · ${place.country}`;
        }
        button.appendChild(scope);
        button.addEventListener('click', () => {
          input.value = place.name;
          if (place.level) focusAdminRegion(place);
          else focusPlace(place);
        });
        suggestions.appendChild(button);
      }
      if (!matches.length) {
        const empty = document.createElement('div');
        empty.className = 'boundary-status';
        empty.textContent = 'No region match found. Try the country name too.';
        suggestions.appendChild(empty);
      }
    }

    fetch('./admin-regions.json').then((response) => {
      if (!response.ok) throw new Error('Region index is unavailable.');
      return response.json();
    }).then((data) => {
      regionIndex = data;
      boundaryStatus.textContent = `Search loaded for ${regionIndex.length.toLocaleString()} ADM1/ADM2 records worldwide. India states appear on zoom; districts load closer in.`;
    }).catch(() => {
      boundaryStatus.textContent = 'The global region search index failed to load.';
    });

    input.addEventListener('input', () => renderSuggestions(normalizeName(input.value)));
    document.querySelector('#search-form').addEventListener('submit', (event) => {
      event.preventDefault();
      const query = input.value.trim();
      const normalized = normalizeName(query);
      const region = regionIndex.find((item) => normalizeName(item.name) === normalized)
        || regionIndex.find((item) => normalizeName(item.ascii || '') === normalized);
      const place = allPlaces.find((item) => normalizeName(item.name) === normalized);
      if (region) focusAdminRegion(region);
      else if (place) focusPlace(place);
      else if (query) renderSuggestions(query);
      else result.textContent = 'Enter a city, state, province, district, county, or continent.';
    });

    controls.addEventListener('change', updateBoundaryVisibility);

    loadCountryBoundaries('IND', false).catch(() => {
      boundaryStatus.textContent = 'India state boundaries are unavailable. Global region search is still available.';
    });

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    renderer.domElement.addEventListener('click', (event) => {
      const bounds = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
      pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const cityHit = raycaster.intersectObjects(cityMeshes)[0];
      const earthHit = raycaster.intersectObject(earth)[0];
      if (cityHit && (!earthHit || cityHit.distance < earthHit.distance)) {
        focusPlace(cityHit.object.userData.place);
      }
    });

    addEventListener('resize', () => {
      camera.aspect = innerWidth / innerHeight;
      camera.updateProjectionMatrix();
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      renderer.setSize(innerWidth, innerHeight);
    });

    renderer.setAnimationLoop(() => {
      controls.update();
      renderer.render(scene, camera);
    });
  </script>
</body>
</html>
'''


def create_interactive_globe():
    region_count = build_admin_index()
    page = PAGE.replace("@@LOCATIONS@@", json.dumps(fetch_city_data(), ensure_ascii=False))
    page = page.replace("@@CONTINENTS@@", json.dumps(CONTINENTS, ensure_ascii=False))
    with open("index.html", "w", encoding="utf-8", newline="\n") as output:
        output.write(page)
    print(f"Generated index.html and admin-regions.json ({region_count:,} GeoNames ADM1/ADM2 records). Keep earth-texture.jpg and the GeoNames source files beside the script.")


if __name__ == "__main__":
    create_interactive_globe()
