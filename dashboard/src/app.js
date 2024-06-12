import {
  WebGLRenderer,
  PerspectiveCamera,
  Scene,
  Mesh,
  PlaneGeometry,
  ShadowMaterial,
  DirectionalLight,
  PCFSoftShadowMap,
  Color,
  AmbientLight,
  Box3,
  LoadingManager,
  MathUtils,
  MeshBasicMaterial,
  MeshPhysicalMaterial,
  MeshPhongMaterial,
  MeshStandardMaterial,
  SphereGeometry,
  AxesHelper,
  Raycaster,
  Vector2,
  Vector3,
  PointLight,
} from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import URDFLoader from "urdf-loader";
import {
  PointerURDFDragControls,
  URDFDragControls,
} from "urdf-loader/src/URDFDragControls";

let scene,
  camera,
  renderer,
  robot,
  controls,
  urdfDragControls,
  bb,
  ground;

init();
render();

function resetQuad() {
  robot.joints['11'].setJointValue(MathUtils.degToRad(90));
  robot.joints['21'].setJointValue(MathUtils.degToRad(-90));
  robot.joints['31'].setJointValue(MathUtils.degToRad(-90));
  robot.joints['41'].setJointValue(MathUtils.degToRad(90));

  robot.joints['12'].setJointValue(MathUtils.degToRad(215));
  robot.joints['22'].setJointValue(MathUtils.degToRad(215));
  robot.joints['32'].setJointValue(MathUtils.degToRad(215));
  robot.joints['42'].setJointValue(MathUtils.degToRad(-215));
}

function init() {
  scene = new Scene();
  scene.background = new Color(0x263238);

  // const axesHelper = new AxesHelper(1);
  // axesHelper.scale.addScalar(100)
  // scene.add(axesHelper);

  slidersDiv = document.getElementById('sliders');

  camera = new PerspectiveCamera();
  camera.position.set(10, 10, 10);
  camera.lookAt(0, 0, 0);

  renderer = new WebGLRenderer({ antialias: true });
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  urdfDragControls = new PointerURDFDragControls(
    scene,
    camera,
    renderer.domElement
  );
  urdfDragControls.enabled = true;

  const pointLight = new PointLight(0xffffff, 500, 0, 1.5);
  pointLight.position.set(-10, 50, 2);
  pointLight.shadow.mapSize.setScalar(4096);
  pointLight.castShadow = true;
  pointLight.shadow.radius = 8;
  scene.add(pointLight);

  // const pointLight2 = new PointLight(0xffffff, 50, 0, 1.5);
  // pointLight2.position.set(10, 30, 15);
  // pointLight2.shadow.mapSize.setScalar(4096);
  // pointLight2.castShadow = true;
  // scene.add(pointLight2);
  // pointLight.shadow.radius = 24;

  // const pointLight3 = new PointLight(0xffffff, 50, 0, 1.5);
  // pointLight3.position.set(-10, 30, -15);
  // pointLight3.shadow.mapSize.setScalar(4096);
  // pointLight3.castShadow = true;
  // pointLight.shadow.radius = 24;
  // scene.add(pointLight3);

  const ambientLight = new AmbientLight(0xffffff, 0.2);
  scene.add(ambientLight);

  ground = new Mesh(
    new PlaneGeometry(3000, 3000),
    new ShadowMaterial({ opacity: 0.25 })
  );
  ground.rotation.x = -Math.PI / 2;
  // ground.position.y = -10;
  ground.scale.setScalar(1);
  ground.receiveShadow = true;
  scene.add(ground);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.minDistance = 4;
  controls.target.y = 1;

  // Load robot
  const manager = new LoadingManager();
  const loader = new URDFLoader(manager);
  loader.packages = (pkg) => {
    return `/assets/QUADurdf/${pkg}`;
  };
  loader.load("/assets/QUADurdf/quadurdf.urdf", (result) => {
    robot = result;
  });

  manager.onLoad = () => {
    robot.scale.setScalar(30);
    robot.rotation.x = -Math.PI / 2;

    robot.traverse(c => {
      c.castShadow = true;
    });

    bb = new Box3();
    bb.setFromObject(robot);
    robot.position.y -= bb.min.y;

    scene.add(robot);

    console.log(Object.keys(robot.joints));

    resetQuad();

  };

  onResize();
  window.addEventListener("resize", onResize);
}

const raycaster = new Raycaster();
const mouse = new Vector2();

// Event listeners for mouse interaction
document.addEventListener("mousedown", onDocumentMouseDown);
document.addEventListener("mouseup", onDocumentMouseUp);

// Mouse down event handler
function onDocumentMouseDown(event) {
  const intersects = getIntersects(event.layerX, event.layerY);
  if (intersects.length > 0) {
    controls.enabled = false;
  } else {
    controls.enabled = true;
  }
}

// Mouse up event handler
function onDocumentMouseUp(event) {
  event.preventDefault();
  selectedObject = null;
  controls.enabled = true;
}

// Function to get intersection point with mouse
function getIntersects(x, y) {
  x = (x / window.innerWidth) * 2 - 1;
  y = -(y / window.innerHeight) * 2 + 1;

  mouse.set(x, y);

  raycaster.setFromCamera(mouse, camera);
  return raycaster.intersectObject(robot);
}

function onResize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

function render() {
  requestAnimationFrame(render);
  renderer.render(scene, camera);
  urdfDragControls.update();

  if (robot && bb) {
    bb.setFromObject(robot);
    ground.position.y = bb.min.y;
  }
}
