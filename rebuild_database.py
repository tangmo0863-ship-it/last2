"""
rebuild_database.py — คำนวณฐานข้อมูลใหม่ทั้งหมดด้วยสูตรล่าสุด + ตรวจว่าได้ตัวเลขใหม่จริง
====================================================================================
วิธีใช้ (รันที่โฟลเดอร์หลักของโปรเจกต์ ที่เดียวกับ app.py):

    python rebuild_database.py

สคริปต์นี้ทำ 5 อย่างตามลำดับ:
    1. ตรวจว่าไฟล์ใน calculate_modules/ ตั้งชื่อถูก (ไฟล์ชื่อ "risk_analysis (4).py" Python จะไม่ใช้)
    2. ลบไฟล์ขยะที่ทำให้สับสน: __pycache__/, _run_tests_preview_tmp.py
    3. สำรอง cis_database.db เดิมเป็น cis_database_backup.db แล้วลบตัวเดิมทิ้ง
    4. รัน import_data + calculate_scores ใหม่ทั้งหมด
    5. ตรวจผลลัพธ์ว่าเป็นตัวเลขชุดใหม่จริง (PASS/FAIL)

หลังรันผ่าน: ปิด streamlit ที่เปิดค้างไว้ แล้วเปิดใหม่ (streamlit run app.py)
และ commit ไฟล์ cis_database.db ขึ้น GitHub ด้วย
"""

import glob
import os
import re
import shutil
import sqlite3
import sys

DB = "cis_database.db"
BACKUP = "cis_database_backup.db"
REQUIRED_MODULES = ["common", "company_health", "fair_value", "entry_timing",
                    "ai_prediction", "risk_analysis", "industry_benchmark"]

ok_all = True


def check(label, cond, hint=""):
    global ok_all
    print(("  ✅ " if cond else "  ❌ ") + label + ("" if cond or not hint else f"\n       → {hint}"))
    ok_all = ok_all and bool(cond)


print("\n[1/5] ตรวจไฟล์ใน calculate_modules/")
for name in REQUIRED_MODULES:
    check(f"calculate_modules/{name}.py", os.path.exists(f"calculate_modules/{name}.py"),
          "ไม่พบไฟล์นี้ — ต้องมีชื่อตรงเป๊ะ")
stray = [f for f in glob.glob("calculate_modules/*.py")
         if re.search(r"\(\d+\)|__\d+_|copy|สำเนา", os.path.basename(f), re.I)]
check("ไม่มีไฟล์ชื่อซ้ำ/สำเนา เช่น 'risk_analysis (4).py'", not stray,
      f"พบ {stray} — ให้ลบไฟล์เก่าที่ชื่อถูกต้องทิ้ง แล้วเปลี่ยนชื่อไฟล์ใหม่เป็นชื่อมาตรฐาน")
try:
    src = open("calculate_modules/fair_value.py", encoding="utf-8").read()
    check("fair_value.py เป็นเวอร์ชันใหม่ (มี FIX-F1)", "FIX-F1" in src, "ยังเป็นไฟล์เก่า ให้วางไฟล์ใหม่ทับ")
    src = open("calculate_modules/ai_prediction.py", encoding="utf-8").read()
    check("ai_prediction.py เป็นเวอร์ชันใหม่ (มี FIX-A2)", "FIX-A2" in src, "ยังเป็นไฟล์เก่า ให้วางไฟล์ใหม่ทับ")
    src = open("calculate_scores.py", encoding="utf-8").read()
    check("calculate_scores.py เป็นเวอร์ชันใหม่ (มี CALC_VERSION)", "CALC_VERSION" in src,
          "ยังเป็นไฟล์เก่า ให้วางไฟล์ใหม่ทับ")
except FileNotFoundError as e:
    check(str(e), False)
if not ok_all:
    print("\n⛔ แก้ไฟล์ตามข้างบนก่อน แล้วรันใหม่อีกครั้ง")
    sys.exit(1)

print("\n[2/5] ลบไฟล์ขยะ")
for d in glob.glob("**/__pycache__", recursive=True):
    shutil.rmtree(d, ignore_errors=True)
    print(f"  🗑  {d}/")
for f in ["_run_tests_preview_tmp.py"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"  🗑  {f}")

print("\n[3/5] สำรองและลบฐานข้อมูลเดิม")
if os.path.exists(DB):
    shutil.copy2(DB, BACKUP)
    os.remove(DB)
    print(f"  💾 สำรองไว้ที่ {BACKUP} แล้วลบ {DB} เดิม")
else:
    print("  (ไม่มีฐานข้อมูลเดิม)")

print("\n[4/5] คำนวณใหม่ทั้งหมด")
import import_data          # noqa: E402
import calculate_scores     # noqa: E402
from sqlalchemy import create_engine  # noqa: E402

engine = create_engine(f"sqlite:///{DB}")
import_data.import_financial_data(engine)
import_data.import_price_data(engine)
import_data.import_risk_metrics(engine)
calculate_scores.run_full_pipeline()

print("\n[5/5] ตรวจว่าได้ตัวเลขชุดใหม่จริง")
con = sqlite3.connect(DB)
cols = [r[1] for r in con.execute("PRAGMA table_info(cis_summary_scores)")]
rows = {r[0]: dict(zip(cols, r)) for r in con.execute("SELECT * FROM cis_summary_scores")}
con.close()
g = lambda t, k: rows.get(t, {}).get(k)

check(f"calc_version = {calculate_scores.CALC_VERSION}", g("DELTA", "calc_version") == calculate_scores.CALC_VERSION)
check("มีคอลัมน์ใหม่ครบ (n_purged, net_debt_used, ratio_mismatch, volatility_static)",
      all(c in cols for c in ["n_purged", "net_debt_used", "ratio_mismatch", "volatility_static"]))
fv = g("DELTA", "fair_value")
check(f"DELTA fair value ไม่ใช่ 112.45 แบบเก่า (ได้ {fv})", fv is not None and abs(fv - 112.45) > 1)
roe = g("HANA", "roe")
check(f"HANA ROE ติดลบตามผลขาดทุนจริง (ได้ {roe})", roe is not None and roe < 0)
gr = g("TRUE", "net_income_growth_yoy")
check(f"TRUE กำไรโต +% (พลิกจากขาดทุนเป็นกำไร) (ได้ {gr})", gr is not None and gr > 0)
check("AI ตัดรอยต่อ train/test 10 แถวทุกหุ้น",
      all(g(t, "n_purged") == 10 for t in rows))

print("\n" + "=" * 70)
if ok_all:
    print("✅ เสร็จสมบูรณ์ — ฐานข้อมูลเป็นตัวเลขชุดใหม่แล้ว")
    print("   ต่อไป: 1) ปิด streamlit ที่เปิดค้างไว้ แล้วรัน  streamlit run app.py  ใหม่")
    print("          2) git add cis_database.db calculate_scores.py common.py calculate_modules/")
    print("             git commit -m \"recalculate with fixed formulas\" && git push")
    print(f"          3) ถ้าทุกอย่างโอเค ลบ {BACKUP} ทิ้งได้ (อย่า commit ไฟล์ backup ขึ้น GitHub)")
else:
    print("❌ มีบางข้อไม่ผ่าน — ดูรายการ ❌ ด้านบน")
    sys.exit(1)
