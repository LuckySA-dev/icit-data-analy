import React, { useRef, useMemo, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html, Sky } from '@react-three/drei'
import * as THREE from 'three'
import { WIFI_BUILDINGS, OTHER_BUILDINGS, qualityColor, classifyRSSI } from '../data/campusData'

// Color = "impact on users" = density × signal quality badness
// No users → neutral gray (nobody affected, regardless of signal)
// Many users + bad signal → RED (many people suffering)
// Many users + good signal → GREEN (working well)
function floorColorHex(weakPct, densityRatio) {
  // Idle: almost nobody using → neutral blue-gray
  if (densityRatio <= 0.02) return '#b0bec5'

  // "Impact" = how bad the situation is for actual users
  // density high + signal bad = high impact (red)
  // density high + signal good = low impact (green)
  // density low = calm regardless
  const qBad = weakPct / 100 // 0 = perfect signal, 1 = terrible
  const impact = Math.min(densityRatio * (0.3 + 0.7 * qBad), 1)

  // Continuous gradient: green → yellow → orange → red
  const active = new THREE.Color()
  if (impact < 0.33) {
    active.setStyle('#4ade80').lerp(new THREE.Color('#facc15'), impact / 0.33)
  } else if (impact < 0.66) {
    active.setStyle('#facc15').lerp(new THREE.Color('#f97316'), (impact - 0.33) / 0.33)
  } else {
    active.setStyle('#f97316').lerp(new THREE.Color('#ef4444'), Math.min((impact - 0.66) / 0.34, 1))
  }

  // Smooth fade from idle gray → active color as density ramps up (0 → 0.15)
  const fadeIn = Math.min(densityRatio / 0.15, 1)
  const result = new THREE.Color('#b0bec5').lerp(active, fadeIn)
  return '#' + result.getHexString()
}

// ============ ANIMATED FLOOR — smooth color lerp ============
function AnimatedFloor({ y, w, floorH, d, targetColor, opacity }) {
  const matRef = useRef()
  const colorObj = useRef(new THREE.Color(targetColor))

  useFrame(() => {
    if (!matRef.current) return
    colorObj.current.lerp(new THREE.Color(targetColor), 0.045)
    matRef.current.color.copy(colorObj.current)
  })

  return (
    <mesh position={[0, y + floorH / 2, 0]} castShadow receiveShadow>
      <boxGeometry args={[w, floorH, d]} />
      <meshStandardMaterial
        ref={matRef}
        color={targetColor}
        transparent
        opacity={opacity}
        roughness={0.35}
        metalness={0.02}
      />
    </mesh>
  )
}

// ============ WIFI BUILDING COMPONENT ============
function WifiBuilding({ buildingData, isSelected, isHovered, onClick, onHover, currentHour, currentDay, dailyHourlyData, peakUsersMap }) {
  const meshRef = useRef()
  const config = WIFI_BUILDINGS[buildingData.code]
  if (!config) return null

  const [px, , pz] = config.position
  const [w, maxH, d] = config.size
  const floors = buildingData.floors || []

  // Sort floors by floor_num to ensure correct order
  const sortedFloors = useMemo(() =>
    [...floors].sort((a, b) => a.floor_num - b.floor_num),
    [floors]
  )

  // Use number of actual floors for height calculation (not max_floor — avoids gaps & B79 div-by-zero)
  const numFloors = Math.max(sortedFloors.length, 1)
  const floorH = maxH / numFloors

  // Building-level density for this day+hour (NO fallback to monthly aggregate — missing = 0 users)
  const dhKey = `${currentDay}_${currentHour}`
  const dhBuilding = dailyHourlyData?.[buildingData.code] || {}
  const hourData = dhBuilding[dhKey] || null

  // Use actual per-building peak from data for normalization (not hardcoded)
  const maxUsersBuilding = Math.max(peakUsersMap?.[buildingData.code] || 100, 1)
  const densityRatio = hourData ? Math.min(hourData.users / maxUsersBuilding, 1) : 0

  useFrame(() => {
    if (!meshRef.current) return
    const target = isHovered || isSelected ? 1.02 : 1.0
    meshRef.current.scale.x = THREE.MathUtils.lerp(meshRef.current.scale.x, target, 0.08)
    meshRef.current.scale.z = THREE.MathUtils.lerp(meshRef.current.scale.z, target, 0.08)
  })

  const baseY = 0.08

  // Compute per-floor density (distribute building density with weight by floor user ratio)
  const totalFloorSessions = sortedFloors.reduce((s, f) => s + (f.sessions || 1), 0)

  return (
    <group position={[px, 0, pz]}>
      {/* Foundation pad */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, 0]}>
        <planeGeometry args={[w + 1.4, d + 1.4]} />
        <meshStandardMaterial color="#c8cdd4" roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.04, 0]} receiveShadow>
        <boxGeometry args={[w + 0.5, 0.08, d + 0.5]} />
        <meshStandardMaterial color="#b0b8c4" roughness={0.8} />
      </mesh>

      {/* Building body */}
      <group
        ref={meshRef}
        onClick={(e) => { e.stopPropagation(); onClick(buildingData.code) }}
        onPointerEnter={(e) => { e.stopPropagation(); onHover(buildingData.code) }}
        onPointerLeave={(e) => { e.stopPropagation(); onHover(null) }}
      >
        {/* Solid floor blocks — positioned by sequential INDEX (no gaps!) */}
        {sortedFloors.map((floor, index) => {
          const y = baseY + index * floorH
          // Per-floor density: base = building density, modulated by floor's session share
          // A proportional floor (1/N) gets exactly densityRatio; dominant floors get up to 1.4x
          const floorWeight = totalFloorSessions > 0 ? (floor.sessions || 1) / totalFloorSessions : 1 / numFloors
          const floorDensity = densityRatio * (0.6 + 0.4 * floorWeight * numFloors)
          const color = floorColorHex(floor.weak_pct, Math.min(floorDensity, 1))
          const opacity = isSelected ? 0.95 : isHovered ? 0.9 : 0.85

          return (
            <group key={floor.floor}>
              {/* Animated solid floor block with smooth color transition */}
              <AnimatedFloor y={y} w={w} floorH={floorH} d={d} targetColor={color} opacity={opacity} />
              {/* Thin floor divider line (except ground floor) */}
              {index > 0 && (
                <mesh position={[0, y + 0.01, 0]}>
                  <boxGeometry args={[w + 0.02, 0.02, d + 0.02]} />
                  <meshStandardMaterial color="#ffffff" transparent opacity={0.4} />
                </mesh>
              )}
            </group>
          )
        })}

        {/* Roof cap */}
        <mesh position={[0, baseY + maxH + 0.04, 0]} castShadow>
          <boxGeometry args={[w + 0.08, 0.08, d + 0.08]} />
          <meshStandardMaterial color="#64748b" roughness={0.5} />
        </mesh>

        {/* Subtle edge outline */}
        {isSelected && (
          <>
            <mesh position={[0, baseY + maxH / 2, 0]}>
              <boxGeometry args={[w + 0.04, maxH + 0.04, d + 0.04]} />
              <meshBasicMaterial color="#3182ce" wireframe transparent opacity={0.2} />
            </mesh>
            <mesh position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <ringGeometry args={[Math.max(w, d) * 0.7, Math.max(w, d) * 0.85, 32]} />
              <meshBasicMaterial color="#3182ce" transparent opacity={0.3} />
            </mesh>
          </>
        )}
      </group>

      {/* ===== LABEL — bigger, clearer, with background ===== */}
      <Html
        position={[0, baseY + maxH + 1.5, 0]}
        center
        distanceFactor={18}
        style={{ pointerEvents: 'none', userSelect: 'none' }}
      >
        <div style={{
          textAlign: 'center',
          whiteSpace: 'nowrap',
          fontFamily: "'IBM Plex Sans Thai', 'Sarabun', sans-serif",
          background: 'rgba(255,255,255,0.92)',
          borderRadius: 10,
          padding: '6px 14px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.15)',
          border: isSelected ? '2px solid #3182ce' : '1px solid rgba(0,0,0,0.1)',
        }}>
          <div style={{
            fontSize: 28,
            fontWeight: 800,
            color: isSelected ? '#2b6cb0' : '#1e293b',
            lineHeight: 1.2,
            letterSpacing: '-0.5px',
          }}>
            {buildingData.code}
          </div>
          <div style={{
            fontSize: 15,
            color: '#475569',
            fontWeight: 500,
            maxWidth: 200,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {config.name}
          </div>
          <div style={{
            fontSize: 18,
            fontWeight: 700,
            marginTop: 3,
            color: densityRatio > 0.6 ? '#dc2626' : densityRatio > 0.35 ? '#d97706' : densityRatio > 0.1 ? '#16a34a' : '#9ca3af',
          }}>
            👤 {hourData ? hourData.users.toLocaleString() : '—'} คน
          </div>
        </div>
      </Html>
    </group>
  )
}

// ============ CONTEXT BUILDING (no WiFi data) ============
function ContextBuilding({ building }) {
  const [w, h, d] = building.size
  const [px, , pz] = building.position
  const actualH = Math.max(h, 0.3)

  return (
    <group position={[px, 0, pz]}>
      {/* Small foundation */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <planeGeometry args={[w + 0.4, d + 0.4]} />
        <meshStandardMaterial color="#d4d8de" roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.03, 0]} receiveShadow>
        <boxGeometry args={[w + 0.2, 0.06, d + 0.2]} />
        <meshStandardMaterial color="#b8bfc8" roughness={0.8} />
      </mesh>

      {/* Building body */}
      <mesh position={[0, 0.06 + actualH / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[w, actualH, d]} />
        <meshStandardMaterial color="#cbd5e1" transparent opacity={0.5} roughness={0.7} />
      </mesh>

      {/* Roof */}
      {actualH > 0.5 && (
        <mesh position={[0, 0.06 + actualH + 0.04, 0]}>
          <boxGeometry args={[w + 0.06, 0.08, d + 0.06]} />
          <meshStandardMaterial color="#94a3b8" roughness={0.7} />
        </mesh>
      )}

      <Html
        position={[0, 0.06 + actualH + 0.4, 0]}
        center
        distanceFactor={30}
        style={{ pointerEvents: 'none', userSelect: 'none' }}
      >
        <div style={{
          fontSize: 9,
          color: '#94a3b8',
          textShadow: '0 0 3px #fff, 0 0 6px #fff',
          whiteSpace: 'nowrap',
          fontFamily: "'IBM Plex Sans Thai', sans-serif",
        }}>
          {building.code}
        </div>
      </Html>
    </group>
  )
}

// ============ GROUND & ENVIRONMENT ============
function Ground() {
  return (
    <>
      {/* Main ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]} receiveShadow>
        <planeGeometry args={[140, 140]} />
        <meshStandardMaterial color="#c5d4b8" roughness={0.95} />
      </mesh>

      {/* Inner campus lawn */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, -5]} receiveShadow>
        <planeGeometry args={[90, 80]} />
        <meshStandardMaterial color="#b8d0a8" roughness={0.9} />
      </mesh>

      {/* Roads - scaled for larger campus */}
      {[
        { pos: [0, 0.005, 28], size: [100, 3.5] },      // ถนนประชาราษฎร์ 1 (north)
        { pos: [0, 0.005, -42], size: [100, 3] },         // south road
        { pos: [-38, 0.005, -5], size: [3, 75] },         // west perimeter
        { pos: [40, 0.005, -5], size: [3, 75] },          // east perimeter
        { pos: [0, 0.005, -2], size: [70, 2] },           // central horizontal
        { pos: [0, 0.005, 14], size: [60, 1.5] },         // upper horizontal
        { pos: [10, 0.005, -18], size: [1.8, 30] },       // central vertical
        { pos: [-10, 0.005, -10], size: [1.5, 25] },      // west vertical
        { pos: [28, 0.005, -10], size: [1.5, 30] },       // east vertical
      ].map((road, i) => (
        <mesh key={`road-${i}`} rotation={[-Math.PI / 2, 0, 0]} position={road.pos}>
          <planeGeometry args={road.size} />
          <meshStandardMaterial color="#ddd8ce" roughness={0.85} />
        </mesh>
      ))}

      {/* Walkways */}
      {[
        { pos: [-4, 0.006, 8], size: [12, 0.8] },
        { pos: [14, 0.006, -5], size: [0.8, 10] },
        { pos: [-18, 0.006, -10], size: [0.8, 14] },
        { pos: [6, 0.006, -14], size: [8, 0.6] },
      ].map((path, i) => (
        <mesh key={`path-${i}`} rotation={[-Math.PI / 2, 0, 0]} position={path.pos}>
          <planeGeometry args={path.size} />
          <meshStandardMaterial color="#e8e2d8" roughness={0.85} />
        </mesh>
      ))}

      {/* Trees - spread across larger campus */}
      {[
        [-15, -30], [20, -38], [-30, 5], [30, 14],
        [-6, 18], [16, 10], [-28, -20], [0, -35],
        [-20, 16], [24, -16], [6, 22], [-24, -8],
        [34, -6], [-36, -14], [14, 22], [-12, 10],
        [20, 0], [-26, 14], [30, -30], [-6, -24],
        [36, 8], [-34, 0], [8, -28], [-16, -38],
        [26, 20], [-8, -14], [38, -20], [-22, 22],
      ].map(([x, z], i) => (
        <group key={`tree-${i}`} position={[x, 0, z]}>
          <mesh position={[0, 0.8, 0]}>
            <sphereGeometry args={[0.6 + (i % 4) * 0.15, 8, 6]} />
            <meshStandardMaterial color={i % 3 === 0 ? '#4ade80' : i % 3 === 1 ? '#6ee7a0' : '#86efac'} transparent opacity={0.55} />
          </mesh>
          <mesh position={[0, 0.25, 0]}>
            <cylinderGeometry args={[0.06, 0.09, 0.5]} />
            <meshStandardMaterial color="#a07850" />
          </mesh>
        </group>
      ))}
    </>
  )
}

// ============ SCENE ============
function Scene({ vizData, selectedBuilding, onBuildingClick, currentHour, currentDay, hoveredBuilding, setHoveredBuilding }) {
  const buildings = vizData?.buildings || []
  const dailyHourlyData = vizData?.daily_hourly_by_building || {}

  // Compute actual peak daily-hourly users per building (for correct normalization)
  const peakUsersMap = useMemo(() => {
    const peaks = {}
    for (const [code, entries] of Object.entries(dailyHourlyData)) {
      let max = 0
      for (const v of Object.values(entries)) {
        if (v.users > max) max = v.users
      }
      peaks[code] = max
    }
    return peaks
  }, [dailyHourlyData])

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[30, 40, 25]}
        intensity={1.2}
        castShadow
        color="#fff8e7"
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={150}
        shadow-camera-left={-60}
        shadow-camera-right={60}
        shadow-camera-top={60}
        shadow-camera-bottom={-60}
      />
      <directionalLight position={[-10, 15, -10]} intensity={0.2} color="#d0e8ff" />
      <hemisphereLight args={['#87ceeb', '#567d46', 0.3]} />

      <Sky distance={450000} sunPosition={[50, 40, -20]} rayleigh={0.5} turbidity={6} />

      <Ground />

      {/* Road labels */}
      <Html position={[0, 0.15, 30]} center distanceFactor={30} style={{ pointerEvents: 'none' }}>
        <div style={{
          fontSize: 12, color: '#78716c', fontWeight: 500,
          textShadow: '0 0 4px #fff, 0 0 8px #fff',
          fontFamily: "'IBM Plex Sans Thai', sans-serif",
          whiteSpace: 'nowrap',
        }}>
          ถนนประชาราษฎร์ 1
        </div>
      </Html>

      {/* Compass */}
      <Html position={[-42, 0.15, 26]} center distanceFactor={22} style={{ pointerEvents: 'none' }}>
        <div style={{ textAlign: 'center', fontWeight: 700, lineHeight: 1.2 }}>
          <div style={{ color: '#c53030', fontSize: 16 }}>N</div>
          <div style={{ color: '#a0aec0', fontSize: 12 }}>▲</div>
        </div>
      </Html>

      {/* WiFi buildings */}
      {buildings.map(bldg => (
        <WifiBuilding
          key={bldg.code}
          buildingData={bldg}
          isSelected={selectedBuilding === bldg.code}
          isHovered={hoveredBuilding === bldg.code}
          onClick={onBuildingClick}
          onHover={setHoveredBuilding}
          currentHour={currentHour}
          currentDay={currentDay}
          dailyHourlyData={dailyHourlyData}
          peakUsersMap={peakUsersMap}
        />
      ))}

      {/* Context buildings */}
      {OTHER_BUILDINGS.map(bldg => (
        <ContextBuilding key={bldg.code} building={bldg} />
      ))}

      <OrbitControls
        makeDefault
        maxPolarAngle={Math.PI / 2.15}
        minDistance={10}
        maxDistance={120}
        target={[0, 2, -5]}
        enableDamping
        dampingFactor={0.05}
      />
    </>
  )
}

// ============ TOOLTIP ============
function Tooltip({ vizData, hoveredBuilding }) {
  if (!hoveredBuilding || !vizData) return null
  const bldg = vizData.buildings.find(b => b.code === hoveredBuilding)
  if (!bldg) return null
  const quality = classifyRSSI(bldg.avg_rssi)

  return (
    <div className="tooltip-3d" style={{ top: 12, right: 12 }}>
      <div className="tooltip-3d-title">{bldg.code}</div>
      <div className="tooltip-3d-name">{bldg.name}</div>
      <div className="tooltip-3d-row"><span>ผู้ใช้</span><span>{bldg.total_users.toLocaleString()} คน</span></div>
      <div className="tooltip-3d-row"><span>Sessions</span><span>{bldg.total_sessions.toLocaleString()}</span></div>
      <div className="tooltip-3d-row"><span>RSSI เฉลี่ย</span><span style={{ color: quality.color }}>{bldg.avg_rssi} dBm</span></div>
      <div className="tooltip-3d-row"><span>คุณภาพ</span><span style={{ color: quality.color }}>{quality.label}</span></div>
      <div className="tooltip-3d-row"><span>สัญญาณอ่อน</span><span style={{ color: bldg.overall_weak_pct > 70 ? '#e53e3e' : '#d69e2e' }}>{bldg.overall_weak_pct}%</span></div>
    </div>
  )
}

// ============ ERROR BOUNDARY ============
class CanvasErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(error) { return { error } }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, textAlign: 'center', color: '#e53e3e', fontFamily: "'IBM Plex Sans Thai', sans-serif" }}>
          <h3>เกิดข้อผิดพลาดในการแสดงผล 3D</h3>
          <p style={{ fontSize: 13, color: '#718096', marginTop: 8 }}>{this.state.error.message}</p>
          <button onClick={() => this.setState({ error: null })} style={{
            marginTop: 16, padding: '8px 20px', borderRadius: 8, border: '1px solid #e2e8f0',
            cursor: 'pointer', background: '#ebf4ff', color: '#2b6cb0', fontFamily: 'inherit',
          }}>ลองใหม่</button>
        </div>
      )
    }
    return this.props.children
  }
}

// ============ EXPORT ============
export default function CampusScene({ vizData, selectedBuilding, onBuildingClick, currentHour, currentDay, hoveredBuilding, setHoveredBuilding }) {
  return (
    <CanvasErrorBoundary>
      <Canvas
        camera={{ position: [45, 35, 50], fov: 45 }}
        shadows
        style={{ width: '100%', height: '100%' }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.1 }}
        onCreated={({ gl }) => { gl.setClearColor('#e8f4fd') }}
      >
        <Suspense fallback={null}>
          <Scene
            vizData={vizData}
            selectedBuilding={selectedBuilding}
            onBuildingClick={onBuildingClick}
            currentHour={currentHour}
            currentDay={currentDay}
            hoveredBuilding={hoveredBuilding}
            setHoveredBuilding={setHoveredBuilding}
          />
        </Suspense>
      </Canvas>
      <Tooltip vizData={vizData} hoveredBuilding={hoveredBuilding} />
    </CanvasErrorBoundary>
  )
}
