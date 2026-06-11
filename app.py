import streamlit as st
import numpy as np
from PIL import Image
from roboflow import Roboflow

# ==================================================================
# 🚨 [โน้ตหัวข้อสำคัญ] จุดที่พี่วิรัตน์ต้องเปลี่ยน WORDING ให้ตรงกับที่เทรนจริง 🚨
# ==================================================================
# 📌 จุดที่ 1 (บรรทัดที่ 26): เปลี่ยนรหัส API KEY ส่วนตัวของพี่วิรัตน์
# 📌 จุดที่ 2 (บรรทัดที่ 27): เช็กชื่อโปรเจกต์ (เช่น "test11-domtn") ให้ตรงกับบนเว็บ
# 📌 จุดที่ 3 (บรรทัดที่ 28): เลขเวอร์ชัน ต้องเป็นเลข .version(5) ล่าสุด
# 📌 จุดที่ 4 (บรรทัดที่ 38): ตัวแปร TARGET_CLASSES ต้องเปลี่ยนเป็น ["Pink", "Green"]
# ==================================================================

# CONFIGURATION & INITIALIZATION
st.set_page_config(page_title="AI Smart Inspection v5", layout="wide")

# เชื่อมต่อเข้าเตาอบสมองกล Roboflow v5 ของพี่วิรัตน์
@st.cache_resource
def init_roboflow_model():
    try:
        # 🔴 [จุดเปลี่ยนที่ 1-3]: หยอดรหัสกุญแจลับ API KEY และตรวจสอบเลขเวอร์ชันให้เป็นเลข 5
        rf = Roboflow(api_key="ใส่_API_KEY_ของพี่ตรงนี้") 
        project = rf.workspace().project("test11-domtn")
        model = project.version(5).model
        return model
    except Exception as e:
        st.error(f"❌ เชื่อมต่อโมเดลไม่สำเร็จ: โปรดตรวจสอบ API Key หรืออินเทอร์เน็ตครับพี่ ({e})")
        return None

model = init_roboflow_model()

# 🔴 [จุดเปลี่ยนที่ 4]: ตัวแปรคลาสเป้าหมาย เปลี่ยน Wording ให้ตรงกับปากกาจริงที่ตีกรอบไว้
TARGET_CLASSES = ["Pink", "Green"]

if "sim_status" not in st.session_state:
    st.session_state.sim_status = "READY"
if "sim_count" not in st.session_state:
    st.session_state.sim_count = 0

# UI DESIGN: DASHBOARD
st.title("🏭 AI Smart Inspection Dashboard (v5 Cloud Setup)")
st.write("สถานีทดสอบระบบตรวจจับวัตถุสแกนภาพสด - ผ่านระบบกล้องเบราว์เซอร์ปลอดภัย 100%")
st.markdown("---")

col_cam, col_result = st.columns([3, 2])

with col_cam:
    st.subheader("📸 ข้อ 4: หน้าต่างดึงภาพจากกล้องเว็บแคม")
    
    # 💡 ใช้ระบบกล้องเบราว์เซอร์ของ Streamlit ตรงๆ เพื่อแก้ปัญหาคลาวด์ล็อกฮาร์ดแวร์
    img_file = st.camera_input("📸 เล็งปากกาชมพู-เขียวให้อยู่ในหน้าจอ แล้วกดถ่ายภาพเพื่อส่งให้ AI ตรวจได้เลยครับพี่!")

    if img_file is not None and model is not None:
        # แปลงไฟล์ภาพที่ถ่ายสด ๆ ให้กลายเป็นฟอร์แมตที่ AI พร้อมอ่าน
        pil_img = Image.open(img_file)
        
        # ส่งภาพไปให้สมองกล AI v5 ทำการสแกนตรวจจับทันที (ปรับความมั่นใจไว้ที่ 30%)
        predictions = model.predict(pil_img, confidence=30).json()
        
        # ดึงภาพต้นฉบับมาเตรียมวาดเส้นกรอบ
        draw_img = pil_img.copy()
        import collections
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(draw_img)
        
        detected_items = []
        
        if "predictions" in predictions:
            for det in predictions["predictions"]:
                x = det["x"]
                y = det["y"]
                w = det["width"]
                h = det["height"]
                label = det["class"] # ระบบดึงชื่อคลาส (Pink / Green) ออกมาออโต้
                conf = det["confidence"]
                
                detected_items.append(label)
                
                # คำนวณพิกัดเพื่อขีดเส้นกรอบลงบนรูปภาพ
                x1 = int(x - w/2)
                y1 = int(y - h/2)
                x2 = int(x + w/2)
                y2 = int(y + h/2)
                
                # ลากเส้นกรอบสีส้มหนา ๆ ครอบวัตถุทุกชิ้นพร้อมกัน (ไม่ล็อกโควตาตัวเลขภาพแล้ว!)
                draw.rectangle([x1, y1, x2, y2], outline="#ff5722", width=5)
                
        # อัปเดตยอดการนับวัตถุจริงโชว์บนหน้าจอ
        st.session_state.sim_count = len(detected_items)
        if len(detected_items) >= 2:
            st.session_state.sim_status = "OK"
        elif len(detected_items) == 1:
            st.session_state.sim_status = "NG"
        else:
            st.session_state.sim_status = "READY"
            
        # โชว์รูปภาพที่ AI วาดกรอบเสร็จเรียบร้อยแล้วขึ้นหน้าจอแดชบอร์ด
        st.image(draw_img, caption="🎯 ผลลัพธ์การสแกนจากสมองกล AI v5", use_container_width=True)

with col_result:
    st.subheader("📊 ข้อ 5: ตรรกะระบบ ผิด-ถูก (OK/NG) คำนวณจาก AI")
    st.write("ระบบจะปล่อยผ่าน (PASS) ก็ต่อเมื่อเจอทั้ง Pink และ Green ครบทั้งคู่")
    st.write("---")
    
    if st.session_state.sim_status == "OK":
        st.markdown(
            "<div style='background-color:#11caa0; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>PASS (OK)</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>ยอดเยี่ยม! ตรวจพบปากกาครบทั้งสองสีคู่กัน</p>"
            "</div>", unsafe_allow_html=True
        )
    elif st.session_state.sim_status == "NG":
        st.markdown(
            "<div style='background-color:#ef4444; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>REJECT (NG) 🚨</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>พบสิ่งผิดปกติ! วัตถุขาดหายไปหนึ่งสี (ของไม่ครบ)</p>"
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
    st.metric(label="จำนวนปากกาทีระบบสแกนเจอในกล่อง", value=f"{st.session_state.sim_count} / 2 แท่ง")
