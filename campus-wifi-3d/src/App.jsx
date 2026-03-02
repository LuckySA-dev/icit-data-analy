import React, { useState, useEffect, useCallback } from 'react'
import CampusScene from './components/CampusScene'
import TopNav from './components/TopNav'
import LeftSidebar from './components/LeftSidebar'
import RightPanel from './components/RightPanel'
import TimeSlider from './components/TimeSlider'
import vizDataRaw from '../public/viz_data.json'

export default function App() {
  const [vizData, setVizData] = useState(vizDataRaw)
  const [activeTab, setActiveTab] = useState('3d')
  const [selectedBuilding, setSelectedBuilding] = useState(null)
  const [rightPanel, setRightPanel] = useState('insights') // insights | painpoints | building
  const [showRightPanel, setShowRightPanel] = useState(true)
  const [currentHour, setCurrentHour] = useState(12)
  const [currentDay, setCurrentDay] = useState(7) // Day 7 = Wed, a busy weekday
  const [isPlaying, setIsPlaying] = useState(false)
  const [hoveredBuilding, setHoveredBuilding] = useState(null)
  const [filterCategory, setFilterCategory] = useState('all')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Auto-play time slider (advance hour, wrap to next day)
  useEffect(() => {
    if (!isPlaying) return
    const interval = setInterval(() => {
      setCurrentHour(h => {
        if (h >= 23) {
          setCurrentDay(d => d >= 31 ? 1 : d + 1)
          return 0
        }
        return h + 1
      })
    }, 800)
    return () => clearInterval(interval)
  }, [isPlaying])

  const handleBuildingClick = useCallback((code) => {
    setSelectedBuilding(code)
    setRightPanel('building')
    setShowRightPanel(true)
  }, [])

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab)
    if (tab === 'insights') {
      setRightPanel('insights')
      setShowRightPanel(true)
    } else if (tab === 'painpoints') {
      setRightPanel('painpoints')
      setShowRightPanel(true)
    } else if (tab === '3d') {
      if (selectedBuilding) {
        setRightPanel('building')
      }
    }
  }, [selectedBuilding])

  if (!vizData) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: '#f0f4f8', fontFamily: 'IBM Plex Sans Thai',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📡</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>กำลังโหลดข้อมูล...</div>
          <div style={{ fontSize: 13, color: '#718096', marginTop: 8 }}>KMUTNB WiFi Campus Dashboard</div>
        </div>
      </div>
    )
  }

  return (
    <>
      <TopNav
        activeTab={activeTab}
        onTabChange={handleTabChange}
        vizData={vizData}
        currentHour={currentHour}
      />
      <div className="main-layout">
        <LeftSidebar
          vizData={vizData}
          selectedBuilding={selectedBuilding}
          onBuildingClick={handleBuildingClick}
          currentHour={currentHour}
          currentDay={currentDay}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(c => !c)}
        />
        <div className="canvas-area">
          <CampusScene
            vizData={vizData}
            selectedBuilding={selectedBuilding}
            onBuildingClick={handleBuildingClick}
            currentHour={currentHour}
            currentDay={currentDay}
            hoveredBuilding={hoveredBuilding}
            setHoveredBuilding={setHoveredBuilding}
          />
          <TimeSlider
            currentHour={currentHour}
            setCurrentHour={setCurrentHour}
            currentDay={currentDay}
            setCurrentDay={setCurrentDay}
            isPlaying={isPlaying}
            setIsPlaying={setIsPlaying}
            vizData={vizData}
          />
        </div>
        <RightPanel
          panel={rightPanel}
          vizData={vizData}
          selectedBuilding={selectedBuilding}
          isOpen={showRightPanel}
          onClose={() => setShowRightPanel(false)}
          onOpen={() => setShowRightPanel(true)}
          filterCategory={filterCategory}
          setFilterCategory={setFilterCategory}
          currentHour={currentHour}
          currentDay={currentDay}
        />
      </div>
    </>
  )
}
