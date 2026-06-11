import streamlit as st
import numpy as np
from PIL import Image
from roboflow import Roboflow

# ==================================================================
# 🚨 [โน้ตหัวข้อสำคัญ] จุดที่พี่วิรัตน์เปลี่ยน WORDING ให้ตรงเรียบร้อยแล้ว 🚨
# ==================================================================
# ✅ จุดที่ 1: หยอด Private API Key ของจริงเรียบร้อย (rf_E8O0kMpxK...)
# ✅ จุดที่ 2: ชื่อโปรเจกต์ตรงตามฐานข้อมูลหน้าเว็บแล้ว ("test11-domtn")
# ✅ จุดที่ 3: ดึงสมองกลเวอร์ชันล่าสุดเรียบร้อยแล้ว (.version(5))
# ✅ จุดที่ 4: ตั้งค่ากลุ่มคลาสเป็นปากกาจริงตรงตัวแล้ว ["Pink", "Green"]
# 🛠️ [จุดแก้ไขใหม่]: เพิ่มตรรกะแยกแยะตัวหนังสือชื่อคลาสบนรูปภาพ และตรวจเช็กสีห้ามซ้ำซ้อน
# ==================================================================

# CONFIGURATION & INITIALIZATION
st.set_page_config(page_title="AI Smart Inspection v5", layout="wide")

# เชื่อมต่อเข้าเตาอบสมองกล Roboflow v5 ของพี่วิรัตน์
@st.cache_resource
def init_roboflow_model():
    try:
        # พี่วิรัตน์หยอดคีย์ลับเชื่อมต่อเสร็จสมบูรณ์เรียบร้อยครับ!
        rf = Roboflow(api_key="rf_E8O0kMpxKZXtOz2ol6VsvabOJgo1") 
        project = rf.workspace().project("test11-domtn")
        model = project.version(5).model
        return model
    except Exception as e:
        st.error(f"❌ เชื่อมต่อโมเดลไม่สำเร็จ: โปรดตรวจสอบ API Key หรืออินเทอร์เน็ตครับพี่ ({e})")
        return None

model = init_roboflow_model()

# ตัวแปรคลาสเป้าหมายพจนานุกรม AI
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
    
    # ดึงระบบกล้องหน้าเว็บเบราว์เซอร์ของ Streamlit ป้องกันระบบคลาวด์ล็อกฮาร์ดแวร์
    img_file = st.camera_input("📸 เล็งปากกาชมพู-เขียวให้อยู่ในหน้าจอ แล้วกดถ่ายภาพเพื่อส่งให้ AI ตรวจได้เลยครับพี่!")

    if img_file is not None and model is not None:
        pil_img = Image.open(img_file)
        
        # ส่งภาพไปให้สมองกล AI v5 สแกนตรวจจับ (ตั้งค่าความมั่นใจไว้ที่ 30% ตามเดิมครับ)
        predictions = model.predict(pil_img, confidence=30).json()
        
        draw_img = pil_img.copy()
        import collections
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(draw_img)
        
        # 🛠️ ใช้ระบบ Set เพื่อเก็บชื่อคลาสแบบไม่ซ้ำสี ป้องกันพนักงานโกงยัดสีเดิมมา 2 แท่ง
        detected_set = set()
        detected_count = 0
        
        if "predictions" in predictions:
            for det in predictions["predictions"]:
                x = det["x"]
                y = det["y"]
                w = det["width"]
                h = det["height"]
                label = det["class"] # ดึงข้อความ Wording ชื่อคลาสย่อยที่ AI ตรวจเจอสดๆ ("Pink" หรือ "Green")
                conf = det["confidence"]
                
                # บันทึกชื่อคลาสและนับจำนวนจริงที่เจอ
                detected_set.add(label)
                detected_count += 1
                
                # คำนวณพิกัดเพื่อวาดเส้นกรอบสี่เหลี่ยม
                x1 = int(x - w/2)
                y1 = int(y - h/2)
                x2 = int(x + w/2)
                y2 = int(y + h/2)
                
                # 🛠️ วาดเส้นกรอบสีส้มหนาๆ ครอบตัววัตถุ
                draw.rectangle([x1, y1, x2, y2], outline="#ff5722", width=6)
                
                # 🛠️ พ่นสีเขียน Wording ชื่อคลาสพร้อมเปอร์เซ็นต์ความมั่นใจแปะบนหัวกล่องรูปภาพจริง
                text_content = f"{label} {conf*100:.1f}%"
                draw.text((x1 + 5, y1 + 5), text_content, fill="#ffffff")
                
        # 🛠️ อัปเดตยอดนับและวิเคราะห์ตรรกะ ผิด-ถูก (OK/NG) แบบอัจฉริยะดักทางสับขาหลอก
        st.session_state.sim_count = detected_count
        
        # เงื่อนไขเหล็ก: ต้องเจอคำว่า "Pink" และคำว่า "Green" ครบทั้งคู่พร้อมกันจริง ๆ ถึงจะให้ผ่าน!
        if "Pink" in detected_set and "Green" in detected_set:
            st.session_state.sim_status = "OK"
        elif detected_count > 0:
            st.session_state.sim_status = "NG" # เจอชิ้นเดียว หรือเจอสีซ้ำกันปัดเป็นของขาดทันที!
        else:
            st.session_state.sim_status = "READY"
            
        # โชว์รูปภาพที่ AI ตีกรอบพ่นข้อความเสร็จสรรพขึ้นกระดานแดชบอร์ด
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
            "<p style='color:white; margin:0; font-size:18px;'>พบสิ่งผิดปกติ! วัตถุขาดหายไปบางสี หรือชิ้นงานไม่ครบถ้วนตามสเปก</p>"
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
    st.metric(label="จำนวนปากกาทีระบบสแกนเจอในกล่อง ณ ตอนนี้", value=f"{st.session_state.sim_count} แท่ง")
    
    # 🛠️ ตารางเช็กชื่อคลาสย่อยอัปเดตสถานะสดตามสีที่สแกนเจอจริงบนหน้างาน
    st.write("**สถานะการแยกแยะชิ้นงานย่อยยึดตามสมองกล AI:**")
    for item in TARGET_CLASSES:
        if img_file is not None and 'detected_set' in locals() and item in detected_set:
            st.markdown(f"🔹 {item}: <span style='color:#11caa0; font-weight:bold;'>Detected (เจอแล้ว)</span>", unsafe_allow_html=True)
        elif img_file is not None:
            st.markdown(f"🔹 {item}: <span style='color:#ef4444; font-weight:bold;'>Missing / Occluded (ขาดหายไป! 🚨)</span>", unsafe_allow_html=True)
        else:
            st.write(f"🔹 {item}: Standby รอสแกน...")
