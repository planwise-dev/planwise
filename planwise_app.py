
# planwise_app.py
import streamlit as st
import datetime
import pandas as pd

# ---------- TITLE & INTRO ---------- #
st.set_page_config(page_title="PlanWise", layout="wide")
st.title("📚 PlanWise - Study Planner")
st.markdown("Designed to help you organize, focus, and conquer your revision.")

# ---------- USER INPUT ---------- #
st.header("🧠 Enter Your Study Details")

subjects = st.text_area("List your subjects (one per line)").split("\n")
exam_date = st.date_input("When is your first exam?", min_value=datetime.date.today())

study_hours_per_day = st.slider("How many hours per day can you study?", 1, 12, 3)
days_per_week = st.slider("How many days per week can you study?", 1, 7, 5)

focus_mode = st.selectbox(
    "Choose your focus style:",
    ["Classic", "ADHD-Friendly", "Intense (Cram Mode)"]
)

confidence_map = {}
st.subheader("📊 How confident are you in each subject?")
for subject in subjects:
    if subject.strip():
        confidence_map[subject] = st.slider(f"{subject} confidence (1 = low, 5 = high)", 1, 5, 3)

# ---------- PLAN GENERATION ---------- #
def generate_study_plan(subjects, confidence_map, start_date, hours_per_day, days_per_week):
    plan = []
    total_days = (exam_date - start_date).days
    total_slots = total_days * days_per_week * hours_per_day / 7

    weightings = {
        subject: 6 - confidence_map[subject]  # Lower confidence = higher weight
        for subject in subjects if subject.strip()
    }
    total_weight = sum(weightings.values())

    hours_per_subject = {
        subject: round((weight / total_weight) * total_slots)
        for subject, weight in weightings.items()
    }

    current_date = start_date
    while current_date <= exam_date:
        if (current_date - start_date).days % 7 < days_per_week:
            for _ in range(hours_per_day):
                for subject in sorted(hours_per_subject, key=lambda x: hours_per_subject[x], reverse=True):
                    if hours_per_subject[subject] > 0:
                        plan.append((current_date, subject))
                        hours_per_subject[subject] -= 1
                        break
        current_date += datetime.timedelta(days=1)

    return pd.DataFrame(plan, columns=["Date", "Subject"])

# ---------- DISPLAY STUDY PLAN ---------- #
if st.button("📆 Generate My Plan"):
    if not subjects or not exam_date:
        st.warning("Please fill in all inputs.")
    else:
        plan_df = generate_study_plan(subjects, confidence_map, datetime.date.today(), study_hours_per_day, days_per_week)
        st.success("Here's your personalized study plan!")
        st.dataframe(plan_df)

        csv = plan_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Plan as CSV",
            data=csv,
            file_name='planwise_study_plan.csv',
            mime='text/csv'
        )

        st.markdown("---")
        st.markdown("✨ *Pro Tip: Revisit this page anytime to tweak your plan or adjust your confidence levels.*")
