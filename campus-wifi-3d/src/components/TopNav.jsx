import React from 'react'

const TABS = [
  { key: '3d', label: 'แผนที่ 3D' },
  { key: 'insights', label: 'วิเคราะห์' },
  { key: 'painpoints', label: 'ปัญหา & แนวทาง' },
]

export default function TopNav({ activeTab, onTabChange, vizData, currentHour }) {
  const summary = vizData?.summary || {}
  return (
    <nav className="top-nav">
      <div className="top-nav-left">
        <div className="top-nav-logo">มจพ</div>
        <div>
          <div className="top-nav-title">KMUTNB WiFi Campus Dashboard</div>
          <div className="top-nav-subtitle">ระบบวิเคราะห์คุณภาพ WiFi มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ</div>
        </div>
      </div>

      <div className="top-nav-tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`top-nav-tab ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => onTabChange(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="top-nav-right">
        <div className="stat-pill">
          <span>ผู้ใช้ทั้งหมด</span>
          <span className="stat-pill-value">{summary.total_users?.toLocaleString()}</span>
        </div>
        <div className="stat-pill">
          <span>Sessions</span>
          <span className="stat-pill-value">{summary.total_sessions?.toLocaleString()}</span>
        </div>
        <div className="stat-pill">
          <span>RSSI เฉลี่ย</span>
          <span className="stat-pill-value" style={{
            color: summary.avg_rssi < -73 ? '#e53e3e' : summary.avg_rssi < -67 ? '#d69e2e' : '#38a169'
          }}>
            {summary.avg_rssi} dBm
          </span>
        </div>
      </div>
    </nav>
  )
}
