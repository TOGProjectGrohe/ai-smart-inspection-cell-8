import streamlit as st
import cv2
import time
from PIL import Image

# ------------------------------------------------------------------
# CONFIGURATION & INITIALIZATION
# ------------------------------------------------------------------
st.set_page_config(page_title="AI Smart Inspection POC", layout="wide")

# ไอเทมจำลอง 5 ชิ้นปราบเซียนของพี่
TARGET_CLASSES = ["Manual (คู่มือ)", "Black Tag (ป้ายดำ)", "Red Tag (ป้ายแดง)", "O-Ring (โอริง)", "Filter (ไส้กรอง)"]

if "sim_status" not in st.session_state:
    st.session_state.sim_status = "READY"
if "sim_count" not in st.session_state:
    st.session_state.sim_count = 0

# ==================================================================
# ⚙️ [จุดเปลี่ยนเลขกล้องอยู่ตรงนี้ครับพี่!] 
# ==================================================================
# ปกติกล้องติดโน้ตบุ๊กจะเป็นเลข 0
# พอนำกล้อง IT มาเสียบพอร์ต USB เพิ่ม คอมพิวเตอร์จะมองเป็นเลข 1 หรือ 2
# สลับใช้กล้อง USB: เปลี่ยนจาก 0 เป็น 1 (หรือ 2 ถ้ายังไม่ขึ้น) ได้เลยครับพี่!
CAMERA_INDEX = 2 
# ==================================================================

# ------------------------------------------------------------------
# UI DESIGN: DASHBOARD
# ------------------------------------------------------------------
st.title("🏭 AI Smart Inspection Dashboard (POC Stage)")
st.write("สถานีทดสอบระบบตรวจจับวัตถุ 5 ไอเทมหลัก - ป้องกันพนักงานสับขาหลอก")
st.markdown("---")

col_cam, col_result = st.columns([3, 2])

with col_cam:
    st.subheader("📸 ข้อ 4: ทดสอบการทำงานของระบบกล้อง")
    st.info(f"⚡ กำลังดึงภาพจากกล้อง Hardware หมายเลข: {CAMERA_INDEX} (ผ่าน OpenCV)")
    
    # ปุ่มควบคุมสวิตช์ เปิด-ปิด สตรีมวิดีโอ
    run_cam = st.checkbox("🔌 เปิดระบบดึงสัญญาณภาพจากพอร์ตกล้องจริง", value=True)
    FRAME_WINDOW = st.image([]) # ตัวสร้างหน้าต่างรอรับเฟรมภาพสด
    
    if run_cam:
        # เปิดดึงภาพจากเลขกล้องที่ตั้งไว้ด้านบนตรง ๆ 
        cap = cv2.VideoCapture(CAMERA_INDEX)
        
        # ปรับความละเอียดวิดีโอให้ชัดกระแทกตาพนักงาน
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # ลูปจับภาพสดพ่นขึ้นหน้าจอแบบ Real-time
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # แปลงรหัสสีจากฟอร์แมตดิบ OpenCV (BGR) เป็นฟอร์แมตสากล (RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FRAME_WINDOW.image(frame, caption="Live Stream ส่องก้นกล่องแบบเรียลไทม์")
                st.success("🟢 สัญญาณภาพจากกล้อง Hardware ทำงานปกติ!")
            else:
                st.error("🚨 สัญญาณภาพหลุด! โปรดตรวจสอบว่ามีโปรแกรมอื่นแอบเปิดกล้องตัวนี้อยู่ไหม")
            cap.release()
        else:
            st.error(f"❌ คอมพิวเตอร์ค้นหา กล้องหมายเลข [{CAMERA_INDEX}] ไม่เจอ! (โปรดเปลี่ยนตัวเลข CAMERA_INDEX ในโค้ดเป็น 0 หรือ 2 แล้วกดเซฟใหม่ครับพี่)")
    else:
        st.warning("⏸️ สวิตช์กล้องปิดอยู่")

with col_result:
    st.subheader("📊 ข้อ 5: ทดสอบตรรกะระบบ ผิด-ถูก (OK/NG)")
    st.write("กดปุ่มด้านล่างเพื่อซิมมูเลทจังหวะที่ AI ประมวลผล")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🟢 จำลองของครบ 5 ชิ้น", use_container_width=True):
            st.session_state.sim_status = "OK"
            st.session_state.sim_count = 5
    with c2:
        if st.button("🔴 จำลองโดนบัง/ของขาด", use_container_width=True):
            st.session_state.sim_status = "NG"
            st.session_state.sim_count = 3
    with c3:
        if st.button("🟡 รีเซ็ตสถานะ", use_container_width=True):
            st.session_state.sim_status = "READY"
            st.session_state.sim_count = 0
            
    st.write("---")
    
    # แสดงสัญญาณไฟอุตสาหกรรมบนแดชบอร์ด
    if st.session_state.sim_status == "OK":
        st.markdown(
            "<div style='background-color:#11caa0; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>PASS (OK)</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>ชิ้นงานวางครบถ้วนตาม Standard</p>"
            "</div>", unsafe_allow_html=True
        )
    elif st.session_state.sim_status == "NG":
        st.markdown(
            "<div style='background-color:#ef4444; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>REJECT (NG) 🚨</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>ตรวจพบสิ่งผิดปกติ! สินค้าไม่ครบ 5 ชิ้น</p>"
            "</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background-color:#64748b; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>SYSTEM READY</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>รอกล่องถัดไปเข้าจุดสแกนภาพ</p>"
            "</div>", unsafe_allow_html=True
        )

    st.write("")
    st.metric(label="จำนวนวัตถุที่ระบบนับได้ในกล่อง", value=f"{st.session_state.sim_count} / 5 ชิ้น")
    
    # แสดงรายการสถานะไอเทมรายชิ้น
    st.write("**สถานะการแยกแยะชิ้นงานย่อย:**")
    for item in TARGET_CLASSES:
        if st.session_state.sim_status == "OK":
            st.markdown(f"🔹 {item}: <span style='color:#11caa0; font-weight:bold;'>Detected</span>", unsafe_allow_html=True)
        elif st.session_state.sim_status == "NG" and "O-Ring" in item:
            st.markdown(f"🔹 {item}: <span style='color:#ef4444; font-weight:bold;'>Missing / Occluded (โดนบัง)</span>", unsafe_allow_html=True)
        else:
            st.write(f"🔹 {item}: Standby...")
