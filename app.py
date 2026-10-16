import streamlit as st
import pandas as pd
from datetime import date, timedelta
import uuid

st.set_page_config(page_title="CCMI | House Ledger", page_icon="🎵", layout="wide")
st.markdown("""<style>
.block-container {padding-top:2rem;max-width:1250px}
.hero {background:linear-gradient(115deg,#44206B,#8054B3);padding:28px;border-radius:20px;color:white;margin-bottom:18px}
.hero h1 {color:white!important;margin:0;font-size:2.1rem}
.hero p {color:#EDE1FF;margin-bottom:0}
[data-testid="stMetric"] {background:#F4EEFC;border:1px solid #E4D7F5;border-radius:16px;padding:18px}
h2,h3 {color:#533078}
</style>""", unsafe_allow_html=True)


def seed():
    today = date.today()
    st.session_state.assets = [
        dict(asset_id="JPC-MIC-001",name="Lead vocal microphone",category="Audio",team="JPC",location="Technical Store",condition="Good",status="Available",holder="",next_due=str(today+timedelta(days=21)),value=2200.0),
        dict(asset_id="KAV-KEY-001",name="Stage keyboard",category="Instrument",team="Kick Praise",location="Main Stage",condition="Good",status="Available",holder="",next_due=str(today+timedelta(days=40)),value=9500.0),
        dict(asset_id="JPC-ROB-001",name="Choir robe set",category="Wardrobe",team="JPC",location="Wardrobe Store",condition="Good",status="Available",holder="",next_due=str(today+timedelta(days=60)),value=3600.0),
        dict(asset_id="VIS-CAM-001",name="Broadcast camera",category="Video",team="ViSIT",location="Media Store",condition="Fair",status="Under Maintenance",holder="",next_due=str(today-timedelta(days=2)),value=14000.0),
    ]
    st.session_state.movements=[]
    st.session_state.maintenance=[]
    st.session_state.activity=[dict(time=str(today),action="Demo loaded",asset="Sample equipment")]

if "assets" not in st.session_state: seed()


def event(action, aid):
    st.session_state.activity.insert(0,dict(time=str(date.today()),action=action,asset=aid))


def frame(): return pd.DataFrame(st.session_state.assets)


def label(a): return f"{a['asset_id']} · {a['name']}"


with st.sidebar:
    st.title("🎵 House Ledger")
    st.caption("CCMI • Equipment & Assets")
    page=st.radio("Workspace",["Overview","Asset Register","Issue & Return","Maintenance","Reports"])
    st.divider()
    st.info("DEMO MODE\n\nSample data only. Changes last for this browser session. No database or API token needed.")
    if st.button("Reset demo data",use_container_width=True):
        seed(); st.rerun()

st.markdown('<div class="hero"><h1>Stewarding the house.</h1><p>CCMI Equipment & Assets Ledger · Interactive concept demo</p></div>',unsafe_allow_html=True)
st.caption("Fictional sample assets and values • Not an official church inventory • Values shown in GHS")

if page=="Overview":
    df=frame()
    st.subheader("An organised view of ministry resources")
    cols=st.columns(4)
    for c,title,value in zip(cols,["Registered assets","Available","In use","Under maintenance"],[len(df),sum(df.status=="Available"),sum(df.status=="In Use"),sum(df.status=="Under Maintenance")]): c.metric(title,int(value))
    left,right=st.columns([2,1])
    with left:
        st.subheader("Asset snapshot")
        st.dataframe(df[["asset_id","name","team","status","condition"]],hide_index=True,use_container_width=True)
        st.subheader("Maintenance attention")
        due=df[pd.to_datetime(df.next_due).dt.date<=date.today()+timedelta(days=30)]
        st.dataframe(due[["asset_id","name","next_due","status"]],hide_index=True,use_container_width=True)
    with right:
        st.subheader("Resources by team")
        st.bar_chart(df.groupby("team").size(),color="#9871C4")
        st.metric("Illustrative replacement value",f"GHS {df.value.sum():,.0f}")
    st.subheader("Recent activity")
    st.dataframe(pd.DataFrame(st.session_state.activity),hide_index=True,use_container_width=True)

elif page=="Asset Register":
    st.subheader("Asset Register")
    with st.expander("＋ Register an asset"):
        with st.form("new_asset",clear_on_submit=True):
            a,b=st.columns(2)
            aid=a.text_input("Asset ID",placeholder="JPC-MIC-002")
            name=b.text_input("Asset name")
            a,b,c=st.columns(3)
            category=a.selectbox("Category",["Audio","Instrument","Wardrobe","Video","Stage","IT","Other"])
            team=b.selectbox("Responsible team",["JPC","Kick Praise","Kavod SLFX","ViSIT","Crux","Other"])
            condition=c.selectbox("Condition",["New","Good","Fair","Poor","Damaged"],index=1)
            location=st.text_input("Home location")
            value=st.number_input("Replacement value (GHS)",min_value=0.0)
            due=st.date_input("Next maintenance",value=date.today()+timedelta(days=90))
            save=st.form_submit_button("Register asset",type="primary")
        if save:
            if not aid.strip() or not name.strip(): st.error("Enter an Asset ID and name.")
            elif any(x["asset_id"].casefold()==aid.strip().casefold() for x in st.session_state.assets): st.error("That Asset ID already exists.")
            else:
                st.session_state.assets.append(dict(asset_id=aid.strip(),name=name.strip(),category=category,team=team,location=location,condition=condition,status="Under Maintenance" if condition in ["Poor","Damaged"] else "Available",holder="",next_due=str(due),value=value))
                event("Asset registered",aid.strip()); st.success("Added to this demo session.")
    df=frame()
    a,b=st.columns(2)
    search=a.text_input("Search by name or ID")
    teams=b.multiselect("Filter by team",sorted(df.team.unique()))
    if search: df=df[df.name.str.contains(search,case=False,regex=False)|df.asset_id.str.contains(search,case=False,regex=False)]
    if teams: df=df[df.team.isin(teams)]
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.download_button("Export register CSV",df.to_csv(index=False).encode(),"demo_assets.csv","text/csv")

elif page=="Issue & Return":
    st.subheader("Issue & Return")
    issue_tab,return_tab=st.tabs(["Issue equipment","Receive a return"])
    with issue_tab:
        available=[a for a in st.session_state.assets if a["status"]=="Available"]
        if not available: st.info("No available assets. Return an issued item first.")
        else:
            with st.form("issue",clear_on_submit=True):
                aid=st.selectbox("Select asset",[a["asset_id"] for a in available],format_func=lambda v:label(next(a for a in available if a["asset_id"]==v)))
                borrower=st.text_input("Responsible person / borrower")
                purpose=st.text_input("Purpose / event")
                approver=st.text_input("Approved by (demo entry, not a verified approval)")
                due=st.date_input("Expected return",date.today()+timedelta(days=1))
                submit=st.form_submit_button("Issue asset",type="primary")
            if submit:
                asset=next(a for a in st.session_state.assets if a["asset_id"]==aid)
                if not borrower.strip() or not purpose.strip() or not approver.strip(): st.error("Complete borrower, purpose, and approver.")
                elif due<date.today(): st.error("Expected return cannot be in the past.")
                elif asset["status"]!="Available": st.error("Asset is no longer available.")
                else:
                    st.session_state.movements.append(dict(reference=uuid.uuid4().hex[:8].upper(),asset_id=aid,borrower=borrower,purpose=purpose,approved_by=approver,date_out=str(date.today()),due=str(due),returned="",condition_out=asset["condition"],condition_in="",received_by=""))
                    asset.update(status="In Use",holder=borrower); event("Asset issued",aid); st.success("Issued. Open Receive a return to return this item."); st.rerun()
    with return_tab:
        open_moves=[m for m in st.session_state.movements if not m["returned"]]
        if not open_moves: st.info("No open issues. Issue a sample asset first.")
        else:
            with st.form("return"):
                ref=st.selectbox("Open movement",[m["reference"] for m in open_moves],format_func=lambda v:next(f"{m['asset_id']} · {m['borrower']}" for m in open_moves if m["reference"]==v))
                condition=st.selectbox("Return condition",["Good","Fair","Poor","Damaged"])
                receiver=st.text_input("Received by")
                confirm=st.form_submit_button("Confirm return",type="primary")
            if confirm:
                if not receiver.strip(): st.error("Enter the receiving person's name.")
                else:
                    movement=next(m for m in open_moves if m["reference"]==ref)
                    movement.update(returned=str(date.today()),condition_in=condition,received_by=receiver)
                    asset=next(a for a in st.session_state.assets if a["asset_id"]==movement["asset_id"])
                    asset.update(condition=condition,status="Under Maintenance" if condition in ["Poor","Damaged"] else "Available",holder="")
                    event("Asset returned",asset["asset_id"]); st.rerun()
    st.subheader("Movement history")
    st.dataframe(pd.DataFrame(st.session_state.movements),hide_index=True,use_container_width=True)

elif page=="Maintenance":
    st.subheader("Maintenance Desk")
    st.caption("Record completed work. Issued assets must be returned before maintenance can be recorded.")
    eligible=[a for a in st.session_state.assets if a["status"] in ["Available","Under Maintenance"]]
    if eligible:
        with st.form("maintenance",clear_on_submit=True):
            aid=st.selectbox("Asset",[a["asset_id"] for a in eligible],format_func=lambda v:label(next(a for a in eligible if a["asset_id"]==v)))
            work=st.text_area("Work performed")
            tech=st.text_input("Technician / team")
            a,b=st.columns(2)
            cost=a.number_input("Cost (GHS)",min_value=0.0)
            condition=b.selectbox("Condition after work",["Good","Fair","Poor","Damaged"])
            due=st.date_input("Next service date",date.today()+timedelta(days=90))
            save=st.form_submit_button("Save completed maintenance",type="primary")
        if save:
            if not work.strip() or not tech.strip(): st.error("Enter work performed and technician.")
            elif due<date.today(): st.error("Next service date cannot be in the past.")
            else:
                asset=next(a for a in st.session_state.assets if a["asset_id"]==aid)
                st.session_state.maintenance.append(dict(asset_id=aid,date=str(date.today()),work=work,technician=tech,cost=cost,condition_after=condition,next_due=str(due)))
                asset.update(condition=condition,next_due=str(due),status="Under Maintenance" if condition in ["Poor","Damaged"] else "Available")
                event("Maintenance recorded",aid); st.success("Saved in this demo session.")
    st.dataframe(pd.DataFrame(st.session_state.maintenance),hide_index=True,use_container_width=True)

else:
    st.subheader("Reports & Downloads")
    for title,data in [("Asset Register",st.session_state.assets),("Movement History",st.session_state.movements),("Maintenance History",st.session_state.maintenance),("Demo Activity",st.session_state.activity)]:
        with st.expander(title,expanded=title=="Asset Register"):
            df=pd.DataFrame(data)
            st.dataframe(df,hide_index=True,use_container_width=True)
            st.download_button(f"Download {title}",df.to_csv(index=False).encode(),title.lower().replace(" ","_")+".csv","text/csv",key=title)

st.divider()
st.caption("CCMI House Ledger • Visual prototype only • Session-based data • No authentication or permanent storage")
