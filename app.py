import streamlit as st
import cv2
import time
from PIL import Image

# ------------------------------------------------------------------
# CONFIGURATION & INITIALIZATION
# ------------------------------------------------------------------
st.set_page_config(page_title="AI Smart Inspection POC", layout="wide")

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
    
    # ------------------------------------------------------------------
    # 🛠️ [แผนรบใหม่] ใช้ HTML5 Video + JavaScript บังคับให้เบราว์เซอร์เปิดหน้าต่างสลับกล้อง
    # ------------------------------------------------------------------
    st.markdown("### 📽️ หน้าต่างดึงภาพจากกล้องหน้างาน")
    st.caption("💡 **วิธีแก้ปัญหากล้องนิ่ง:** เมื่อกดปุ่ม 'เปิดกล้องอุตสาหกรรม' แล้ว หากภาพยังเป็นกล้องหน้าโน้ตบุ๊ก ให้พนักงานคลิกปุ่มสลับกล้องที่จอกล้องได้เลย ระบบจะบังคับตัดสลับไปกล้อง USB ทันที")
    
    # ฝังระบบเครื่องเล่นวิดีโอแบบเลือกกล้องได้เองลงหน้าเว็บ ไม่ต้องง้อสิทธิ์รากเบราว์เซอร์
    html_camera_script = """
    <div style="text-align:center;">
        <video id="webcam" autoplay playsinline width="100%" style="border-radius:10px; background:#333; max-width:640px; min-height:480px;"></video>
        <br><br>
        <button id="btn-toggle" style="padding:10px 20px; font-size:16px; background-color:#11caa0; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">📸 เปิดกล้องอุตสาหกรรม</button>
        <button id="btn-switch" style="padding:10px 20px; font-size:16px; background-color:#3b82f6; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; margin-left:10px;">🔄 สลับไปกล้อง USB ตัวนอก</button>
    </div>

    <script>
        const video = document.getElementById('webcam');
        const btnToggle = document.getElementById('btn-toggle');
        const btnSwitch = document.getElementById('btn-switch');
        let currentStream = null;
        let useFacingMode = "user"; // เริ่มต้นที่กล้องหน้า

        async function startWebcam(facingMode) {
            if (currentStream) {
                currentStream.getTracks().forEach(track => track.stop());
            }
            try {
                // บังคับให้เบราว์เซอร์ควานหาอุปกรณ์กล้องทั้งหมด
                const constraints = {
                    video: { facingMode: facingMode, width: 640, height: 480 }
                };
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
            } catch (err) {
                console.error("Error accessing webcam: ", err);
                alert("ไม่สามารถเข้าถึงกล้องได้ โปรดตรวจสอบการต่อสาย USB หรือกดอนุญาตสิทธิ์กล้องที่มุมบนเว็บครับพี่");
            }
        }

        btnToggle.addEventListener('click', () => {
            startWebcam(useFacingMode);
        });

        btnSwitch.addEventListener('click', async () => {
            // ทริคเด็ด: สั่งสลับ Mode การดึงกล้อง จากกล้องหน้า (user) เป็นกล้องนอก/กล้องหลัง (environment)
            useFacingMode = (useFacingMode === "user") ? "environment" : "user";
            await startWebcam(useFacingMode);
        });
    </script>
    """
    
    # รันโค้ดสลับกล้องทะลวงบล็อกเบราว์เซอร์
    st.components.v1.html(html_camera_script, height=560)

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
    
    st.write("**สถานะการแยกแยะชิ้นงานย่อย:**")
    for item in TARGET_CLASSES:
        if st.session_state.sim_status == "OK":
            st.markdown(f"🔹 {item}: <span style='color:#11caa0; font-weight:bold;'>Detected</span>", unsafe_allow_html=True)
        elif st.session_state.sim_status == "NG" and "O-Ring" in item:
            st.markdown(f"🔹 {item}: <span style='color:#ef4444; font-weight:bold;'>Missing / Occluded (โดนบัง)</span>", unsafe_allow_html=True)
        else:
            st.write(f"🔹 {item}: Standby...")
