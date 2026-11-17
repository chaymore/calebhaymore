// The room: loads the baked scene and lets the visitor turn to each wall and open the objects.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Reflector } from 'three/addons/objects/Reflector.js';

export interface Hotspot {
  group: string;
  label: string;
  /** Where the camera goes when the object is open, in Blender axes (x east, y north, z up). */
  eye: [number, number, number];
  look: [number, number, number];
}

interface Manifest {
  groups: Record<string, { texture: string; size: number }>;
  live: string[];
  model?: string;
  outside?: { texture: string; eye: [number, number, number]; distance: number; width: number; height: number };
}

const WALLS = ['north', 'east', 'south', 'west'] as const;
type Wall = (typeof WALLS)[number];
const DIR: Record<Wall, [number, number]> = { north: [0, 1], east: [1, 0], south: [0, -1], west: [-1, 0] };
const BACK = 0.6;
const EYE = 1.38;

/** Blender (x, y, z-up) to three.js (x, y-up, z). */
const v = (x: number, y: number, z: number) => new THREE.Vector3(x, z, -y);

export function startRoom(root: HTMLElement, base: string, hotspots: Hotspot[]) {
  const canvas = root.querySelector<HTMLCanvasElement>('canvas')!;
  const label = root.querySelector<HTMLElement>('[data-room-label]')!;
  const loading = root.querySelector<HTMLElement>('[data-room-loading]')!;
  const wallButtons = [...root.querySelectorAll<HTMLButtonElement>('[data-wall]')];
  const panels = [...root.querySelectorAll<HTMLElement>('[data-panel]')];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping; // the bake already holds the final colours

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e9b98a');
  const camera = new THREE.PerspectiveCamera(60, 1, 0.05, 400);

  // ---- camera state: where it is and where it looks, eased toward a target
  const pos = new THREE.Vector3(), look = new THREE.Vector3();
  const posT = new THREE.Vector3(), lookT = new THREE.Vector3();
  let wall: Wall = 'north';
  let open: Hotspot | null = null;
  const lean = new THREE.Vector2(), leanT = new THREE.Vector2();
  let shift = 0, shiftT = 0; // pixels the picture moves left to clear the open panel

  function wallPose(w: Wall) {
    const [dx, dy] = DIR[w];
    return { eye: v(-dx * BACK, -dy * BACK, EYE), look: v(dx * 2.0, dy * 2.0, EYE - 0.08) };
  }

  function aim(snap = false) {
    const p = open ? { eye: v(...open.eye), look: v(...open.look) } : wallPose(wall);
    posT.copy(p.eye);
    lookT.copy(p.look);
    if (snap || reduceMotion) { pos.copy(posT); look.copy(lookT); }
    wallButtons.forEach((b) => b.setAttribute('aria-pressed', String(!open && b.dataset.wall === wall)));
    panels.forEach((el) => { el.hidden = !open || el.dataset.panel !== open.group; });
    root.dataset.open = open ? open.group : '';
    shiftT = open && root.clientWidth > 767 ? Math.min(420, root.clientWidth) / 2 : 0;
    if (snap || reduceMotion) shift = shiftT;
    needsFrame = true;
  }

  function turn(step: number) {
    open = null;
    wall = WALLS[(WALLS.indexOf(wall) + step + 4) % 4];
    aim();
  }

  function face(w: Wall) { open = null; wall = w; aim(); }

  function openGroup(group: string) {
    const h = hotspots.find((x) => x.group === group);
    if (!h) return;
    open = h;
    aim();
    const panel = panels.find((el) => el.dataset.panel === group);
    panel?.querySelector<HTMLElement>('[data-close]')?.focus({ preventScroll: true });
  }

  function close() { if (open) { open = null; aim(); } }

  // ---- size
  function resize() {
    const w = root.clientWidth, h = root.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // Hold a horizontal view of about 79 degrees on wide screens; on tall screens keep the vertical view sane.
    const hfov = THREE.MathUtils.degToRad(78.6);
    const vfov = 2 * Math.atan(Math.tan(hfov / 2) / camera.aspect);
    camera.fov = THREE.MathUtils.clamp(THREE.MathUtils.radToDeg(vfov), 30, 68);
    camera.updateProjectionMatrix();
    needsFrame = true;
  }

  // ---- scene
  const meshes: THREE.Mesh[] = [];
  const materials = new Map<string, THREE.MeshBasicMaterial[]>(); // by object group
  let hovered = '';

  async function load() {
    const manifest: Manifest = await (await fetch(`${base}manifest.json`)).json();
    const texLoader = new THREE.TextureLoader();
    // Some hosts cannot serve .glb files. There the model ships as base64 inside a JSON file.
    const model = manifest.model ?? 'room.glb';
    const loader = new GLTFLoader();
    const gltf = model.endsWith('.json')
      ? await loader.parseAsync(Uint8Array.from(atob((await (await fetch(base + model)).json()).glb), (c) => c.charCodeAt(0)).buffer, base)
      : await loader.loadAsync(base + model);
    const jobs: Promise<unknown>[] = [];
    gltf.scene.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh) return;
      const info = manifest.groups[m.name];
      if (info) {
        const mat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        jobs.push(texLoader.loadAsync(base + info.texture).then((t) => {
          t.flipY = false;
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = renderer.capabilities.getMaxAnisotropy();
          mat.map = t;
          mat.needsUpdate = true;
        }));
        // "bookshelf__detail" holds the sharp pictures (spines, posters) that belong to "bookshelf"
        const group = m.name.split('__')[0];
        if (m.name.includes('__detail')) { mat.polygonOffset = true; mat.polygonOffsetFactor = -2; mat.polygonOffsetUnits = -2; }
        m.material = mat;
        materials.set(group, [...(materials.get(group) ?? []), mat]);
        m.userData.group = group;
        meshes.push(m);
      } else if (m.name.startsWith('live_mirror')) {
        // a real planar reflection, laid just in front of the glass
        m.geometry.computeBoundingBox();
        const size = m.geometry.boundingBox!.getSize(new THREE.Vector3());
        const glass = new Reflector(new THREE.PlaneGeometry(size.z, size.y), {
          textureWidth: 512, textureHeight: 1024, color: 0xd8d2c4, clipBias: 0.003,
        });
        glass.rotation.y = Math.PI / 2;
        glass.position.x = size.x / 2 + 0.002;
        m.add(glass);
        m.material = new THREE.MeshBasicMaterial({ color: 0x15120e });
        m.userData.group = 'mirror';
        meshes.push(m);
      } else if (m.name.startsWith('live_screen')) {
        m.geometry.computeBoundingBox();
        const size = m.geometry.boundingBox!.getSize(new THREE.Vector3());
        const face = new THREE.Mesh(new THREE.PlaneGeometry(size.x, size.y), new THREE.MeshBasicMaterial({ map: screenTexture() }));
        face.rotation.y = Math.PI;
        face.position.z = -size.z / 2 - 0.0008;
        m.add(face);
        m.material = new THREE.MeshBasicMaterial({ color: 0x0a0a0a });
        m.userData.group = 'desk';
        meshes.push(m);
      } else if (m.name.startsWith('live_strings')) {
        m.material = new THREE.MeshBasicMaterial({ color: 0xe8e2d0, transparent: true, opacity: 0.35 });
      }
    });
    if (manifest.outside) {
      const o = manifest.outside;
      const plate = new THREE.Mesh(new THREE.PlaneGeometry(o.width, o.height), new THREE.MeshBasicMaterial());
      plate.position.copy(v(o.eye[0] + o.distance, o.eye[1], o.eye[2]));
      plate.rotation.y = -Math.PI / 2;
      jobs.push(texLoader.loadAsync(base + o.texture).then((t) => {
        t.colorSpace = THREE.SRGBColorSpace;
        (plate.material as THREE.MeshBasicMaterial).map = t;
        (plate.material as THREE.MeshBasicMaterial).needsUpdate = true;
      }));
      scene.add(plate);
    }
    await Promise.all(jobs);
    scene.add(gltf.scene);
    loading.hidden = true;
    root.dataset.ready = 'true';
    needsFrame = true;
  }

  /** What the laptop shows: a plain page in the site's own type. */
  function screenTexture() {
    const c = document.createElement('canvas');
    c.width = 1024; c.height = 660;
    const g = c.getContext('2d')!;
    g.fillStyle = '#F6F5EF'; g.fillRect(0, 0, c.width, c.height);
    g.fillStyle = '#000';
    g.font = '300 26px ui-monospace, monospace';
    g.fillText('PROJECTS:', 64, 96);
    g.fillRect(64, 122, c.width - 128, 2);
    g.font = '400 84px Helvetica, Arial, sans-serif';
    g.fillText('Things I have built', 60, 236);
    g.font = '400 30px ui-monospace, monospace';
    ['01  THIS ROOM', '02  NIGHTLOCK', '03  MILO', '04  SCRIPTURE HIGHLIGHTER'].forEach((t, i) => {
      g.fillRect(64, 300 + i * 74, c.width - 128, 1);
      g.fillText(t, 64, 350 + i * 74);
      g.fillText('\u2197', c.width - 100, 350 + i * 74);
    });
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return t;
  }

  // ---- pointer: hover labels, click to open, drag or swipe to turn
  const ray = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  let down: { x: number; y: number; t: number } | null = null;

  function pick(e: PointerEvent): string {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hit = ray.intersectObjects(meshes, false)[0];
    const g = hit ? (hit.object.userData.group as string) : '';
    return hotspots.some((h) => h.group === g) ? g : '';
  }

  function setHover(g: string, e?: PointerEvent) {
    if (g !== hovered) {
      if (hovered) materials.get(hovered)?.forEach((x) => x.color.setScalar(1));
      hovered = g;
      if (g) materials.get(g)?.forEach((x) => x.color.setScalar(1.12));
      canvas.style.cursor = g ? 'pointer' : 'grab';
      label.textContent = g ? hotspots.find((h) => h.group === g)!.label : '';
      label.hidden = !g;
      needsFrame = true;
    }
    if (g && e) {
      const r = root.getBoundingClientRect();
      label.style.transform = `translate(${e.clientX - r.left + 14}px, ${e.clientY - r.top + 14}px)`;
    }
  }

  canvas.addEventListener('pointermove', (e) => {
    const r = canvas.getBoundingClientRect();
    leanT.set(((e.clientX - r.left) / r.width) * 2 - 1, ((e.clientY - r.top) / r.height) * 2 - 1);
    needsFrame = true;
    if (!down && e.pointerType !== 'touch') setHover(open ? '' : pick(e), e);
  });
  canvas.addEventListener('pointerleave', () => { leanT.set(0, 0); setHover(''); });
  canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
  canvas.addEventListener('pointerup', (e) => {
    if (!down) return;
    const dx = e.clientX - down.x, dy = e.clientY - down.y;
    down = null;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.5) { turn(dx < 0 ? 1 : -1); return; }
    if (Math.hypot(dx, dy) > 8) return;
    if (open) { close(); return; }
    const g = pick(e);
    if (g) { setHover(''); openGroup(g); }
  });
  canvas.addEventListener('pointercancel', () => { down = null; });

  addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowRight') turn(1);
    else if (e.key === 'ArrowLeft') turn(-1);
  });
  wallButtons.forEach((b) => b.addEventListener('click', () => face(b.dataset.wall as Wall)));
  root.querySelectorAll<HTMLElement>('[data-turn]').forEach((b) => b.addEventListener('click', () => turn(Number(b.dataset.turn))));
  root.querySelectorAll<HTMLElement>('[data-close]').forEach((b) => b.addEventListener('click', close));
  root.querySelectorAll<HTMLElement>('[data-open]').forEach((b) => b.addEventListener('click', () => {
    const h = hotspots.find((x) => x.group === b.dataset.open);
    if (h) { open = null; openGroup(h.group); }
  }));

  // ---- frame loop: only draws while something moves
  let needsFrame = true;
  let last = performance.now();
  const tmp = new THREE.Vector3(), right = new THREE.Vector3();
  function frame(now: number) {
    requestAnimationFrame(frame);
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    const k = 1 - Math.exp(-dt * 4.2);
    const moving = pos.distanceToSquared(posT) > 1e-7 || look.distanceToSquared(lookT) > 1e-7 || lean.distanceToSquared(leanT) > 1e-6 || Math.abs(shift - shiftT) > 0.3;
    if (!moving && !needsFrame) return;
    needsFrame = false;
    pos.lerp(posT, k);
    look.lerp(lookT, k);
    shift += (shiftT - shift) * k;
    if (Math.abs(shift) > 0.3) camera.setViewOffset(root.clientWidth, root.clientHeight, shift, 0, root.clientWidth, root.clientHeight);
    else camera.clearViewOffset();
    lean.lerp(leanT, reduceMotion ? 1 : 1 - Math.exp(-dt * 6));
    // the head leans a little with the pointer, which gives the room depth
    tmp.subVectors(look, pos).normalize();
    right.crossVectors(tmp, camera.up).normalize();
    const amount = open ? 0.03 : 0.1;
    camera.position.copy(pos).addScaledVector(right, lean.x * amount).addScaledVector(camera.up, -lean.y * amount * 0.5);
    camera.lookAt(tmp.copy(look).addScaledVector(right, lean.x * amount * 2.2).addScaledVector(camera.up, -lean.y * amount * 1.1));
    renderer.render(scene, camera);
  }

  new ResizeObserver(resize).observe(root);
  resize();
  aim(true);
  requestAnimationFrame(frame);
  load().catch((err) => {
    console.error(err);
    loading.textContent = 'The room did not load. Use the links below.';
    root.dataset.failed = 'true';
  });
}
