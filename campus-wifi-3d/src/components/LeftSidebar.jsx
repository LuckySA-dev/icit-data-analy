import React, { useState } from 'react'
import { WIFI_BUILDINGS, classifyRSSI, qualityColor } from '../data/campusData'

export default function LeftSidebar({ vizData, selectedBuilding, onBuildingClick, currentHour, currentDay, collapsed, onToggleCollapse }) {
  const [expandedBuilding, setExpandedBuilding] = useState(null)
  const buildings = vizData?.buildings || []
  const dailyHourlyData = vizData?.daily_hourly_by_building || {}
  const dailyData = vizData?.daily_by_building || {}
  const dayInfo = vizData?.day_info || {}
  const info = dayInfo[String(currentDay)] || {}
  const dayLabel = info.dow_th || ''

  const campusDH = vizData?.daily_hourly_campus?.[`${currentDay}_${currentHour}`] || null

  // Sort buildings by current hour users (descending)
  const sortedBuildings = [...buildings].sort((a, b) => {
    const aU = dailyHourlyData?.[a.code]?.[`${currentDay}_${currentHour}`]?.users || 0
    const bU = dailyHourlyData?.[b.code]?.[`${currentDay}_${currentHour}`]?.users || 0
    return bU - aU
  })

  const totalCurrentUsers = sortedBuildings.reduce((sum, b) => {
    return sum + (dailyHourlyData?.[b.code]?.[`${currentDay}_${currentHour}`]?.users || 0)
  }, 0)

  // === COLLAPSED MODE ===
  if (collapsed) {
    return (
      <div className="left-sidebar left-sidebar-collapsed">
        <button className="sidebar-toggle-btn" onClick={onToggleCollapse} title="เปิดเมนูอาคาร">
          <span style={{ fontSize: 18 }}>☰</span>
        </button>
        <div className="sidebar-collapsed-icons">
          {sortedBuildings.map(bldg => {
            const hourData = dailyHourlyData?.[bldg.code]?.[`${currentDay}_${currentHour}`] || null
            const users = hourData?.users || 0
            const isActive = selectedBuilding === bldg.code
            const config = WIFI_BUILDINGS[bldg.code]
            return (
              <button
                key={bldg.code}
                className={`sidebar-collapsed-item ${isActive ? 'active' : ''}`}
                onClick={() => onBuildingClick(bldg.code)}
                title={`${bldg.code} - ${users} คน`}
                style={{ borderColor: isActive ? (config?.color || '#3182ce') : 'transparent' }}
              >
                <span className="sidebar-collapsed-code" style={{ color: config?.color || '#3182ce' }}>
                  {bldg.code.replace('B', '')}
                </span>
                {users > 0 && (
                  <span className={`sidebar-collapsed-count ${
                    users > 200 ? 'count-high' : users > 50 ? 'count-mid' : 'count-low'
                  }`}>{users}</span>
                )}
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  // === EXPANDED MODE ===
  return (
    <div className="left-sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3>🏢 อาคาร WiFi ({buildings.length})</h3>
          <button className="sidebar-toggle-btn" onClick={onToggleCollapse} title="พับเมนู">◀</button>
        </div>
        <div className="sidebar-live-bar">
          <div className="sidebar-live-indicator">
            <span className="live-dot" />
            <span>{currentDay} ม.ค. {dayLabel} • {String(currentHour).padStart(2, '0')}:00</span>
          </div>
          <div className="sidebar-live-stats">
            <span>👤 <strong>{totalCurrentUsers.toLocaleString()}</strong></span>
            {campusDH && (
              <span style={{ color: campusDH.avg_rssi < -73 ? '#e53e3e' : '#38a169' }}>
                📶 <strong>{campusDH.avg_rssi} dBm</strong>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Building list */}
      <div className="sidebar-content">
        {sortedBuildings.map(bldg => {
          const quality = classifyRSSI(bldg.avg_rssi)
          const config = WIFI_BUILDINGS[bldg.code]
          const hourData = dailyHourlyData?.[bldg.code]?.[`${currentDay}_${currentHour}`] || null
          const dayData = dailyData?.[bldg.code]?.[String(currentDay)] || null
          const isActive = selectedBuilding === bldg.code
          const isExpanded = expandedBuilding === bldg.code

          const curUsers = hourData?.users ?? 0
          const curRSSI = hourData?.avg_rssi ?? null
          const curQuality = curRSSI ? classifyRSSI(curRSSI) : null
          const dayUsers = dayData?.users ?? 0

          const peakUsers = vizData?.max_users_per_building?.[bldg.code] || 1
          const loadPct = (curUsers / peakUsers) * 100

          return (
            <div key={bldg.code} className={`building-item ${isActive ? 'active' : ''}`}>
              {/* Main clickable row */}
              <div className="building-item-main" onClick={() => onBuildingClick(bldg.code)}>
                <div className="building-item-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="building-item-code" style={{ color: config?.color || '#3182ce' }}>
                      {bldg.code}
                    </span>
                    {curUsers > 0 ? (
                      <span className={`building-live-badge ${
                        loadPct > 70 ? 'load-high' : loadPct > 30 ? 'load-mid' : 'load-low'
                      }`}>{curUsers.toLocaleString()} คน</span>
                    ) : (
                      <span className="building-live-badge load-zero">ไม่มีผู้ใช้</span>
                    )}
                  </div>
                  <button
                    className="building-expand-btn"
                    onClick={(e) => { e.stopPropagation(); setExpandedBuilding(isExpanded ? null : bldg.code) }}
                    title={isExpanded ? 'ย่อ' : 'ขยาย'}
                  >{isExpanded ? '▲' : '▼'}</button>
                </div>

                <div className="building-item-name">{bldg.name}</div>

                {/* Load progress bar */}
                <div className="building-load-bar">
                  <div className="building-load-fill" style={{
                    width: `${Math.min(loadPct, 100)}%`,
                    background: loadPct > 70 ? '#e53e3e' : loadPct > 30 ? '#d69e2e' : curUsers > 0 ? '#38a169' : '#cbd5e0',
                    transition: 'width 0.5s ease, background 0.3s',
                  }} />
                </div>

                {/* Quick stats */}
                <div className="building-item-quick">
                  <span>📶 <span style={{ color: curQuality ? curQuality.color : '#a0aec0', fontWeight: 600 }}>
                    {curRSSI != null ? `${curRSSI} dBm` : '—'}
                  </span></span>
                  <span style={{ color: '#e2e8f0' }}>|</span>
                  <span>🏢 {bldg.floor_count} ชั้น</span>
                  <span style={{ color: '#e2e8f0' }}>|</span>
                  <span>📅 วันนี้ {dayUsers.toLocaleString()} คน</span>
                </div>
              </div>

              {/* Expandable detail */}
              {isExpanded && (
                <div className="building-item-detail fade-in">
                  <div className="building-detail-grid">
                    <div className="mini-stat">
                      <div className="mini-stat-val">{bldg.total_users.toLocaleString()}</div>
                      <div className="mini-stat-label">ผู้ใช้ (เดือน)</div>
                    </div>
                    <div className="mini-stat">
                      <div className="mini-stat-val">{bldg.total_sessions.toLocaleString()}</div>
                      <div className="mini-stat-label">Sessions</div>
                    </div>
                    <div className="mini-stat">
                      <div className="mini-stat-val">{bldg.total_GB.toLocaleString()} GB</div>
                      <div className="mini-stat-label">ข้อมูล</div>
                    </div>
                    <div className="mini-stat">
                      <div className="mini-stat-val" style={{ color: quality.color }}>{bldg.avg_rssi} dBm</div>
                      <div className="mini-stat-label">RSSI เฉลี่ย</div>
                    </div>
                  </div>
                  {/* Signal quality bar */}
                  <div className="building-signal-row">
                    <span style={{ fontSize: 10, color: '#718096' }}>สัญญาณอ่อน</span>
                    <div className="signal-bar-bg">
                      <div className="signal-bar-fill" style={{
                        width: `${bldg.overall_weak_pct}%`,
                        background: qualityColor(bldg.overall_weak_pct),
                      }} />
                    </div>
                    <span style={{
                      fontSize: 11, fontWeight: 600,
                      color: bldg.overall_weak_pct > 70 ? '#e53e3e' : bldg.overall_weak_pct > 60 ? '#d69e2e' : '#38a169',
                    }}>{bldg.overall_weak_pct}%</span>
                  </div>
                  {/* Floor chips (live) */}
                  <div className="building-floor-preview">
                    {bldg.floors.sort((a, b) => a.floor_num - b.floor_num).map(f => {
                      const floorDH = vizData?.daily_hourly_floor_by_building?.[bldg.code]?.[`${currentDay}_${currentHour}`]?.[String(f.floor_num)] || null
                      const fu = floorDH?.users ?? 0
                      const wp = floorDH?.weak_pct
                      return (
                        <div key={f.floor_num} className="floor-mini-chip" style={{
                          background: fu > 0
                            ? (wp > 70 ? 'rgba(229,62,62,0.12)' : wp > 60 ? 'rgba(214,158,46,0.12)' : 'rgba(56,161,105,0.12)')
                            : '#f7fafc',
                          borderColor: fu > 0
                            ? (wp > 70 ? '#feb2b2' : wp > 60 ? '#fefcbf' : '#c6f6d5')
                            : '#e2e8f0',
                        }}>
                          <span className="floor-mini-name">{f.floor_num === 0 ? 'G' : `F${f.floor_num}`}</span>
                          <span className="floor-mini-count">{fu > 0 ? fu : '—'}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
