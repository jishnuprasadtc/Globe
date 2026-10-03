import json


def fetch_city_data():
    """Return the demo locations shown on the globe."""
    return [
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
        {"name": "Munnar", "lat": 10.0892, "lon": 77.0597, "pop": "32k", "type": "Town"},
        {"name": "Kaza", "lat": 32.2276, "lon": 78.0700, "pop": "3.2k", "type": "Village"},
        {"name": "Zermatt", "lat": 46.0207, "lon": 7.7491, "pop": "5.8k", "type": "Town"},
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
    .panel { position: fixed; z-index: 2; top: max(22px, env(safe-area-inset-top)); left: max(22px, env(safe-area-inset-left)); width: min(370px, calc(100vw - 44px)); padding: 20px; border: 1px solid #ffffff1c; border-radius: 18px; background: #0b1422dc; box-shadow: 0 18px 60px #0008; backdrop-filter: blur(18px); }
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
    <p class="sub">A high resolution satellite globe. Search a place or a continent to fly there.</p>
    <form id="search-form">
      <input id="search" type="search" list="places" placeholder="Try Tokyo or Africa" aria-label="Search cities and continents">
      <datalist id="places"></datalist>
      <button type="submit">Find</button>
    </form>
    <div class="result" id="result" role="status" aria-live="polite">Drag to rotate · scroll or pinch to zoom</div>
  </section>
  <div class="credit">Earth texture: <a href="https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-topography/" target="_blank" rel="noreferrer">NASA Blue Marble Next Generation</a></div>
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
    const datalist = document.querySelector('#places');
    allPlaces.forEach((place) => {
      const option = document.createElement('option');
      option.value = place.name;
      datalist.appendChild(option);
    });

    function focusPlace(place) {
      const targetX = THREE.MathUtils.degToRad(place.lat);
      const targetY = THREE.MathUtils.degToRad(place.lon + 180);
      const startX = globe.rotation.x;
      const startY = globe.rotation.y;
      const deltaY = THREE.MathUtils.euclideanModulo(targetY - startY + Math.PI, Math.PI * 2) - Math.PI;
      const started = performance.now();
      const duration = 950;
      function move(now) {
        const t = Math.min((now - started) / duration, 1);
        const eased = t * t * (3 - 2 * t);
        globe.rotation.x = THREE.MathUtils.lerp(startX, targetX, eased);
        globe.rotation.y = startY + deltaY * eased;
        if (t < 1) requestAnimationFrame(move);
      }
      requestAnimationFrame(move);
      result.replaceChildren();
      const heading = document.createElement('strong');
      heading.textContent = place.name;
      const detail = document.createElement('div');
      detail.textContent = place.type === 'Continent'
        ? 'Continent · Search the map to explore this region.'
        : `${place.type} · Population ${place.pop} · ${place.lat.toFixed(2)}°, ${place.lon.toFixed(2)}°`;
      result.append(heading, detail);
    }

    document.querySelector('#search-form').addEventListener('submit', (event) => {
      event.preventDefault();
      const query = document.querySelector('#search').value.trim().toLocaleLowerCase();
      const match = query && (allPlaces.find((place) => place.name.toLocaleLowerCase() === query)
        || allPlaces.find((place) => place.name.toLocaleLowerCase().includes(query)));
      if (match) focusPlace(match);
      else result.textContent = query ? 'No match found. Try one of the suggested places.' : 'Enter a city or continent to search.';
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
    page = PAGE.replace("@@LOCATIONS@@", json.dumps(fetch_city_data(), ensure_ascii=False))
    page = page.replace("@@CONTINENTS@@", json.dumps(CONTINENTS, ensure_ascii=False))
    with open("index.html", "w", encoding="utf-8", newline="\n") as output:
        output.write(page)
    print("Generated index.html. Keep earth-texture.jpg beside it when publishing.")


if __name__ == "__main__":
    create_interactive_globe()
