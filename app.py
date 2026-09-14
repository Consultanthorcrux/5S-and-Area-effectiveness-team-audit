import streamlit as st
import pandas as pd
import json, sqlite3, uuid
from pathlib import Path
from datetime import date, datetime

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "audit_data.db"
CHECKLIST_PATH = APP_DIR / "data" / "five_s_checklist.json"
DEPARTMENTS = ["Slip House & Spray Dryer", "Press & Glazeline", "Kiln, Polishing & Sorting"]
KPI_CATEGORIES = {
    "Q": "Quality", "P": "Production", "D": "Delivery", "C": "Cost", "S": "Safety"
}
RATING_HELP = {
    0: "Non-existent (no evidence)",
    1: "Evident in a few individual cases (<25% of area/zone)",
    2: "Evident in some areas (25% to 50% of area/zone)",
    3: "Evident in most areas (50% to 90% of area/zone)",
    4: "Evident in all areas",
}

st.set_page_config(page_title="Simpolo Audit Portal", page_icon="✅", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f5fbf7 0%,#eef5f1 46%,#f7faf8 100%);}
.block-container {max-width: 1220px; padding-top: 1.5rem; padding-bottom: 3rem;}
.hero {padding: 24px 28px; border-radius: 22px; color: white; background: linear-gradient(120deg,#0b5d3b,#178355); box-shadow: 0 14px 35px rgba(11,93,59,.20); margin-bottom:20px;}
.hero h1 {margin:0;font-size:2.05rem}.hero p{margin:.5rem 0 0;opacity:.92}
.option-card {background:white;border:1px solid #dce9e1;border-radius:20px;padding:19px;min-height:168px;box-shadow:0 8px 25px rgba(18,70,45,.08);}
.icon {font-size:42px;line-height:1}.option-card h3{color:#124b34;margin:.65rem 0 .35rem}.option-card p{color:#5b6f64}
.score-card {background:white;border-left:7px solid #198754;border-radius:16px;padding:16px 20px;box-shadow:0 5px 18px rgba(0,0,0,.06);}
.section-title{background:#e7f4ec;color:#124b34;padding:10px 14px;border-radius:10px;font-weight:700;margin-top:12px}
.small-muted{color:#6c7a72;font-size:.9rem}.footer{text-align:center;color:#708077;margin-top:30px;font-size:.85rem}
div[data-testid="stForm"] {background:rgba(255,255,255,.75);padding:18px;border-radius:18px;border:1px solid #e1ebe5}
.stButton>button, .stDownloadButton>button {border-radius:12px;font-weight:650}
</style>
""", unsafe_allow_html=True)

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS audits (
            audit_id TEXT PRIMARY KEY, audit_type TEXT, department TEXT, auditor TEXT,
            audit_date TEXT, shift TEXT, overall_score REAL, grade TEXT,
            details_json TEXT, created_at TEXT)""")
        con.commit()

def save_audit(payload):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("INSERT INTO audits VALUES (?,?,?,?,?,?,?,?,?,?)", payload)
        con.commit()

def grade(score):
    if score > 90: return "A"
    if score > 80: return "B"
    if score >= 60: return "C"
    return "D"

def score_banner(score):
    st.markdown(f'<div class="score-card"><b>Audit Score</b><br><span style="font-size:2rem;color:#0b5d3b;font-weight:800">{score:.1f}%</span> &nbsp; <b>Grade {grade(score)}</b></div>', unsafe_allow_html=True)

init_db()
if "view" not in st.session_state: st.session_state.view="Home"
if "last_result" not in st.session_state: st.session_state.last_result=None

st.markdown('<div class="hero"><h1>✅ Simpolo Audit Portal</h1><p>Digital audits for Area Effectiveness Teams and workplace 5S.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navigation")
    for v,icon in [("Home","🏠"),("AET Audit","📊"),("5S Audit","✨"),("Audit History","🗂️")]:
        if st.button(f"{icon}  {v}", use_container_width=True): st.session_state.view=v; st.rerun()
    st.divider()
    st.caption("Rating scale: 0 = no evidence, 4 = evident in all areas")

if st.session_state.view == "Home":
    st.subheader("Choose an audit")
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.markdown('<div class="option-card"><div class="icon">📊</div><h3>AET KPI Audit</h3><p>Audit Q, P, D, C and S performance for each departmental AET.</p></div>',unsafe_allow_html=True)
        if st.button("Start AET Audit",type="primary",use_container_width=True): st.session_state.view="AET Audit";st.rerun()
    with c2:
        st.markdown('<div class="option-card"><div class="icon">✨</div><h3>5S Audit</h3><p>Complete the Simpolo checklist for Sort, Set in Order, Shine, Standardize and Sustain.</p></div>',unsafe_allow_html=True)
        if st.button("Start 5S Audit",type="primary",use_container_width=True): st.session_state.view="5S Audit";st.rerun()
    st.info("After submission, the normalized score and grade appear immediately. Submitted records are available under Audit History.")

elif st.session_state.view == "AET Audit":
    st.subheader("📊 AET KPI Audit")
    st.caption("This version scores only Q, P, D, C and S. Each category is rated from 0 to 4 and normalized to 100%.")
    with st.form("aet_form", clear_on_submit=False):
        a,b,c,d=st.columns([2,1.4,1,1])
        department=a.selectbox("Departmental AET",DEPARTMENTS)
        auditor=b.text_input("Auditor name")
        audit_date=c.date_input("Audit date",date.today())
        shift=d.selectbox("Shift",["General","A","B","C"])
        records=[]
        for code,name in KPI_CATEGORIES.items():
            st.markdown(f'<div class="section-title">{code} · {name}</div>',unsafe_allow_html=True)
            x,y=st.columns([1,3])
            rating=x.select_slider(f"{name} rating",options=list(RATING_HELP),value=0,key=f"aet_{code}",format_func=lambda z:f"{z} - {RATING_HELP[z]}")
            evidence=y.text_area(f"Evidence / observation for {name}",key=f"ev_{code}",height=90,placeholder="Record factual evidence, gap, or reference...")
            z1,z2,z3=st.columns([2,1,1])
            action=z1.text_input(f"Action required for {name} (optional)",key=f"act_{code}")
            owner=z2.text_input(f"Owner - {name}",key=f"own_{code}")
            target=z3.date_input(f"Target date - {name}",value=None,key=f"tar_{code}")
            records.append({"code":code,"category":name,"rating":rating,"evidence":evidence,"action":action,"owner":owner,"target_date":str(target) if target else ""})
        submitted=st.form_submit_button("Submit AET Audit",type="primary",use_container_width=True)
    if submitted:
        if not auditor.strip(): st.error("Please enter the auditor name.")
        else:
            score=sum(r["rating"] for r in records)/(len(records)*4)*100
            aid=str(uuid.uuid4())[:8].upper()
            save_audit((aid,"AET",department,auditor.strip(),str(audit_date),shift,score,grade(score),json.dumps(records),datetime.now().isoformat(timespec="seconds")))
            st.success(f"AET audit {aid} submitted successfully.")
            score_banner(score)

elif st.session_state.view == "5S Audit":
    checklist=json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))
    st.subheader("✨ 5S Audit")
    st.caption("Checklist reproduced from the provided Simpolo checksheet. Ratings are normalized against the maximum possible rating of 4 per checkpoint.")
    with st.form("five_s_form",clear_on_submit=False):
        a,b,c,d=st.columns([2,1.4,1,1])
        department=a.selectbox("Audit Area / AET",DEPARTMENTS)
        auditor=b.text_input("Auditor name")
        audit_date=c.date_input("Audit date",date.today())
        shift=d.selectbox("Shift",["General","A","B","C"])
        records=[]
        for sec in checklist:
            st.markdown(f'<div class="section-title">{sec["number"]}. {sec["title"]}</div>',unsafe_allow_html=True)
            for item in sec["items"]:
                st.markdown(f'**{item["id"]}** {item["checkpoint"]}')
                x,y=st.columns([1,2.4])
                rating=x.selectbox("Rating",list(RATING_HELP),key=f'5s_{item["id"]}',format_func=lambda z:f"{z} - {RATING_HELP[z]}")
                notes=y.text_input("Notes / evidence",key=f'note_{item["id"]}',label_visibility="visible",placeholder="Add evidence or observation...")
                records.append({"section":sec["title"],"id":item["id"],"checkpoint":item["checkpoint"],"rating":rating,"notes":notes})
        submitted=st.form_submit_button("Submit 5S Audit",type="primary",use_container_width=True)
    if submitted:
        if not auditor.strip(): st.error("Please enter the auditor name.")
        else:
            score=sum(r["rating"] for r in records)/(len(records)*4)*100
            aid=str(uuid.uuid4())[:8].upper()
            save_audit((aid,"5S",department,auditor.strip(),str(audit_date),shift,score,grade(score),json.dumps(records),datetime.now().isoformat(timespec="seconds")))
            st.success(f"5S audit {aid} submitted successfully.")
            score_banner(score)

elif st.session_state.view == "Audit History":
    st.subheader("🗂️ Audit History")
    with sqlite3.connect(DB_PATH) as con:
        df=pd.read_sql_query("SELECT audit_id AS 'Audit ID', audit_type AS 'Type', department AS 'Department', auditor AS 'Auditor', audit_date AS 'Audit Date', shift AS 'Shift', ROUND(overall_score,1) AS 'Score (%)', grade AS 'Grade', created_at AS 'Submitted At' FROM audits ORDER BY created_at DESC",con)
    if df.empty: st.info("No audits have been submitted yet.")
    else:
        f1,f2=st.columns(2)
        types=f1.multiselect("Audit type",sorted(df["Type"].unique()),default=sorted(df["Type"].unique()))
        depts=f2.multiselect("Department",sorted(df["Department"].unique()),default=sorted(df["Department"].unique()))
        view=df[df["Type"].isin(types)&df["Department"].isin(depts)]
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.download_button("Download filtered history (CSV)",view.to_csv(index=False).encode("utf-8"),"simpolo_audit_history.csv","text/csv",use_container_width=True)
        st.caption("On Streamlit Community Cloud, local database files may reset when the app restarts or redeploys. Connect a permanent database for production use.")

st.markdown('<div class="footer">Simpolo Digital Audit Interface · AET KPI and 5S</div>',unsafe_allow_html=True)
