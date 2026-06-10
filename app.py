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

# ------------------------------------------------------------------
# UI DESIGN: DASHBOARD
# ------------------------------------------------------------------
st.title("🏭 AI Smart Inspection Dashboard (POC Stage)")
st.write("สถานีทดสอบระบบตรวจจับวัตถุ 5 ไอเทมหลัก - ป้องกันพนักงานสับขาหลอก")
st.markdown("---")

col_cam, col_result = st.columns([3, 2])

with col_cam:
    st.subheader("📸 ข้อ 4: ทดสอบการทำงานของระบบกล้อง")
    
    # ดึงฟังก์ชันกล้องเว็บแคมผ่านระบบเบราว์เซอร์ของ Streamlit Direct
    # ตัวนี้พอนำขึ้นระบบ share.streamlit.io จะเปิดใช้งานกล้องของโน้ตบุ๊กพี่ได้ทันที
    cam_image = st.camera_input("ส่องกล้องลงไปที่ก้นกล่องบรรจุชิ้นงานเพื่อทดสอบสัญญาณภาพ")
    
    if cam_image:
        st.success("🟢 สัญญาณภาพจากกล้องใช้งานได้ปกติ!")

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
            "</div>", unsafe_style_allowed=True
        )
    elif st.session_state.sim_status == "NG":
        st.markdown(
            "<div style='background-color:#ef4444; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>REJECT (NG) 🚨</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>ตรวจพบสิ่งผิดปกติ! สินค้าไม่ครบ 5 ชิ้น</p>"
            "</div>", unsafe_style_allowed=True
        )
    else:
        st.markdown(
            "<div style='background-color:#64748b; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>SYSTEM READY</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>รอกล่องถัดไปเข้าจุดสแกนภาพ</p>"
            "</div>", unsafe_style_allowed=True
        )

    st.write("")
    st.metric(label="จำนวนวัตถุที่ระบบนับได้ในกล่อง", value=f"{st.session_state.sim_count} / 5 ชิ้น")
    
    # แสดงรายการสถานะไอเทมรายชิ้น
    st.write("**สถานะการแยกแยะชิ้นงานย่อย:**")
    for item in TARGET_CLASSES:
        if st.session_state.sim_status == "OK":
            st.markdown(f"🔹 {item}: <span style='color:#11caa0; font-weight:bold;'>Detected</span>", unsafe_style_allowed=True)
        elif st.session_state.sim_status == "NG" and "O-Ring" in item:
            st.markdown(f"🔹 {item}: <span style='color:#ef4444; font-weight:bold;'>Missing / Occluded (โดนบัง)</span>", unsafe_style_allowed=True)
        else:
            st.write(f"🔹 {item}: Standby...")
