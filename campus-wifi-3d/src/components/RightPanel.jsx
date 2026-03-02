import React, { useState } from 'react'
import { INSIGHTS, PAIN_POINTS, CATEGORIES, classifyRSSI, qualityColor, WIFI_BUILDINGS } from '../data/campusData'

// ============ INSIGHTS PANEL ============
function InsightsPanel({ filterCategory, setFilterCategory }) {
  const [expandedId, setExpandedId] = useState(null)

  const filtered = filterCategory === 'all'
    ? INSIGHTS
    : INSIGHTS.filter(i => i.category === filterCategory)

  return (
    <div className="fade-in">
      <div className="filter-row">
        {CATEGORIES.map(cat => (
          <button
            key={cat.key}
            className={`filter-btn ${filterCategory === cat.key ? 'active' : ''}`}
            onClick={() => setFilterCategory(cat.key)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {filtered.map(insight => (
        <div
          key={insight.id}
          className={`insight-card ${expandedId === insight.id ? 'expanded' : ''}`}
          onClick={() => setExpandedId(expandedId === insight.id ? null : insight.id)}
        >
          <div className="insight-card-header">
            <div
              className="insight-icon"
              style={{ background: insight.iconBg }}
            >
              {insight.icon}
            </div>
            <div style={{ flex: 1 }}>
              <div className="insight-card-title">{insight.title}</div>
              <div className="insight-card-subtitle">
                <span className="insight-category-badge" style={{
                  background: insight.severity === 'critical' ? '#FED7D7' :
                             insight.severity === 'warning' ? '#FEFCBF' : '#BEE3F8',
                  color: insight.severity === 'critical' ? '#742a2a' :
                        insight.severity === 'warning' ? '#744210' : '#2a4365',
                }}>
                  {insight.category}
                </span>
                {' '}{insight.subtitle}
              </div>
            </div>
          </div>

          {expandedId === insight.id && (
            <div className="insight-card-detail">
              {insight.detail}
              <div style={{ marginTop: 8 }}>
                <span className="insight-card-metric">{insight.metric}</span>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ============ PAIN POINTS PANEL ============
function PainPointsPanel() {
  return (
    <div className="fade-in">
      <div style={{ fontSize: 12, color: '#718096', marginBottom: 12, lineHeight: 1.6 }}>
        จากการวิเคราะห์ข้อมูล WiFi 189,445 sessions พบปัญหาหลัก 6 ประการ
        พร้อมแนวทางแก้ไขเรียงตามความสำคัญ
      </div>

      {PAIN_POINTS.map(pp => (
        <div
          key={pp.id}
          className="pain-point-card"
          style={{ borderLeftColor: pp.color }}
        >
          <div className="pain-point-title" style={{ color: pp.color }}>
            <span style={{
              display: 'inline-block',
              background: pp.color,
              color: 'white',
              fontSize: 10,
              fontWeight: 700,
              padding: '1px 6px',
              borderRadius: 4,
              marginRight: 8,
            }}>
              {pp.priority}
            </span>
            {pp.title}
          </div>
          <div className="pain-point-desc">{pp.description}</div>
          <div className="pain-point-solution">
            <strong>💡 แนวทางแก้ไข</strong>
            {pp.solution}
          </div>
        </div>
      ))}
    </div>
  )
}

// ============ BUILDING DETAIL PANEL ============
function BuildingDetailPanel({ vizData, selectedBuilding, currentHour, currentDay }) {
  const [viewMode, setViewMode] = useState('now') // 'now' | 'day' | 'total'

  if (!selectedBuilding || !vizData) return null

  const bldg = vizData.buildings.find(b => b.code === selectedBuilding)
  if (!bldg) return (
    <div style={{ padding: 16, fontSize: 13, color: '#718096' }}>
      ไม่พบข้อมูลอาคาร {selectedBuilding}
    </div>
  )

  const quality = classifyRSSI(bldg.avg_rssi)
  const config = WIFI_BUILDINGS[bldg.code]

  // ---------- Building-level data by mode ----------
  const dhKey = `${currentDay}_${currentHour}`
  const nowBldg = vizData.daily_hourly_by_building?.[bldg.code]?.[dhKey] || null
  const dayBldg = vizData.daily_by_building?.[bldg.code]?.[String(currentDay)] || null

  const dayInfo = vizData.day_info?.[String(currentDay)] || {}
  const dayLabel = dayInfo.dow_th ? `${currentDay} ม.ค. (${dayInfo.dow_th})` : `วันที่ ${currentDay}`

  // Choose building-level stats based on mode
  let modeUsers, modeSessions, modeRSSI, modeGB, modeLabel
  if (viewMode === 'now') {
    modeUsers = nowBldg?.users ?? '—'
    modeSessions = nowBldg?.sessions ?? '—'
    modeRSSI = nowBldg?.avg_rssi ?? null
    modeGB = null // hourly doesn't have GB
    modeLabel = `⏰ เวลา ${String(currentHour).padStart(2, '0')}:00 • ${dayLabel}`
  } else if (viewMode === 'day') {
    modeUsers = dayBldg?.users ?? '—'
    modeSessions = dayBldg?.sessions ?? '—'
    modeRSSI = dayBldg?.avg_rssi ?? null
    modeGB = dayBldg?.total_MB ? (dayBldg.total_MB / 1024).toFixed(2) : '—'
    modeLabel = `📅 ${dayLabel}`
  } else {
    modeUsers = bldg.total_users
    modeSessions = bldg.total_sessions
    modeRSSI = bldg.avg_rssi
    modeGB = bldg.total_GB
    modeLabel = '📊 รวมทั้งเดือน (ม.ค. 2569)'
  }

  const modeQuality = modeRSSI ? classifyRSSI(modeRSSI) : quality

  // ---------- Floor data by mode ----------
  const dhFloors = vizData.daily_hourly_floor_by_building?.[bldg.code]?.[dhKey] || {}
  const dayFloors = vizData.daily_floor_by_building?.[bldg.code]?.[String(currentDay)] || {}
  const totalFloors = bldg.floors // overall aggregate

  // Build unified floor list with current mode's values
  const floorList = totalFloors
    .sort((a, b) => a.floor_num - b.floor_num)
    .map(f => {
      const fn = String(f.floor_num)
      if (viewMode === 'now') {
        const d = dhFloors[fn]
        return {
          floor_num: f.floor_num,
          users: d?.users ?? 0,
          sessions: d?.sessions ?? 0,
          avg_rssi: d?.avg_rssi ?? null,
          weak_pct: d?.weak_pct ?? null,
          hasData: !!d,
        }
      } else if (viewMode === 'day') {
        const d = dayFloors[fn]
        return {
          floor_num: f.floor_num,
          users: d?.users ?? 0,
          sessions: d?.sessions ?? 0,
          avg_rssi: d?.avg_rssi ?? null,
          weak_pct: d?.weak_pct ?? null,
          total_MB: d?.total_MB ?? 0,
          hasData: !!d,
        }
      } else {
        return {
          floor_num: f.floor_num,
          users: f.unique_users,
          sessions: f.sessions,
          avg_rssi: f.avg_rssi,
          weak_pct: f.weak_pct,
          total_GB: f.total_GB,
          hasData: true,
        }
      }
    })

  const maxSessions = Math.max(...floorList.map(f => f.sessions), 1)
  const maxUsers = Math.max(...floorList.map(f => f.users), 1)

  return (
    <div className="fade-in">
      {/* Building header */}
      <div className="building-detail-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="building-detail-code" style={{ color: config?.color || '#3182ce' }}>
            {bldg.code}
          </div>
          <span
            className={`building-item-quality ${
              bldg.overall_weak_pct > 70 ? 'quality-poor' :
              bldg.overall_weak_pct > 60 ? 'quality-weak' :
              bldg.overall_weak_pct > 50 ? 'quality-fair' : 'quality-good'
            }`}
          >
            {quality.label}
          </span>
        </div>
        <div className="building-detail-name">{bldg.name}</div>
      </div>

      {/* ========== VIEW MODE TOGGLE ========== */}
      <div style={{
        display: 'flex',
        gap: 0,
        padding: '8px 16px',
        borderBottom: '1px solid #e2e8f0',
        background: '#f7fafc',
      }}>
        {[
          { key: 'now', label: '⏰ ตอนนี้', desc: `${String(currentHour).padStart(2,'0')}:00` },
          { key: 'day', label: '📅 วันนี้', desc: `วันที่ ${currentDay}` },
          { key: 'total', label: '📊 ผลรวม', desc: 'ทั้งเดือน' },
        ].map(m => (
          <button
            key={m.key}
            onClick={() => setViewMode(m.key)}
            style={{
              flex: 1,
              padding: '6px 4px',
              border: '1px solid',
              borderColor: viewMode === m.key ? '#3182ce' : '#e2e8f0',
              background: viewMode === m.key ? '#ebf8ff' : 'white',
              color: viewMode === m.key ? '#2b6cb0' : '#718096',
              fontWeight: viewMode === m.key ? 700 : 400,
              fontSize: 11,
              cursor: 'pointer',
              borderRadius: m.key === 'now' ? '6px 0 0 6px' : m.key === 'total' ? '0 6px 6px 0' : '0',
              fontFamily: 'inherit',
              lineHeight: 1.3,
              transition: 'all 0.15s',
            }}
          >
            <div>{m.label}</div>
            <div style={{ fontSize: 9, opacity: 0.7, marginTop: 1 }}>{m.desc}</div>
          </button>
        ))}
      </div>

      {/* ========== BUILDING STATS ========== */}
      <div style={{
        padding: '10px 16px',
        background: viewMode === 'now' ? '#ebf8ff' : viewMode === 'day' ? '#f0fff4' : '#faf5ff',
        borderBottom: '1px solid #e2e8f0',
        fontSize: 11,
        color: '#4a5568',
      }}>
        <div style={{ fontWeight: 600, marginBottom: 6, fontSize: 10, opacity: 0.7 }}>
          {modeLabel}
        </div>
        <div className="building-detail-stats">
          <div className="building-stat-item">
            <div className="building-stat-value">
              {typeof modeUsers === 'number' ? modeUsers.toLocaleString() : modeUsers}
            </div>
            <div className="building-stat-label">ผู้ใช้</div>
          </div>
          <div className="building-stat-item">
            <div className="building-stat-value">
              {typeof modeSessions === 'number' ? modeSessions.toLocaleString() : modeSessions}
            </div>
            <div className="building-stat-label">Sessions</div>
          </div>
          <div className="building-stat-item">
            <div className="building-stat-value" style={{ color: modeRSSI ? modeQuality.color : '#a0aec0' }}>
              {modeRSSI ? `${modeRSSI} dBm` : '—'}
            </div>
            <div className="building-stat-label">RSSI เฉลี่ย</div>
          </div>
          <div className="building-stat-item">
            <div className="building-stat-value">
              {modeGB != null && modeGB !== '—' ? `${modeGB} GB` : '—'}
            </div>
            <div className="building-stat-label">ข้อมูล</div>
          </div>
        </div>
      </div>

      {/* ========== FLOOR DETAILS ========== */}
      <div style={{ padding: 16 }}>
        <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, display: 'flex', justifyContent: 'space-between' }}>
          <span>📊 รายละเอียดแต่ละชั้น</span>
          <span style={{ fontSize: 10, fontWeight: 400, color: '#a0aec0' }}>
            {viewMode === 'now' ? 'ชม.นี้' : viewMode === 'day' ? 'วันนี้' : 'รวม'}
          </span>
        </h4>
        {floorList.map(floor => {
          const fQuality = floor.avg_rssi ? classifyRSSI(floor.avg_rssi) : null
          const barWidth = (floor.users / maxUsers) * 100

          return (
            <div key={floor.floor_num} className="floor-bar" style={{ opacity: floor.hasData ? 1 : 0.4 }}>
              <div className="floor-bar-label">
                {floor.floor_num === 0 ? 'GF' : `F${floor.floor_num}`}
              </div>
              <div className="floor-bar-graph">
                <div
                  className="floor-bar-fill"
                  style={{
                    width: `${barWidth}%`,
                    background: floor.hasData && floor.weak_pct != null
                      ? qualityColor(floor.weak_pct)
                      : '#cbd5e0',
                    transition: 'width 0.3s, background 0.3s',
                  }}
                />
              </div>
              <div className="floor-bar-value" style={{
                color: fQuality ? fQuality.color : '#a0aec0',
                minWidth: 56,
                textAlign: 'right',
              }}>
                {floor.avg_rssi != null ? `${floor.avg_rssi} dBm` : '—'}
              </div>
              <div className="floor-bar-value" style={{ minWidth: 48, textAlign: 'right' }}>
                {floor.hasData ? `${floor.users.toLocaleString()} คน` : '—'}
              </div>
            </div>
          )
        })}

        {/* No data message for 'now' mode */}
        {viewMode === 'now' && floorList.every(f => !f.hasData) && (
          <div style={{ textAlign: 'center', padding: 16, color: '#a0aec0', fontSize: 12 }}>
            ไม่มีข้อมูลในช่วงเวลานี้
          </div>
        )}
      </div>

      {/* ========== QUALITY SUMMARY ========== */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid #e2e8f0' }}>
        <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>
          📋 สรุปปัญหา
        </h4>
        <div style={{ fontSize: 12, color: '#4a5568', lineHeight: 1.7 }}>
          {bldg.overall_weak_pct > 70 && (
            <div>🔴 สัญญาณอ่อนมาก ({bldg.overall_weak_pct}%) ต้องเพิ่ม AP เร่งด่วน</div>
          )}
          {bldg.overall_weak_pct > 60 && bldg.overall_weak_pct <= 70 && (
            <div>🟡 สัญญาณอ่อน ({bldg.overall_weak_pct}%) ควรเพิ่ม AP</div>
          )}
          {bldg.floors.some(f => f.zero_pct > 10) && (
            <div>⚠️ มีชั้นที่ session ล้มเหลวสูง (Zero Data &gt; 10%)</div>
          )}
          {bldg.floors.some(f => f.unique_aps <= 2) && (
            <div>📡 บางชั้นมี AP เพียง 1-2 จุด coverage ไม่ทั่วถึง</div>
          )}
          {bldg.total_sessions > 50000 && (
            <div>🔥 ปริมาณการใช้งานสูงมาก ({bldg.total_sessions.toLocaleString()} sessions)</div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============ RIGHT PANEL MAIN ============
export default function RightPanel({ panel, vizData, selectedBuilding, isOpen, onClose, onOpen, filterCategory, setFilterCategory, currentHour, currentDay }) {
  const titles = {
    insights: '📊 ผลวิเคราะห์ WiFi',
    painpoints: '⚠️ ปัญหาและแนวทางแก้ไข',
    building: '🏢 รายละเอียดอาคาร',
  }

  // Collapsed state — show a small toggle button
  if (!isOpen) {
    return (
      <div className="right-panel-toggle">
        <button className="right-panel-open-btn" onClick={onOpen} title="เปิดแผงข้อมูล">
          ◀
        </button>
      </div>
    )
  }

  return (
    <div className="right-panel">
      <div className="panel-header">
        <h3>{titles[panel] || 'รายละเอียด'}</h3>
        <button className="panel-close-btn" onClick={onClose} title="ปิดแผงข้อมูล">✕</button>
      </div>
      <div className="panel-content">
        {panel === 'insights' && (
          <InsightsPanel
            filterCategory={filterCategory}
            setFilterCategory={setFilterCategory}
          />
        )}
        {panel === 'painpoints' && <PainPointsPanel />}
        {panel === 'building' && (
          <BuildingDetailPanel
            vizData={vizData}
            selectedBuilding={selectedBuilding}
            currentHour={currentHour}
            currentDay={currentDay}
          />
        )}
      </div>
    </div>
  )
}
