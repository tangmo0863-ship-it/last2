# TEAM_ROLES.md — บทบาทหน้าที่ทีม 11 คน (v16)

จุดเริ่มต้นเดียวที่ทุกคนควรอ่านก่อนเริ่มงาน: ใครรับผิดชอบอะไร ต้องอ่านอะไร ส่งงานให้ใคร

---

## 0. แผนที่เอกสาร

| อยากรู้เรื่อง | เปิด |
|---|---|
| บทบาท/การส่งต่องาน | **ไฟล์นี้** |
| โครงสร้างไฟล์, วิธีรัน, หลักการคำนวณ, ข้อจำกัด | `README.md` |
| ที่มาของทุกตัวเลข/พารามิเตอร์ + สถานะหลักฐาน + แหล่งอ้างอิง | เอกสาร "ที่มาของตัวเลขและพารามิเตอร์" + ไฟล์ Word "สรุปแหล่งอ้างอิง" |
| สูตรปัจจุบันและประวัติการแก้ | Data Contract + CHANGELOG หัวไฟล์ `calculate_modules/<โมดูล>.py` |
| คำอธิบายกราฟที่ผู้ใช้เห็น | `chart_notes.py` |
| เคสขอบที่ต้องทดสอบ | `EDGE_CASES.md` |
| Git / PR / ลำดับ merge / `CALC_VERSION` | `GIT_WORKFLOW.md` |
| ตรวจว่างานพังไหม | `python rebuild_database.py` แล้ว `python run_tests.py` |
| ดูหน้าตัวเองแบบเดี่ยว | `streamlit run preview_my_page.py` |

`DATA_FORMULA_AUDIT.md` เลิกใช้แล้ว (ไม่ตรงกับโค้ด v16)

---

## 1. ภาพรวมทีม

| # | บทบาท | ไฟล์หลัก | ส่งงานให้ |
|---|---|---|---|
| 1-6 | เจ้าของโมดูล | `pages_content/<โมดูล>.py` + `calculate_modules/<โมดูล>.py` + ข้อความกราฟตัวเองใน `chart_notes.py` | 8/9 (สูตร), 10 (Layout) |
| 7 | Overview Owner | `pages_content/overview.py` | 10, 11 |
| 8 | Auditor กลุ่มการเงิน | ตรวจ Company Health, Fair Value, Entry Timing · สคริปต์ `backtest_signals.py` | 1-3, 11 |
| 9 | Auditor กลุ่มควอนต์ | ตรวจ AI, Risk, Industry · สคริปต์ `model_comparison.py`, `tune_ai.py`, `sensitivity_analysis.py` | 4-6, 11 |
| 10 | Layout/Design Lead | `common.py` (หน้าจอ: CSS, responsive), โครงสร้าง `chart_notes.py` | 1-7, 11 |
| 11 | Integration/QA Lead | `app.py`, `calculate_scores.py` (`CALC_VERSION`), `import_data.py`, `Dataset/`, `fetch_price_history.py`, `compute_beta.py`, `rebuild_database.py`, `run_tests.py`, เอกสาร, deploy | — |

```
คนที่ 1-6 ──┬──► คนที่ 8/9 (สูตร/ตัวเลข) ──┐
            └──► คนที่ 10 (Layout) ─────────┤
คนที่ 7 ───────► คนที่ 10 (Layout) ─────────┴──► คนที่ 11 (merge + CALC_VERSION + rebuild + deploy)
```

---

## 2. บทบาทที่ 1-6: เจ้าของโมดูล

| โมดูล | สี | อ้างอิงหลัก |
|---|---|---|
| 💚 Company Health | `#10B981` | Nissim & Penman (2001), Soliman (2008) |
| ⚖️ Fair Value | `#F59E0B` | Damodaran (2012), Graham (1973), Dechow et al. (1999) |
| ⏱️ Entry Timing | `#38BDF8` | Wilder (1978), Appel (2005), Elder (1993), Timmermann (2006) |
| 🔮 AI Prediction | `#A855F7` | López de Prado (2018), Breiman (2001) |
| 🛡️ Risk Analysis | `#FB923C` | Jorion (2007), Daves et al. (2000), Ang et al. (2006) |
| 📊 Industry Benchmark | `#2DD4BF` | Nissim & Penman (2001), Yeh & Liu (2020) |

**ความรับผิดชอบ:** สูตร (`calculate_modules/`), หน้าจอ (`pages_content/`), ข้อความใต้กราฟของตัวเอง (`chart_notes.py`), ที่มาของพารามิเตอร์โมดูลตัวเองในเอกสารพารามิเตอร์

**ต้องอ่านก่อนเริ่ม:** Data Contract + CHANGELOG หัวไฟล์โมดูลตัวเอง · `EDGE_CASES.md` หัวข้อโมดูลตัวเอง · แถวของโมดูลตัวเองในเอกสารพารามิเตอร์

**กติกาหลัก:**
- ข้อมูลไม่พอ → คืน `None` แสดง N/A พร้อมเหตุผล **ห้ามใส่ค่าสมมติ**
- ห้ามบีบคะแนนเพื่อความสวยงาม
- ค่าที่ทีมกำหนดเองต้องมีเหตุผลหรือแหล่งอ้างอิงในเอกสารพารามิเตอร์

**Definition of Done:**
- [ ] `preview_my_page.py` ผ่าน 8 หุ้น (เน้น HANA, JMART, TRUE, DELTA, THCOM)
- [ ] Data Contract ครบ · CHANGELOG อัปเดต
- [ ] `chart_notes.py` ตรงกับสูตรใหม่
- [ ] แจ้งคนที่ 11 ว่าต้องเปลี่ยน `CALC_VERSION`

---

## 3. บทบาทที่ 7: Overview Owner

ไฟล์: `pages_content/overview.py` — ไม่มีสูตรของตัวเอง ดึงผลจาก `cis_summary_scores`
- Overall Score = 5 โมดูล (Health 25 · Valuation 25 · Timing 15 · AI 10 · Risk 15) — Industry ไม่นับซ้ำ
- AI ที่ NO EDGE ต้องแสดง N/A สีเทา ไม่ใช่คะแนนกลาง

**DoD:** preview ผ่าน 8 หุ้น · การ์ด 6 โมดูลตรงกับตัวเลขใน DB · แสดงผลบนมือถือได้

---

## 4. บทบาทที่ 8: Auditor กลุ่มการเงิน

ตรวจ: `company_health.py`, `fair_value.py`, `entry_timing.py` (ทั้งสูตรและหน้าจอคู่กัน)

**วิธีตรวจ:**
1. คำนวณมือ 2-3 หุ้นจาก `Dataset/master_all_8_stocks_financials.csv` เทียบ Dashboard (ROE/ROA ต้องคำนวณจากงบ ไม่ใช่คอลัมน์ในไฟล์)
2. ตรวจหุ้นขาดทุน (HANA, JMART) และธงเตือน FCF (TRUE, JMART)
3. ตรวจการ์ด Market Expectation: Ke = 1.66% + Beta(Blume) × 6.30%
4. รัน `backtest_signals.py` เมื่อเกณฑ์ Entry Timing เปลี่ยน แล้วอัปเดตผลในเล่ม

**DoD:** มือเทียบตรง ≥ 2 หุ้น/โมดูล · Data Contract ครบ · เคสใน `EDGE_CASES.md` ยังผ่าน

---

## 5. บทบาทที่ 9: Auditor กลุ่มควอนต์

ตรวจ: `ai_prediction.py`, `risk_analysis.py`, `industry_benchmark.py`

**วิธีตรวจ:**
1. AI: ฝึก 2015-2024 / ทดสอบ 2025, `n_purged = 10` ทุกหุ้น, ไม่ชนะ Baseline ต้องเป็น NO EDGE
2. Risk: ใช้ 3 ปีล่าสุด (`risk_window`), Rf 1.66%, Beta มาจาก `compute_beta.py` (`beta_verified = True`)
3. Industry: กลุ่ม < 2 หุ้นต้องเทียบทั้ง 8 หุ้น, Overall ไม่รวม Industry Score
4. รัน `model_comparison.py`, `tune_ai.py`, `sensitivity_analysis.py` เมื่อโมเดล/น้ำหนักเปลี่ยน

**DoD:** เหมือนคนที่ 8 + `roc_auc` ไม่เป็น 0.5 เป๊ะทุกตัว + ไม่มีคำว่า "อันดับ 1" ให้หุ้นที่คะแนนจริงแย่

---

## 6. บทบาทที่ 10: Layout/Design Lead

ไฟล์: `common.py` (หน้าจอ), โครงสร้าง `chart_notes.py` + ตรวจ Layout ทุก PR

**ความรับผิดชอบ:**
- สี/ฟอนต์/ระยะห่างสม่ำเสมอ หัวข้อหน้าใช้ `class="module-title"` 26px ทุกหน้า
- CSS รองรับมือถือ/iPad (ใช้ selector ทั้ง `column` และ `stColumn`)
- กราฟใหม่ใช้ `show_chart(fig, key)` (คำอธิบายใต้กราฟขึ้นอัตโนมัติถ้ามี key ใน `chart_notes.py`)

**DoD:**
- [ ] ทดสอบบนจอคอม + iPad + มือถือ
- [ ] ไม่มีตัวเลขสมมติ (50, 0.00, Bearish ปลอม) บนหน้าจอ
- [ ] ทุกกราฟมีแถบ ⓘ
- [ ] แก้ `common.py` แล้วรัน `run_tests.py` ทั้งระบบ

---

## 7. บทบาทที่ 11: Integration/QA Lead

**ความรับผิดชอบ:** merge ตามลำดับ (`GIT_WORKFLOW.md` ข้อ 5) · ดูแล `CALC_VERSION` · อัปเดตข้อมูล (`fetch_price_history.py` → `compute_beta.py`) · deploy · อัปเดตเอกสาร · ตัดสินเมื่อความเห็นขัดแย้ง

**Checklist ก่อน Deploy:**
- [ ] เปลี่ยน `CALC_VERSION` ถ้ามีการแก้ `calculate_modules/` หรือ `Dataset/`
- [ ] `python rebuild_database.py` ผ่าน 6 ข้อ
- [ ] `python run_tests.py` ผ่าน
- [ ] ไล่ดูด้วยตา HANA, JMART, TRUE, DELTA บนคอมและ iPad
- [ ] push `Dataset/` และ `cis_database.db` ครบ (เช็คหน้า repo)
- [ ] ไฟล์ชื่อซ้ำอยู่ถูกโฟลเดอร์ ไม่มีไฟล์ `xxx (1).py`

---

## 8. คำถามที่พบบ่อย

**Q: แก้สูตรแล้วเว็บไม่เปลี่ยน?**
A: ยังไม่ได้เปลี่ยน `CALC_VERSION` หรือยังไม่ได้ Reboot app

**Q: หุ้นขึ้น N/A / NO EDGE เยอะ ผิดไหม?**
A: ไม่ผิด เป็นการออกแบบให้ไม่แสดงตัวเลขที่ไม่มีหลักฐาน ดูเหตุผลใน `EDGE_CASES.md`

**Q: Auditor กับเจ้าของโมดูลเห็นไม่ตรงกัน?**
A: คุยใน PR ก่อน ไม่จบให้คนที่ 11 ตัดสิน โดยดูเอกสารพารามิเตอร์และแหล่งอ้างอิงประกอบ

**Q: เพิ่มค่าคงที่ใหม่ในสูตรต้องทำอะไร?**
A: เพิ่มแถวในเอกสารพารามิเตอร์ (ค่า, ตำแหน่งในโค้ด, ที่มา/เหตุผล, สถานะหลักฐาน) ก่อน merge
