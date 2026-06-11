import streamlit as st
import numpy as np
from PIL import Image
from roboflow import Roboflow

# ==================================================================
# 🔴 [โน้ตหัวข้อสำคัญ] จุดที่เปลี่ยน WORDING ให้ตรงกับการเทรนจริง 🔴
# ==================================================================
# ✅ จุดที่ 1: หยอด Private API Key ของจริงเรียบร้อย (rf_E8O0kMpxK...)
# ✅ จุดที่ 2: ชื่อโปรเจกต์ตรงตามคลังฐานข้อมูลแล้ว ("test11-domtn")
# ✅ จุดที่ 3: ดึงสมองกลเวอร์ชันล่าสุดเรียบร้อยแล้ว (.version(5))
# ✅ จุดที่ 4: ตั้งค่ากลุ่มคลาสเป้าหมายเป็นปากกาจริงแล้ว ["Pink", "Green"]
# 🛠️ [ตรรกะใหม่]: ปรับ Wording การตรวจเช็กสีห้ามซ้ำซ้อน ดักทางพนักงานโกงยัดสีเดิมมา 2 แท่ง
# ==================================================================

# CONFIGURATION & INITIALIZATION
st.set_page_config(page_title="AI Smart Inspection v5", layout="wide")

# เชื่อมต่อเข้าเตาอบสมองกล Roboflow v5 ของพี่วิรัตน์
@st.cache_resource
def init_roboflow_model():
    try:
        # 🔴 [จุดเปลี่ยนที่ 1-3]: หยอดรหัสกุญแจลับ และเลขเวอร์ชัน 5 ตัวล่าสุดเรียบร้อยแล้ว
        rf = Roboflow(api_key="rf_E8O0kMpxKZXtOz2ol6VsvabOJgo1") 
        project = rf.workspace().project("test11-domtn")
        model = project.version(5).model
        return model
    except Exception as e:
        st.error(f"❌ เชื่อมต่อโมเดลไม่สำเร็จ: โปรดตรวจสอบ API Key หรืออินเทอร์เน็ตครับพี่ ({e})")
        return None

model = init_roboflow_model()

# 🔴 [จุดเปลี่ยนที่ 4]: ตัวแปรกลุ่มคลาสเป้าหมาย เปลี่ยน Wording ให้แมตช์กับปากกาจริงเป๊ะๆ
# คำว่า "Pink" และ "Green" ต้องสะกดตัวใหญ่ตัวเล็กตามคลังตีกรอบบนเว็บห้ามเพี้ยนเด็ดขาด!
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
    
    # 💡 ปรับมาใช้กล้องถ่ายภาพผ่านเบราว์เซอร์แทน cv2.VideoCapture เพื่อทะลวงบล็อกระบบรักษาความปลอดภัยของคลาวด์
    img_file = st.camera_input("📸 เล็งปากกาชมพู-เขียวให้อยู่ในหน้าจอ แล้วกดถ่ายภาพเพื่อส่งให้ AI ตรวจได้เลยครับพี่!")

    if img_file is not None and model is not None:
        pil_img = Image.open(img_file)
        
        # ส่งภาพไปให้สมองกล AI v5 สแกนตรวจจับ (ตั้งค่าความมั่นใจไว้ที่ 30%)
        predictions = model.predict(pil_img, confidence=30).json()
        
        draw_img = pil_img.copy()
        import collections
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(draw_img)
        
        # 🛠️ ใช้ระบบ Set เพื่อล็อกชื่อคลาสแบบไม่ซ้ำสี ป้องกันพนักงานยัดชมพูมา 2 แท่งแล้วระบบเอ๋อให้ผ่าน
        detected_set = set()
        detected_count = 0
        
        if "predictions" in predictions:
            for det in predictions["predictions"]:
                x = det["x"]
                y = det["y"]
                w = det["width"]
                h = det["height"]
                label = det["class"] # 🔴 ระบบดึง Wording ชื่อคลาสที่ AI พ่นออกมาออโต้ ("Pink" หรือ "Green")
                conf = det["confidence"]
                
                detected_set.add(label)
                detected_count += 1
                
                # คำนวณพิกัดเพื่อขีดเส้นกรอบสี่เหลี่ยมลงบนรูปภาพ
                x1 = int(x - w/2)
                y1 = int(y - h/2)
                x2 = int(x + w/2)
                y2 = int(y + h/2)
                
                # วาดเส้นกรอบหนา ๆ ครอบวัตถุทุกชิ้นพร้อมกัน (ไม่จำกัดโควตาชิ้นงานแล้ว)
                draw.rectangle([x1, y1, x2, y2], outline="#ff5722", width=6)
                
                # พ่นข้อความ Wording ชื่อสีพร้อมเปอร์เซ็นต์ความแม่นยำแปะบนตัวกล่องชิ้นงาน
                text_content = f"{label} {conf*100:.1f}%"
                draw.text((x1 + 5, y1 + 5), text_content, fill="#ffffff")
                
        # อัปเดตยอดการนับวัตถุจริงโชว์บนหน้าจอ
        st.session_state.sim_count = detected_count
        
        # 🛠️ ปรับตรรกะเหล็ก: ต้องตรวจเจอคำว่า "Pink" และคำว่า "Green" พร้อมกันคู่กันจริง ๆ ถึงจะขึ้น PASS
        if "Pink" in detected_set and "Green" in detected_set:
            st.session_state.sim_status = "OK"
        elif detected_count > 0:
            st.session_state.sim_status = "NG" # เจอชิ้นเดียว หรือเจอสีซ้ำกัน ปรับเป็นของขาดทันที!
        else:
            st.session_state.sim_status = "READY"
            
        # แสดงรูปภาพที่ AI ตีกรอบพ่นข้อความเสร็จเรียบร้อยแล้วขึ้นหน้าจอแดชบอร์ด
        st.image(draw_img, caption="🎯 ผลลัพธ์การสแกนตรวจจับจากสมองกล AI v5", use_container_width=True)

with col_result:
    st.subheader("📊 ข้อ 5: ตรรกะระบบ ผิด-ถูก (OK/NG) คำนวณจาก AI")
    st.write("ระบบจะปล่อยผ่าน (PASS) ก็ต่อเมื่อเจอทั้ง Pink และ Green ครบทั้งคู่")
    st.write("---")
    
    if st.session_state.sim_status == "OK":
        st.markdown(
            "<div style='background-color:#11caa0; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>PASS (OK)</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>ยอดเยี่ยม! ตรวจพบปากกาครบทั้งสองสีคู่กันอย่างถูกต้อง</p>"
            "</div>", unsafe_allow_html=True
        )
    elif st.session_state.sim_status == "NG":
        st.markdown(
            "<div style='background-color:#ef4444; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>REJECT (NG) 🚨</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>พบสิ่งผิดปกติ! วัตถุขาดหายไปบางสี หรือชิ้นงานไม่ครบถ้วนตาม Standard</p>"
            "</div>", unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background-color:#64748b; padding:20px; border-radius:10px; text-align:center;'> "
            "<h1 style='color:white; margin:0;'>SYSTEM READY</h1>"
            "<p style='color:white; margin:0; font-size:18px;'>รอกล่องถัดไปเข้าจุดถ่ายภาพสแกนชิ้นงาน</p>"
            "</div>", unsafe_allow_html=True
        )

    st.write("")
    st.metric(label="... จำนวนปากกาทีระบบสแกนเจอในกล่อง ณ ตอนนี้ ...", value=f"{st.session_state.sim_count} แท่ง")
    
    # แสดงสถานะแยกแยะอัปเดตสดตามจริงอ้างอิงจากรายชื่อ Set
    st.write("**สถานะการแยกแยะชิ้นงานย่อยยึดตามสมองกล AI:**")
    for item in TARGET_CLASSES:
        if img_file is not None and 'detected_set' in locals() and item in detected_set:
            st.markdown(f"🔹 {item}: <span style='color:#11caa0; font-weight:bold;'>Detected (เจอแล้ว)</span>", unsafe_allow_html=True)
        elif img_file is not None:
            st.markdown(f"🔹 {item}: <span style='color:#ef4444; font-weight:bold;'>Missing / Occluded (ขาดหายไป! 🚨)</span>", unsafe_allow_html=True)
        else:
            st.write(f"🔹 {item}: Standby รอสแกน...")
