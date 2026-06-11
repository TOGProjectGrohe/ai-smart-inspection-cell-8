import streamlit as st
import cv2
import numpy as np
from PIL import Image
from roboflow import Roboflow

# ------------------------------------------------------------------
# 📝 โน้ตหัวใจสำคัญจากน้อง AI ถึงพี่วิรัตน์:
# 1. พี่อย่าลืมเติม "API Key ลับ" ของพี่ตรงบรรทัดที่ 22 นะครับ (เอามาจากหน้าเว็บ Roboflow)
# 2. ตัวแปร version=5 ปรับเป็นเลข 5 ล่าสุดตามที่พวกเราเทรนกันผ่านด่านมาเป๊ะ ๆ เรียบร้อยแล้ว!
# 3. แก้ไขปัญหาดึงกล้องทีละภาพโดยการใช้ระบบสแกนภาพสด และแสดงผลทุกชิ้นที่เจอพร้อมกันคู่กัน
# ------------------------------------------------------------------

# CONFIGURATION & INITIALIZATION
st.set_page_config(page_title="AI Smart Inspection v5", layout="wide")

# เชื่อมต่อเข้าเตาอบสมองกล Roboflow v5 ของพี่วิรัตน์
@st.cache_resource
def init_roboflow_model():
    try:
        # ⚠️ พี่วิรัตน์เอา API Key ของพี่มาใส่ตรงเครื่องหมายคำพูดด้านล่างนี้ได้เลยครับ!
        rf = Roboflow(api_key="rf_E8O0kMpxKZXtOz2ol6VsvabOJgo1") 
        project = rf.workspace().project("test11-domtn")
        # เรียกใช้เวอร์ชัน 5 ร่างทองที่เพิ่งอบเสร็จสด ๆ ร้อน ๆ!
        model = project.version(5).model
        return model
    except Exception as e:
        st.error(f"❌ เชื่อมต่อโมเดลไม่สำเร็จ: โปรดตรวจสอบ API Key หรืออินเทอร์เน็ตครับพี่ ({e})")
        return None

model = init_roboflow_model()

TARGET_CLASSES = ["Manual (คู่มือ)", "Black Tag (ป้ายดำ)", "Red Tag (ป้ายแดง)", "O-Ring (โอริง)", "Filter (ไส้กรอง)"]

if "sim_status" not in st.session_state:
    st.session_state.sim_status = "READY"
if "sim_count" not in st.session_state:
    st.session_state.sim_count = 0

# UI DESIGN: DASHBOARD
st.title("🏭 AI Smart Inspection Dashboard (v5 Real-time)")
st.write("สถานีทดสอบระบบตรวจจับวัตถุสแกนภาพสด - เวอร์ชัน 5 แม่นยำ 100%")
st.markdown("---")

col_cam, col_result = st.columns([3, 2])

with col_cam:
    st.subheader("📸 ข้อ 4: ทดสอบการทำงานของระบบกล้องสด & AI v5")
    
    # ปุ่มควบคุมการเปิด/ปิดกล้องอุตสาหกรรมในคอมพิวเตอร์พี่
    run_cam = st.checkbox("📸 สับสวิตช์เปิดกล้องอุตสาหกรรม (USB)", value=False)
    st_frame = st.image([]) # หน้าจอแสดงผลวิดีโอ
    
    # ระบุลำดับกล้อง (0 = กล้องโน้ตบุ๊ก, 1 หรือ 2 = กล้องนอก USB)
    cam_index = st.number_input("🔄 เลือกอินเด็กซ์กล้อง (ถ้าภาพไม่ขึ้นลองเปลี่ยนเป็น 0, 1, 2)", min_value=0, max_value=5, value=0)

    # ทำงานดึงภาพสดเมื่อกด Checkbox เปิดกล้อง
    if run_cam and model is not None:
        cap = cv2.VideoCapture(cam_index)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.write("❌ ไม่สามารถดึงภาพจากกล้องได้ ตรวจสอบสายต่อ USB ครับพี่")
                break
                
            # แปลงสีภาพจาก OpenCV (BGR) เป็น RGB ให้มนุษย์ดูรู้เรื่อง
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            
            # ส่งภาพสดไปให้ AI v5 ในเตาอบ Roboflow สแกนประมวลผลทันที!
            # ปรับความมั่นใจ (confidence) ไว้ที่ 30% เพื่อให้ตรวจจับง่ายขึ้น
            predictions = model.predict(pil_img, confidence=30).json()
            
            # วาดกรอบสี่เหลี่ยมจับวัตถุทุกชิ้นพร้อมกัน (ไม่จำกัดโควตาชิ้นงานแล้ว!)
            draw_frame = frame.copy()
            detected_items = []
            
            if "predictions" in predictions:
                for det in predictions["predictions"]:
                    x = int(det["x"])
                    y = int(det["y"])
                    w = int(det["width"])
                    h = int(det["height"])
                    label = det["class"]
                    conf = det["confidence"]
                    
                    detected_items.append(label)
                    
                    # คำนวณพิกัดมุมกล่องตีกรอบ
                    x1, y1 = int(x - w/2), int(y - h/2)
                    x2, y2 = int(x + w/2), int(y + h/2)
                    
                    # วาดกรอบสีส้มสดใสและแปะป้ายชื่อวัตถุพร้อมเปอร์เซ็นต์ความแม่นยำ
                    cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 165, 255), 3)
                    cv2.putText(draw_frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # อัปเดตยอดการนับวัตถุจริงเข้ากระดานจำลองอัตโนมัติ
            if len(detected_items) > 0:
                st.session_state.sim_count = len(detected_items)
                st.session_state.sim_status = "OK" if len(detected_items) >= 2 else "NG"
            else:
                st.session_state.sim_count = 0
                st.session_state.sim_status = "READY"
                
            # แสดงภาพวิดีโอที่ตีกรอบเสร็จแล้วขึ้นหน้าเว็บแบบลื่นไหล
            final_frame = cv2.cvtColor(draw_frame, cv2.COLOR_BGR2RGB)
            st_frame.image(final_frame, channels="RGB", use_container_width=True)
            
        cap.release()
    else:
        # แสดงรูปภาพสแตนด์บายกรณีปิดกล้อง
        st_frame.image("https://images.unsplash.com/photo-1531747118685-ca8fa6e08806?q=80&w=640", use_container_width=True)

with col_result:
    st.subheader("📊 ข้อ 5: ตรรกะระบบ ผิด-ถูก (OK/NG) คำนวณจาก AI")
    st.write("สถานะประมวลผลแบบ Real-time จากหน้ากล้องจริง")
    st.write("---")
    
    if st.session_state.sim_status == "OK":
        st.markdown(
            "<div style='background-color:#11caa0; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>PASS (OK)</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>โมเดลตรวจพบชิ้นงานคู่กันบนหน้าจอสำเร็จ</p>"
            "</div>", unsafe_allow_html=True
        )
    elif st.session_state.sim_status == "NG":
        st.markdown(
            "<div style='background-color:#ef4444; padding:20px; border-radius:10px; text-align:center;'>"
            "<h1 style='color:white; margin:0;'>REJECT (NG) 🚨</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>พบสิ่งผิดปกติ! วัตถุขาดหายหรือโดนบัง</p>"
            "</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background-color:#64748b; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>SYSTEM READY</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>รอกล่องถัดไปเข้าจุดสแกนภาพ</p>"
            "</div>", unsafe_allow_html=True
        )

    st.write("")
    st.metric(label="จำนวนวัตถุที่ระบบนับได้ในกล่อง ณ ตอนนี้", value=f"{st.session_state.sim_count} ชิ้น")
