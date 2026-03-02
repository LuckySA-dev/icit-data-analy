/**
 * KMUTNB Campus Building Data
 * Positions approximated from the campus map image
 * Coordinate system: X = East-West, Z = North-South (Three.js convention)
 * Origin roughly at campus center
 */

// Buildings with WiFi data (from dataset)
// Positions spread across campus using a ~120x100 unit area
export const WIFI_BUILDINGS = {
  B25: {
    code: 'B25',
    name: 'อาคารอเนกประสงค์',
    nameEn: 'Multipurpose Building',
    position: [5, 0, -8],
    size: [4.5, 9, 3.5],  // w, maxH, d
    floors: 10,
    color: '#3182ce',
  },
  B31: {
    code: 'B31',
    name: 'อาคารนวมินทรราชินี',
    nameEn: 'Navamindrarachinee Building',
    position: [18, 0, -28],
    size: [4.5, 10, 3.5],
    floors: 11,
    color: '#805ad5',
  },
  B46: {
    code: 'B46',
    name: 'อาคารศิลปศาสตร์ประยุกต์',
    nameEn: 'Applied Arts & Cafeteria',
    position: [22, 0, 8],
    size: [5, 4.5, 4],
    floors: 5,
    color: '#d69e2e',
  },
  B67: {
    code: 'B67',
    name: 'วิทยาลัยเทคโนโลยีอุตสาหกรรม',
    nameEn: 'College of Industrial Technology',
    position: [-18, 0, -5],
    size: [6, 3, 5],
    floors: 3,
    color: '#38a169',
  },
  B77: {
    code: 'B77',
    name: 'อาคาร 40 ปี มจพ.',
    nameEn: '40th Anniversary & Canteen',
    position: [0, 0, 5],
    size: [5.5, 6.5, 4.5],
    floors: 7,
    color: '#e53e3e',
  },
  B79: {
    code: 'B79',
    name: 'สโมสรบุคลากร มจพ.',
    nameEn: 'Staff Club',
    position: [-8, 0, 12],
    size: [3.5, 1.2, 3],
    floors: 1,
    color: '#319795',
  },
};

// Other campus buildings (context only, spread out)
export const OTHER_BUILDINGS = [
  // === North campus ===
  { code: 'B52', name: 'อาคาร Sirindhorn', position: [12, 0, -36], size: [4, 3.5, 3.5] },
  { code: 'B63', name: 'อาคารบัณฑิตวิทยาลัยวิศวกรรมศาสตร์', position: [26, 0, -34], size: [3.5, 4, 3] },
  { code: 'B65', name: 'ศูนย์เครื่องมือ STRI', position: [4, 0, -32], size: [3.5, 2, 3] },
  
  // === Central ===
  { code: 'B96', name: 'สำนักหอสมุดกลาง', position: [-10, 0, -16], size: [4, 3, 3.5] },
  { code: 'B40', name: 'สำนักพัฒนาเทคนิคศึกษา', position: [14, 0, -14], size: [3.5, 3.5, 3] },
  { code: 'B41', name: 'อาคาร ICIT', position: [6, 0, -20], size: [3, 2.5, 2.5] },
  { code: 'B72', name: 'อาคารปฏิบัติการ', position: [-8, 0, 0], size: [3, 2, 2.5] },
  { code: 'B73', name: 'อาคารเรียนรวม', position: [-14, 0, 8], size: [3.5, 2.5, 3] },
  
  // === South campus ===
  { code: 'B44', name: 'อาคารพื้นที่การเรียนรู้', position: [10, 0, 14], size: [3, 2.5, 2.5] },
  { code: 'B47', name: 'อาคารวิทยาลัยนานาชาติ', position: [0, 0, 20], size: [3.5, 3.5, 3] },
  { code: 'B11', name: 'อาคารคณะพัฒนาธุรกิจ', position: [-20, 0, 18], size: [3.5, 2.5, 3] },
  { code: 'B12', name: 'อาคารจอดรถ', position: [-30, 0, 10], size: [4, 3, 4] },
  
  // === West campus ===
  { code: 'B81', name: 'อาคารเรียน 81', position: [-28, 0, -12], size: [3, 3, 2.5] },
  { code: 'B82', name: 'อาคาร 82', position: [-28, 0, -22], size: [3, 2.5, 2.5] },
  { code: 'B98', name: 'สนามกีฬา', position: [-32, 0, -30], size: [6, 0.3, 8] },
  
  // === East campus ===
  { code: 'B93', name: 'อาคารสถาบันนวัตกรรม', position: [32, 0, -18], size: [3.5, 3, 3] },
];

// All buildings combined
export const ALL_BUILDING_CODES = [
  ...Object.keys(WIFI_BUILDINGS),
  ...OTHER_BUILDINGS.map(b => b.code),
];

// RSSI quality classification
export function classifyRSSI(rssi) {
  if (rssi >= -50) return { label: 'ดีมาก', labelEn: 'Excellent', color: '#276749', bg: '#c6f6d5' };
  if (rssi >= -60) return { label: 'ดี', labelEn: 'Very Good', color: '#2f855a', bg: '#c6f6d5' };
  if (rssi >= -67) return { label: 'พอใช้', labelEn: 'Good', color: '#38a169', bg: '#c6f6d5' };
  if (rssi >= -70) return { label: 'ปานกลาง', labelEn: 'Fair', color: '#d69e2e', bg: '#fefcbf' };
  if (rssi >= -80) return { label: 'อ่อน', labelEn: 'Weak', color: '#e53e3e', bg: '#fed7d7' };
  return { label: 'แย่มาก', labelEn: 'Very Poor', color: '#9b2c2c', bg: '#feb2b2' };
}

// Quality to color mapping for buildings
export function qualityColor(weakPct) {
  if (weakPct < 40) return '#38a169';  // green
  if (weakPct < 55) return '#68d391';  // light green
  if (weakPct < 65) return '#d69e2e';  // yellow
  if (weakPct < 75) return '#ed8936';  // orange
  return '#e53e3e';                     // red
}

// Density to color
export function densityColor(value, max) {
  const ratio = Math.min(value / max, 1);
  if (ratio < 0.2) return '#c6f6d5';
  if (ratio < 0.4) return '#9ae6b4';
  if (ratio < 0.6) return '#fefcbf';
  if (ratio < 0.8) return '#fed7d7';
  return '#fc8181';
}

// Insights data (Thai)
export const INSIGHTS = [
  {
    id: 1,
    icon: '📶',
    category: 'สัญญาณ',
    title: 'สัญญาณ WiFi อ่อนทั่วทั้งมหาวิทยาลัย',
    subtitle: 'RSSI เฉลี่ย -73.3 dBm',
    detail: '68.6% ของ session ทั้งหมดมีสัญญาณอ่อน (RSSI ≤ -71 dBm) อาคาร B77 ชั้น 6 มีสัญญาณอ่อนถึง 81.5% และ B25 ชั้น 9 มี RSSI เฉลี่ย -81.2 ซึ่งแย่มาก',
    metric: '68.6% สัญญาณอ่อน',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 2,
    icon: '🏢',
    category: 'อาคาร',
    title: 'B77 มีปริมาณการใช้งานสูงสุด',
    subtitle: '82,875 sessions / เดือน',
    detail: 'อาคาร 40 ปี มจพ. มี session มากที่สุดถึง 43.7% ของทั้งหมด แต่มี AP เพียง 16 จุด ทำให้ RSSI เฉลี่ย -74.1 dBm และ 74.6% สัญญาณอ่อน แนะนำเพิ่ม AP อย่างน้อย 8-10 จุด',
    metric: '43.7% ของ sessions',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 3,
    icon: '📱',
    category: 'อุปกรณ์',
    title: 'iPhone/iOS มีสัญญาณแย่กว่า Android',
    subtitle: 'Apple RSSI -75.0 vs Samsung -71.5',
    detail: 'อุปกรณ์ Apple มี RSSI เฉลี่ยแย่กว่า Samsung ถึง 3.5 dBm อาจเกิดจาก RF sensitivity ที่ต่างกัน หรือ roaming behavior ที่ไม่ดีพอ',
    metric: 'Apple = -75.0 dBm',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
  {
    id: 4,
    icon: '⏰',
    category: 'เวลา',
    title: 'ช่วงพีค 11:00-13:00 สัญญาณตกลงอย่างชัดเจน',
    subtitle: 'ผู้ใช้พร้อมกัน 4,000+ คน',
    detail: 'เวลา 12:00 มี sessions สูงสุด 26,153 ต่อชั่วโมง RSSI ลดลง 2-3 dBm เมื่อเทียบกับช่วง off-peak ชี้ให้เห็นว่า AP ไม่เพียงพอรับโหลด',
    metric: 'Peak 26,153 sessions/hr',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 5,
    icon: '📡',
    category: 'AP',
    title: 'AP กระจายไม่ทั่วถึง - Dead Zones จำนวนมาก',
    subtitle: 'บางชั้นมี AP เพียง 1-2 จุด',
    detail: 'B25 มี 8 ชั้น แต่หลายชั้นมีเพียง 3-4 AP B77 FL3 มีนักศึกษามากแต่ AP มีเพียง 2 จุด ทำให้ coverage ไม่ทั่วถึง',
    metric: '2 APs/ชั้น (บางที่)',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
  {
    id: 6,
    icon: '🌐',
    category: 'เครือข่าย',
    title: 'eduroam vs @KMUTNB มีคุณภาพต่างกัน',
    subtitle: 'eduroam เร็วกว่า 40%+',
    detail: 'eduroam: RSSI -72.1 dBm, ข้อมูลเฉลี่ย 95 MB/session ส่วน @KMUTNB: RSSI -74.8 dBm, 42 MB/session ชี้ว่า QoS config ต่างกัน',
    metric: 'eduroam 2.3x data',
    severity: 'info',
    bgColor: '#BEE3F8',
    iconBg: '#90CDF4',
  },
  {
    id: 7,
    icon: '🔄',
    category: 'Roaming',
    title: '71.5% ผู้ใช้เป็น Roamer - เชื่อมต่อ >3 AP',
    subtitle: 'ปัญหา handover ทำให้สัญญาณหลุด',
    detail: 'ผู้ใช้ส่วนใหญ่ต้องเชื่อมต่อกับ AP หลายจุด ซึ่งทำให้เกิด handover delay และ session drops ผู้ใช้ที่ roam มากกว่า 10 AP มีถึง 20%',
    metric: '71.5% เป็น Roamer',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 8,
    icon: '⬆️',
    category: 'ทราฟฟิก',
    title: 'อัตราส่วน Upload/Download ผิดปกติ 13.6:1',
    subtitle: 'UL มากกว่า DL อย่างมาก',
    detail: 'ปกติแล้ว DL ควรมากกว่า UL แต่ที่ มจพ. พบว่า Upload มากกว่า Download 13.6 เท่า อาจเป็นผลจาก malware, P2P sharing หรือ backup อัตโนมัติ',
    metric: 'UL:DL = 13.6x',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 9,
    icon: '📊',
    category: 'ช่องสัญญาณ',
    title: 'ใช้งานจำนวนช่อง 25 channels - มี bottleneck',
    subtitle: 'Channel 132 มีคนใช้มากสุด',
    detail: 'Channel 132 มี sessions สูงสุด 25,483 ตามด้วย Channel 36 (18,442 sessions) Channel ที่ใช้ 5GHz มีสัญญาณดีกว่า 2.4GHz ประมาณ 5 dBm',
    metric: '25 channels',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
  {
    id: 10,
    icon: '📅',
    category: 'เวลา',
    title: 'วันธรรมดา RSSI ดีกว่าวันหยุด 2.3 dBm',
    subtitle: 'วันธรรมดา -73.3 vs วันหยุด -75.6',
    detail: 'สัญญาณในวันหยุดแย่กว่า แม้คนน้อยกว่า อาจเป็นเพราะ AP บางตัวถูกปิดในวันหยุด หรือ power management ปรับต่ำ',
    metric: 'ต่างกัน 2.3 dBm',
    severity: 'info',
    bgColor: '#BEE3F8',
    iconBg: '#90CDF4',
  },
  {
    id: 11,
    icon: '📶',
    category: 'เทคโนโลยี',
    title: 'WiFi 6 คิดเป็น 74.7% แต่ fail rate สูง 10%',
    subtitle: 'WiFi 6 มีคนใช้มากแต่ AP อาจไม่พอ',
    detail: 'อุปกรณ์ส่วนใหญ่รองรับ WiFi 6 (802.11ax) แต่ fail rate 10% สูงมาก ชี้ว่าไม่ใช่ปัญหาเทคโนโลยี แต่เป็น capacity ที่ไม่พอ',
    metric: 'WiFi 6 fail 10%',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
  {
    id: 12,
    icon: '❌',
    category: 'การเชื่อมต่อ',
    title: '9.1% session ล้มเหลว (Zero Data)',
    subtitle: '17,288 sessions ไม่มีการรับส่งข้อมูลเลย',
    detail: 'มี AP 19 ตัวที่ fail rate เกิน 10% ปัญหาไม่ใช่สัญญาณ (RSSI ดี) แต่เป็นปัญหา authentication, DHCP หรือ capacity',
    metric: '17,288 failed sessions',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 13,
    icon: '🔥',
    category: 'AP',
    title: '31 AP Overloaded - รับคนเกิน 500 คน',
    subtitle: 'AP ที่มีคนมากที่สุดรับ 1,032 คน',
    detail: 'มี 31 AP ที่รับผู้ใช้มากเกิน 500 คนต่อเดือน โดยอันดับ 1 คือ AP ที่ B77 ชั้น 2 รับถึง 1,032 คน ทำให้คุณภาพตก',
    metric: '31 AP Overloaded',
    severity: 'critical',
    bgColor: '#FED7D7',
    iconBg: '#FEB2B2',
  },
  {
    id: 14,
    icon: '🎓',
    category: 'ผู้ใช้',
    title: 'นักศึกษา fail rate สูงกว่าบุคลากร 1.9 เท่า',
    subtitle: 'นักศึกษา 9.5% vs บุคลากร 5.0%',
    detail: 'นักศึกษามีอัตรา session ล้มเหลวเกือบสองเท่าของบุคลากร อาจเป็นเพราะใช้พื้นที่ที่ AP หนาแน่นน้อยกว่า',
    metric: 'นศ. fail 1.9x',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
  {
    id: 15,
    icon: '🏗️',
    category: 'โครงสร้าง',
    title: 'ชั้นสูง (6+) สัญญาณแย่กว่าชั้นล่าง',
    subtitle: 'ชั้น 9-10 RSSI ต่ำกว่า 5+ dBm',
    detail: 'B25 ชั้น 9 มี RSSI -81.2 (แย่มาก) ส่วนชั้น 10 ดีกว่าเพราะมี AP เพิ่ม ปัญหาเกิดจากการวาง AP ไม่เพียงพอในชั้นสูง',
    metric: 'FL9 = -81.2 dBm',
    severity: 'warning',
    bgColor: '#FEFCBF',
    iconBg: '#FAF089',
  },
];

// Pain points (Thai)
export const PAIN_POINTS = [
  {
    id: 1,
    title: 'สัญญาณอ่อนทั่วทั้งมหาวิทยาลัย',
    description: 'RSSI เฉลี่ย -73.3 dBm, 68.6% ต่ำกว่ามาตรฐาน ส่งผลให้อินเทอร์เน็ตช้า ตัดเชื่อมต่อบ่อย',
    solution: 'เพิ่มจำนวน AP อย่างน้อย 30% ในจุดที่สัญญาณอ่อน ปรับ TX Power และ channel planning ใหม่',
    color: '#e53e3e',
    priority: 'P0',
  },
  {
    id: 2,
    title: 'AP ไม่เพียงพอในจุดหนาแน่น',
    description: '31 AP รับผู้ใช้เกิน 500 คน B77 ชั้น 1-2 มีนักศึกษาหนาแน่นแต่ AP มีเพียง 3-5 จุด',
    solution: 'ติดตั้ง AP เพิ่มทันทีในพื้นที่ critical: B77 FL1-2, B25 FL1,FL3,FL9 รวมอย่างน้อย 15 จุด',
    color: '#e53e3e',
    priority: 'P0',
  },
  {
    id: 3,
    title: 'Roaming ไม่ราบรื่น',
    description: '71.5% ผู้ใช้เชื่อมต่อ >3 AP แต่ handover ไม่ seamless ทำให้เกิด session drops',
    solution: 'ใช้ 802.11r/k/v Fast BSS Transition ปรับ RSSI threshold สำหรับ roaming trigger',
    color: '#d69e2e',
    priority: 'P1',
  },
  {
    id: 4,
    title: 'Session ล้มเหลว 9.1%',
    description: '17,288 sessions ไม่มีข้อมูลถ่ายโอน RSSI ดีแต่ connection ไม่สำเร็จ ปัญหา auth/DHCP',
    solution: 'ตรวจ DHCP pool exhaustion, ปรับ RADIUS timeout, เพิ่ม DHCP scope ในชั่วโมงพีค',
    color: '#d69e2e',
    priority: 'P1',
  },
  {
    id: 5,
    title: 'Upload/Download ผิดปกติ',
    description: 'UL:DL = 13.6:1 ผิดปกติมาก อาจมี malware หรือ P2P ไม่พึงประสงค์',
    solution: 'ติดตั้ง traffic monitoring/DPI วิเคราะห์ประเภท traffic ที่ทำให้ UL สูง ตั้ง QoS policy',
    color: '#805ad5',
    priority: 'P1',
  },
  {
    id: 6,
    title: 'Dead Zones ชั้นสูง',
    description: 'ชั้น 6+ ของ B25 และ B77 สัญญาณอ่อนกว่าชั้นล่างอย่างชัดเจน',
    solution: 'เพิ่ม AP ในชั้นสูง โดยเฉพาะ B25 FL9 (-81.2 dBm) และ B77 FL6 (-77.2 dBm)',
    color: '#38a169',
    priority: 'P2',
  },
];

// Category filters
export const CATEGORIES = [
  { key: 'all', label: 'ทั้งหมด' },
  { key: 'สัญญาณ', label: 'สัญญาณ' },
  { key: 'อาคาร', label: 'อาคาร' },
  { key: 'AP', label: 'AP' },
  { key: 'เวลา', label: 'เวลา' },
  { key: 'ผู้ใช้', label: 'ผู้ใช้' },
  { key: 'ทราฟฟิก', label: 'ทราฟฟิก' },
  { key: 'เครือข่าย', label: 'เครือข่าย' },
  { key: 'โครงสร้าง', label: 'โครงสร้าง' },
];
