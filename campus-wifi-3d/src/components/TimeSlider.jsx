import React from 'react'

export default function TimeSlider({
  currentHour, setCurrentHour,
  currentDay, setCurrentDay,
  isPlaying, setIsPlaying,
  vizData
}) {
  const dayInfo = vizData?.day_info || {}
  const dailyHourlyCampus = vizData?.daily_hourly_campus || {}
  const dailyCampus = vizData?.daily_campus || {}

  // Get data for current day+hour combo
  const dhKey = `${currentDay}_${currentHour}`
  const hourData = dailyHourlyCampus[dhKey] || {}
  const dayData = dailyCampus[String(currentDay)] || {}
  const info = dayInfo[String(currentDay)] || {}

  const isWeekend = !info.is_weekday

  const periodLabel = (h) => {
    if (h >= 6 && h < 12) return '🌅 เช้า'
    if (h >= 12 && h < 14) return '☀️ กลางวัน'
    if (h >= 14 && h < 18) return '🌤️ บ่าย'
    if (h >= 18 && h < 22) return '🌙 เย็น'
    return '🌃 กลางคืน'
  }

  // Day labels for the calendar strip
  const dayOfWeekShort = {
    'จันทร์': 'จ', 'อังคาร': 'อ', 'พุธ': 'พ',
    'พฤหัสบดี': 'พฤ', 'ศุกร์': 'ศ', 'เสาร์': 'ส', 'อาทิตย์': 'อา'
  }

  return (
    <div className="time-slider-bar">
      {/* Play/Pause */}
      <button
        className="play-btn"
        onClick={() => setIsPlaying(!isPlaying)}
        title={isPlaying ? 'หยุด' : 'เล่น'}
      >
        {isPlaying ? '⏸' : '▶'}
      </button>

      {/* Time & Date display */}
      <div className="time-date-display">
        <div className="time-display-hour">
          {String(currentHour).padStart(2, '0')}:00
        </div>
        <div className="time-display-date">
          {currentDay} ม.ค. ({info.dow_th || ''})
        </div>
        <div className="time-display-label">{periodLabel(currentHour)}</div>
      </div>

      {/* Sliders */}
      <div className="time-slider-tracks">
        {/* Day calendar strip */}
        <div className="day-strip">
          <span className="strip-label">วัน:</span>
          <div className="day-strip-scroll">
            {Array.from({ length: 31 }, (_, i) => {
              const d = i + 1
              const di = dayInfo[String(d)] || {}
              const isWE = !di.is_weekday
              const isCurrent = d === currentDay
              const daySessions = (dailyCampus[String(d)] || {}).sessions || 0
              const intensity = Math.min(daySessions / 11000, 1)

              return (
                <button
                  key={d}
                  className={`day-cell ${isCurrent ? 'active' : ''} ${isWE ? 'weekend' : ''}`}
                  style={{
                    '--intensity': intensity,
                  }}
                  onClick={() => setCurrentDay(d)}
                  title={`${d} ม.ค. 2026 (${di.dow_th || ''}) — ${daySessions.toLocaleString()} sessions`}
                >
                  <span className="day-cell-dow">{dayOfWeekShort[di.dow_th] || ''}</span>
                  <span className="day-cell-num">{d}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Hour slider */}
        <div className="hour-slider-row">
          <span className="strip-label">เวลา:</span>
          <div className="time-slider-track">
            <input
              type="range"
              className="time-slider-input"
              min={0}
              max={23}
              value={currentHour}
              onChange={(e) => setCurrentHour(parseInt(e.target.value))}
            />
            <div className="time-labels">
              {[0, 3, 6, 9, 12, 15, 18, 21, 23].map(h => (
                <span key={h} className="time-label" style={{
                  left: `${(h / 23) * 100}%`,
                }}>
                  {String(h).padStart(2, '0')}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stats for this day+hour */}
      <div className="time-stats-group">
        <div className="time-stat-box">
          <div className="time-stats-value" style={{
            color: (hourData.users || 0) > 500 ? '#e53e3e' :
                   (hourData.users || 0) > 200 ? '#d69e2e' : '#38a169'
          }}>
            {(hourData.users || 0).toLocaleString()}
          </div>
          <div className="time-stats-label">ผู้ใช้ (ชม.นี้)</div>
        </div>

        <div className="time-stat-box">
          <div className="time-stats-value">
            {(dayData.sessions || 0).toLocaleString()}
          </div>
          <div className="time-stats-label">Sessions (วันนี้)</div>
        </div>

        <div className="time-stat-box">
          <div className="time-stats-value" style={{
            color: (hourData.avg_rssi || dayData.avg_rssi || 0) < -73 ? '#e53e3e' :
                   (hourData.avg_rssi || dayData.avg_rssi || 0) < -67 ? '#d69e2e' : '#38a169'
          }}>
            {hourData.avg_rssi || dayData.avg_rssi || '--'}
          </div>
          <div className="time-stats-label">RSSI {isWeekend ? '(วันหยุด)' : ''}</div>
        </div>
      </div>
    </div>
  )
}
