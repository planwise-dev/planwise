
import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="PlanWise", layout="wide")
st.title("📚 PlanWise - Study Planner (v1.1)")
st.markdown("Designed to help you plan study + practice time by confidence.")

st.header("🧠 Study Setup")

subjects = st.text_area("List your subjects (one per line)").split("\n")
exam_date = st.date_input("When is your first exam?", min_value=datetime.date.today())
study_days = st.slider("How many days per week will you study?", 1, 7, 5)
study_hours = st.slider("Hours available per study day", 1, 12, 3)

focus_mode = st.selectbox("Study Style", ["Classic", "ADHD-Friendly", "Cram Mode"])

st.subheader("📊 Confidence, Content & Practice Time per Subject")

subject_data = []
for subject in subjects:
    if subject.strip():
        col1, col2, col3 = st.columns(3)
        with col1:
            conf = st.slider(f"{subject} - Confidence", 1, 5, 3, key=subject+"_conf")
        with col2:
            content_hours = st.number_input(f"{subject} - Content hrs", 1, 100, 10, key=subject+"_content")
        with col3:
            practice_hours = st.number_input(f"{subject} - Practice hrs", 1, 100, 5, key=subject+"_practice")
        subject_data.append({
            "subject": subject,
            "confidence": conf,
            "content_hours": content_hours,
            "practice_hours": practice_hours
        })

def generate_schedule(subjects_info, total_days, hours_per_day, days_per_week):
    plan = []
    slots = total_days * (days_per_week / 7) * hours_per_day

    total_weight = sum([(6 - s["confidence"]) * (s["content_hours"] + s["practice_hours"]) for s in subjects_info])
    weight_map = {s["subject"]: ((6 - s["confidence"]) * (s["content_hours"] + s["practice_hours"])) / total_weight for s in subjects_info}

    hour_allocations = {s["subject"]: round(slots * weight_map[s["subject"]]) for s in subjects_info}

    current_date = datetime.date.today()
    subject_index = 0
    while current_date <= exam_date:
        if (current_date - datetime.date.today()).days % 7 < days_per_week:
            for _ in range(hours_per_day):
                if not subjects_info:
                    break
                sub = subjects_info[subject_index % len(subjects_info)]["subject"]
                if hour_allocations[sub] > 0:
                    plan.append((current_date, sub))
                    hour_allocations[sub] -= 1
                subject_index += 1
        current_date += datetime.timedelta(days=1)

    return pd.DataFrame(plan, columns=["Date", "Subject"])

if st.button("📆 Generate Plan"):
    if not subject_data or not exam_date:
        st.error("Fill in all fields.")
    else:
        days = (exam_date - datetime.date.today()).days
        df = generate_schedule(subject_data, days, study_hours, study_days)
        st.success("✅ Your plan is ready!")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "study_schedule.csv", "text/csv")
