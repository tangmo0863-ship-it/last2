# CIS — Comprehensive Investment System (v16)

Dashboard วิเคราะห์หุ้นกลุ่มเทคโนโลยีใน SET 8 ตัว (ADVANC, CCET, DELTA, HANA, JMART, KCE, THCOM, TRUE)
6 โมดูล + หน้า Overview สร้างด้วย Streamlit ทุกตัวเลขคำนวณจากข้อมูลจริงในโฟลเดอร์ `Dataset/`
ถ้าข้อมูลไม่พอ ระบบแสดง **N/A** พร้อมเหตุผล — ไม่มีค่าสมมติ/ค่าเดา

- ข้อมูลราคา: 5 ม.ค. 2015 – 30 ธ.ค. 2025 (Yahoo Finance) · งบการเงิน: FY2023 – FY2025
- เวอร์ชันสูตรคำนวณปัจจุบัน: `CALC_VERSION = "2026-10-05-v16"` (ใน `calculate_scores.py`)

---

## โครงสร้างไฟล์

```
cis-dashboard/
├── app.py                        ★ จุดเริ่มแอป: ประกอบหน้า + routing
├── common.py                     ★ ฝั่งหน้าจอ: CSS (รองรับมือถือ/iPad), sidebar, โหลดข้อมูล, PageContext,
│                                   show_chart(), render_chart_note(), ตรวจ DB เก่าแล้วคำนวณใหม่อัตโนมัติ
├── chart_notes.py                ★ ข้อความ "ⓘ วิธีอ่านกราฟและเทคนิคที่ใช้" ใต้กราฟทั้ง 11 ตัว + การ์ด Market Expectation
├── pages_content/                ★ หน้าจอ 1 ไฟล์ต่อ 1 หน้า (overview + 6 โมดูล)
├── calculate_modules/            ★ สูตรคำนวณ 1 ไฟล์ต่อ 1 โมดูล
│   ├── common.py                   clean_float(), SECTOR_MAP, RISK_FREE_RATE (1.66%) ใช้ร่วมกันทุกโมดูล
│   ├── company_health.py · fair_value.py · entry_timing.py · ai_prediction.py · risk_analysis.py
│   └── industry_benchmark.py       จัดอันดับ + Overall Score (รอผล 5 โมดูลก่อน)
├── calculate_scores.py           ★ Orchestrator: เรียกทุกโมดูล บันทึกผลลง DB + CALC_VERSION
├── import_data.py                ★ นำ CSV เข้า SQLite (cis_database.db)
├── Dataset/
│   ├── master_all_8_stocks_financials.csv   งบการเงิน FY2023-2025
│   ├── stock_cleaned_data_2015_2025.csv     ราคา + ตัวชี้วัด 10 ปี
│   ├── stock_risk_metrics.csv               Beta / Downside Beta (สร้างโดย compute_beta.py)
│   └── set_index_2015_2025.csv              ข้อมูลตลาด (TDEX) ที่ใช้คำนวณ Beta — เก็บไว้เป็นหลักฐาน
├── .streamlit/config.toml        ธีมสีสว่าง
├── requirements.txt
│
│   — เครื่องมือข้อมูล (ไม่จำเป็นต่อการเปิดแอป) —
├── fetch_price_history.py        ดึงราคาจาก Yahoo Finance + คำนวณตัวชี้วัดด้วยสูตรเดียวกับไฟล์เดิม
├── compute_beta.py               คำนวณ Beta เทียบตลาด (3 ปี, ผลตอบแทนรายวัน) → stock_risk_metrics.csv
├── rebuild_database.py           คำนวณ DB ใหม่ทั้งหมด + ตรวจผล 6 ข้อ
│
│   — สคริปต์สร้างหลักฐานสำหรับเล่ม/สไลด์ (ไม่จำเป็นต่อการเปิดแอป) —
├── model_comparison.py           เปรียบเทียบ 4 โมเดล AI
├── sensitivity_analysis.py       ทดสอบน้ำหนักคะแนน
├── backtest_signals.py           Backtest สัญญาณ Entry Timing (หักค่าธรรมเนียม)
├── tune_ai.py                    ปรับจูน AI ด้วย TimeSeriesSplit
│
│   — เครื่องมือทีม —
├── preview_my_page.py            เปิดดูหน้าเดียวตอนพัฒนา
├── run_tests.py                  ทดสอบทุกหน้า × ทุกหุ้นก่อน deploy
└── README.md · TEAM_ROLES.md · GIT_WORKFLOW.md · EDGE_CASES.md
```

**ไฟล์ชื่อซ้ำ (ระวังวางผิดโฟลเดอร์):** `common.py`, `fair_value.py`, `risk_analysis.py`, `entry_timing.py` ฯลฯ
มีทั้งในโฟลเดอร์หลัก/`pages_content/` (หน้าจอ — มี `import streamlit`) และใน `calculate_modules/` (สูตร — ไม่มี streamlit)

---

## วิธีรัน

```bash
pip install -r requirements.txt
python rebuild_database.py      # คำนวณ DB ใหม่ + ตรวจผล (หรือ: python import_data.py && python calculate_scores.py)
streamlit run app.py            # เปิด http://localhost:8501
```

**Deploy (Streamlit Community Cloud):** push ทั้งโฟลเดอร์ขึ้น GitHub → share.streamlit.io → Main file `app.py`
ถ้าไม่มี `cis_database.db` หรือ `calc_version` ใน DB ไม่ตรงกับ `CALC_VERSION` แอปจะคำนวณใหม่เองตอนเปิดครั้งแรก (10–30 วินาที)

**กฎสำคัญ:** แก้สูตรใน `calculate_modules/` ทุกครั้ง → เปลี่ยนค่า `CALC_VERSION` ใน `calculate_scores.py`
ไม่งั้นเว็บที่ deploy จะยังแสดงตัวเลขเก่า

**อัปเดตข้อมูลราคา / Beta (ต้องต่ออินเทอร์เน็ต รันใน Colab ได้):**
```bash
pip install yfinance
python fetch_price_history.py   # → Dataset/stock_cleaned_data_2015_2025.csv
python compute_beta.py          # → Dataset/stock_risk_metrics.csv (ถ้าดึงดัชนีไม่ได้: --index-file ไฟล์.csv)
python rebuild_database.py
```

---

## หลักการคำนวณ (สรุป)

| โมดูล | วิธีคำนวณ | อ้างอิงหลัก |
|---|---|---|
| 💚 Company Health | ROE/ROA คำนวณจากงบจริง (กำไรสุทธิ ÷ ส่วนผู้ถือหุ้น / สินทรัพย์) ถ่วง ROE 30% · ROA 25% · สภาพคล่อง 20% · หนี้ 25% | Nissim & Penman (2001), Soliman (2008) |
| ⚖️ Fair Value | DCF (Gordon Growth, หนี้สุทธิไม่รวมเจ้าหนี้การค้า) 55% + P/E 45% · การ์ด "ราคานี้คาดหวังอะไร": ROE ที่ราคาต้องการ (Residual Income, Ke จาก CAPM) เทียบ ROE จริง · เตือนเมื่อ FCF > 1.5 เท่าของกำไร | Damodaran (2012), Graham (1973), Dechow et al. (1999) |
| ⏱️ Entry Timing | Trend 60 (ราคา>EMA20, EMA20>EMA50, ราคา>MA200) + Momentum 40 (MACD>0, ADX≥25, Volume>เฉลี่ย 20 วัน) · ราคา<MA200 บังคับ BEARISH · Stop Loss = ต่ำสุด 30 วัน | Wilder (1978), Appel (2005), Elder (1993), Timmermann (2006) |
| 🔮 AI Prediction | Random Forest แยกรายหุ้น ทำนายทิศทาง 10 วัน · Feature 11 ตัวแบบสัดส่วน · ฝึก 2015-2024 / ทดสอบ 2025 + Purging · ไม่ชนะ Baseline → **NO EDGE** (ไม่นับคะแนน) | López de Prado (2018), Breiman (2001) |
| 🛡️ Risk Analysis | 3 ปีล่าสุด (TRUE หลังควบรวม 3 มี.ค. 2023) · VaR/CVaR 95%, Drawdown, Volatility, Beta, PSR → 5 มิติ 30/25/20/15/10 · Rf 1.66% | Jorion (2007), Daves et al. (2000), Ang et al. (2006) |
| 📊 Industry Benchmark | Overall = ค่าเฉลี่ยถ่วง 5 โมดูล (Health 25 · Valuation 25 · Timing 15 · AI 10 · Risk 15) · Industry Score แสดงอันดับในกลุ่มเท่านั้น ไม่นับซ้ำ | Nissim & Penman (2001), Yeh & Liu (2020) |

**พารามิเตอร์ตลาด:** Rf 1.66% (ThaiBMA พันธบัตร 10 ปี สิ้นปี 2568) · ERP 6.30% (Damodaran, ม.ค. 2026) · g 2.0% (เป้าเงินเฟ้อ ธปท.) · Beta ปรับแบบ Blume

ที่มาของทุกตัวเลขและสถานะหลักฐาน: เอกสาร "ที่มาของตัวเลขและพารามิเตอร์" · คำอธิบายกราฟ: `chart_notes.py` · ประวัติการแก้สูตร: CHANGELOG ที่หัวไฟล์ใน `calculate_modules/`
(`DATA_FORMULA_AUDIT.md` เดิมเลิกใช้แล้ว เนื้อหาไม่ตรงกับโค้ดปัจจุบัน)

---

## หลักฐานประกอบเล่ม (ผลจากสคริปต์)

| เรื่อง | ผล |
|---|---|
| เปรียบเทียบโมเดล AI | Random Forest ชนะ Baseline 3/8 หุ้น (เท่ากับ Logistic Regression ดีที่สุด) |
| ปรับจูน AI | ไม่ได้เพิ่มหุ้นที่ชนะ Baseline → คงพารามิเตอร์เดิม |
| Sensitivity น้ำหนัก | หุ้นอันดับ 1 ไม่เปลี่ยนใน 17 สถานการณ์ |
| Backtest Entry Timing (2016-2025) | STRONG BUY ชนะ Baseline +1.81 จุด/20 วัน (ทิศทางสม่ำเสมอ แต่ยังไม่มีนัยสำคัญทางสถิติ) |
| การ์ด Market Expectation | ทำนายผลตอบแทนปีถัดไปไม่ได้ (Spearman 0.00, n=16) → ใช้ทำความเข้าใจราคา ไม่ใช่สัญญาณซื้อขาย |

## ข้อจำกัดหลัก

- WACC และ Target P/E ยังเป็นค่าที่ทีมกำหนดตามกลุ่ม (DCF ด้วย CAPM แกว่งรุนแรงเพราะดอกเบี้ยไทยต่ำ และ FCF ของหุ้นสื่อสารสูงเกินจริงเพราะไม่มีข้อมูลค่าเช่าโครงข่าย/ใบอนุญาต)
- Beta เทียบ TDEX (ETF อ้างอิง SET50) แทนดัชนี SET เพราะดึงข้อมูลดัชนีไม่ได้
- งบการเงินมีแค่ 3 ปี จึงทดสอบย้อนหลังด้านมูลค่าได้จำกัด
- การประเมินนี้ไม่ใช่คำแนะนำในการลงทุน
