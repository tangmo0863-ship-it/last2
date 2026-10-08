# คู่มือ Git Workflow — ทีม 11 คน (v16)

วิธีใช้ Git ร่วมกันให้แก้โค้ดพร้อมกันได้โดยไม่ทับกัน อ่านคู่กับ `TEAM_ROLES.md` (ใครทำอะไร) และ `README.md` (โครงสร้างไฟล์)

---

## 1. Branch

```
main                              ← โค้ดที่ deploy จริง ห้าม push ตรง
├── feature/company-health        ← คนที่ 1
├── feature/fair-value            ← คนที่ 2
├── feature/entry-timing          ← คนที่ 3
├── feature/ai-prediction         ← คนที่ 4
├── feature/risk-analysis         ← คนที่ 5
├── feature/industry-benchmark    ← คนที่ 6
├── feature/overview              ← คนที่ 7
├── feature/layout                ← คนที่ 10 (common.py หน้าจอ, CSS, chart_notes.py)
└── data/<เรื่อง>                  ← คนที่ 11 เมื่ออัปเดตข้อมูล เช่น data/price-2026
```

- **คนที่ 8, 9 (Auditor):** ไม่มี feature branch งานหลักคือรีวิว PR ถ้าแก้บั๊กเอง ใช้ `fix/<คำอธิบาย>`
- **คนที่ 11 (Integration):** ทำงานบน `main` + branch `data/...` ตอนอัปเดตข้อมูล

```bash
git clone <repo-url>
cd cis-dashboard
git checkout -b feature/company-health   # เปลี่ยนตามโมดูลตัวเอง
```

---

## 2. ใครแก้ไฟล์ไหนได้

| ไฟล์ | ใครแก้ | หมายเหตุ |
|---|---|---|
| `pages_content/<โมดูล>.py` | เจ้าของโมดูล (1-6), Overview (7) | |
| `calculate_modules/<โมดูล>.py` | เจ้าของโมดูล (1-6) | ห้ามลบ/เปลี่ยนชื่อ key ใน Data Contract · บันทึก CHANGELOG หัวไฟล์ |
| `calculate_modules/common.py` | แจ้งทีมก่อน | `SECTOR_MAP`, `clean_float`, `RISK_FREE_RATE` กระทบทุกโมดูล |
| `common.py` (หน้าจอ) | คนที่ 10 | CSS/responsive, `show_chart`, `render_chart_note` กระทบทุกหน้า |
| `chart_notes.py` | คนที่ 10 (โครงสร้าง) + เจ้าของโมดูล (ข้อความกราฟตัวเอง) | แก้สูตรแล้วต้องแก้คำอธิบายกราฟให้ตรง |
| `calculate_scores.py`, `import_data.py`, `app.py` | คนที่ 11 | **`CALC_VERSION` อยู่ในไฟล์นี้** |
| `Dataset/*.csv`, `fetch_price_history.py`, `compute_beta.py`, `rebuild_database.py` | คนที่ 11 | อัปเดตข้อมูลแล้วแจ้งทุกคน pull + rebuild |
| `model_comparison.py`, `sensitivity_analysis.py`, `backtest_signals.py`, `tune_ai.py` | คนที่ 8/9 | สคริปต์หลักฐาน ไม่กระทบแอป |
| `run_tests.py`, `README.md`, `GIT_WORKFLOW.md`, `TEAM_ROLES.md`, `EDGE_CASES.md` | คนที่ 11 (8/9 เพิ่มเคสใน EDGE_CASES ได้) | |

**กฎทอง:** ไม่ใช่ไฟล์ของตัวเอง → เปิด PR เสมอ ห้าม push ตรงเข้า `main`

---

## 3. Workflow รายวัน

```bash
git checkout main && git pull origin main
git checkout feature/company-health
git merge main                       # เอาโค้ดล่าสุดมารวมก่อนเริ่มงาน

streamlit run preview_my_page.py     # ทดสอบหน้าตัวเอง ครบ 8 หุ้น
# แก้สูตรแล้ว → กดปุ่ม "🔄 คำนวณคะแนนใหม่" ในหน้า preview

git add pages_content/company_health.py calculate_modules/company_health.py
git commit -m "company_health: <เปลี่ยนอะไร ทำไม>"
git push origin feature/company-health
```

---

## 4. เปิด Pull Request

**Checklist ก่อนเปิด PR:**
- [ ] `preview_my_page.py` ผ่านครบ 8 หุ้น (โดยเฉพาะ HANA, JMART, TRUE, DELTA, THCOM)
- [ ] Data Contract ยังคืน key ครบ
- [ ] ข้อมูลไม่พอ → คืน `None` ไม่ใช่ค่าสมมติ · หน้าจอใช้ `safe()` / `fmt_ratio()`
- [ ] แก้สูตร → บันทึก CHANGELOG หัวไฟล์ + แก้ข้อความใน `chart_notes.py` ถ้ากราฟเปลี่ยน
- [ ] แก้สูตร → **แจ้งคนที่ 11 ให้เปลี่ยน `CALC_VERSION`** ตอน merge
- [ ] ค่าใหม่ที่ทีมกำหนดเอง → เพิ่มในเอกสาร "ที่มาของตัวเลขและพารามิเตอร์" พร้อมเหตุผล/แหล่งอ้างอิง
- [ ] `git diff main --stat` มีแต่ไฟล์ของตัวเอง

**หัวข้อ PR:** `[Fair Value] เพิ่ม X, แก้ Y`

| PR จากโมดูล | Formula Auditor | Layout |
|---|---|---|
| Company Health, Fair Value, Entry Timing | คนที่ 8 | คนที่ 10 |
| AI Prediction, Risk Analysis, Industry Benchmark | คนที่ 9 | คนที่ 10 |
| Overview | — | คนที่ 10 |

Merge ได้เมื่อ Approve ครบทั้ง Auditor + Layout

---

## 5. ลำดับการ Merge

```
1. company-health → 2. fair-value → 3. entry-timing → 4. ai-prediction → 5. risk-analysis
6. industry-benchmark   (ต้องมีผล 5 โมดูลก่อน)
7. overview             (ต้องมีคะแนนครบทุกโมดูล)
8. layout               (ถ้ามีแก้ common.py / chart_notes.py)
```

---

## 6. ขั้นตอนรวมทีม (คนที่ 11)

```bash
git checkout main && git pull origin main
git merge feature/company-health --no-ff
python rebuild_database.py        # คำนวณใหม่ + ตรวจผล 6 ข้อ
python run_tests.py               # หน้าจอ 7 หน้า × 8 หุ้น
# ผ่าน → merge branch ถัดไป ทำซ้ำตามลำดับข้อ 5
```

**หลัง merge ครบ:**
1. ถ้ามีการแก้ `calculate_modules/` → เปลี่ยน `CALC_VERSION` ใน `calculate_scores.py` (เช่น `"2026-10-20-v17"`)
2. `python rebuild_database.py` อีกครั้ง
3. commit `cis_database.db` ไปด้วย
4. `git push origin main` → Reboot app บน Streamlit Cloud ถ้าจำเป็น

**อัปเดตข้อมูล (branch `data/...`):** `fetch_price_history.py` → `compute_beta.py` → `rebuild_database.py` → commit ไฟล์ใน `Dataset/` + DB → PR → merge → เปลี่ยน `CALC_VERSION`

---

## 7. Conflict

เกิดได้ 3 จุด: `common.py` (หน้าจอ), `calculate_modules/common.py`, `calculate_scores.py` (`CALC_VERSION`)
→ ประกาศในกลุ่มก่อนแก้ ถ้าชนกัน คนที่ 11 ตัดสิน · `CALC_VERSION` ให้ใช้ค่าใหม่กว่าเสมอ

```bash
git status
# แก้ <<<<<<< / ======= / >>>>>>> ด้วยมือ
git add <ไฟล์> && git commit
python run_tests.py
```

---

## 8. สรุปแจกทีม

> **ก่อนแก้:** `git pull` + `git merge main`
> **ระหว่างแก้:** แตะแค่ไฟล์ตัวเอง · ทดสอบ `preview_my_page.py` ครบ 8 หุ้น · ไม่มีค่าสมมติ
> **ก่อน PR:** CHANGELOG + `chart_notes.py` + เอกสารพารามิเตอร์ (ถ้าเกี่ยว) · แท็ก Auditor + Layout
> **ตอนรวม:** merge ตามลำดับ · `rebuild_database.py` + `run_tests.py` · เปลี่ยน `CALC_VERSION` · commit DB
