import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# ✅ CSV from Google Drive
csv_url = "https://drive.google.com/uc?export=download&id=1UYSiHKKxqwq2s5Tjtypnce3-tz6xqDlV"

st.set_page_config(page_title="Student Quiz Dashboard", layout="wide")
st.title("🎓 Umagine Student Impact Dashboard")

# ✅ Load CSV from Google Drive
try:
    response = requests.get(csv_url)
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    st.success("✅ File loaded successfully from Google Drive!")
except Exception as e:
    st.error(f"❌ Failed to load CSV: {e}")
    st.stop()

# ✅ Show columns for debug
st.write("📊 Columns in your CSV:", df.columns.tolist())

# ✅ Check required columns
required_columns = ['total_score', 'is_correct', 'user_id', 'question_no', 'score', 'attempts', 'selected_option', 'quiz_question_id']
missing = [col for col in required_columns if col not in df.columns]
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# -------------------------------------
# 📌 Insight 1: OVERALL QUIZ PERFORMANCE
# -------------------------------------
st.header("📌 Insight 1: OVERALL QUIZ PERFORMANCE")

st.subheader("A. Average score per quiz")
st.metric("Average Score", f"{df['total_score'].mean():.2f}")

st.subheader("B. Overall accuracy rate")
st.metric("Accuracy Rate", f"{df['is_correct'].mean() * 100:.2f}%")

st.subheader("C. Users who answered all questions correctly")
all_correct = df.groupby('user_id')['is_correct'].sum() == df.groupby('user_id')['question_no'].nunique()
st.metric("Users Got All Correct", all_correct.sum())

st.subheader("D. Question with the highest score")
score_by_question = df.groupby('question_no')['total_score'].mean().reset_index()
high_q = score_by_question.loc[score_by_question['total_score'].idxmax()]['question_no']
st.success(f"Highest scoring question: {int(high_q)}")

st.subheader("E. Question with the lowest score")
low_q = score_by_question.loc[score_by_question['total_score'].idxmin()]['question_no']
st.error(f"Lowest scoring question: {int(low_q)}")

st.plotly_chart(px.histogram(df, x="total_score", nbins=20, title="Score Distribution", labels={'total_score': 'Score'}))

# -------------------------------------
# 📌 Insight 2: QUESTION-LEVEL ANALYSIS
# -------------------------------------
st.header("📌 Insight 2: QUESTION-LEVEL ANALYSIS")

st.subheader("A. Most attempted questions")
attempts_q = df['question_no'].value_counts().reset_index()
attempts_q.columns = ['question_no', 'Attempts']
st.plotly_chart(px.bar(attempts_q.head(10), x='question_no', y='Attempts', title="Most Attempted Questions"))

st.subheader("B. Highest correct answers")
correct = df[df['is_correct'] == True]['question_no'].value_counts().reset_index()
correct.columns = ['question_no', 'Correct Count']
st.plotly_chart(px.bar(correct.head(10), x='question_no', y='Correct Count', title="Most Correct Answers"))

st.subheader("C. Lowest correct answers")
lowest_correct = correct.sort_values(by='Correct Count').head(10)
st.plotly_chart(px.bar(lowest_correct, x='question_no', y='Correct Count', title="Lowest Correct Answers"))

st.subheader("D. Most wrong answers")
wrong = df[df['is_correct'] == False]['question_no'].value_counts().reset_index()
wrong.columns = ['question_no', 'Wrong Count']
st.plotly_chart(px.bar(wrong.head(10), x='question_no', y='Wrong Count', title="Most Wrong Answers"))

st.subheader("E. Correct vs Incorrect")
correct_wrong = df['is_correct'].value_counts().reset_index()
correct_wrong.columns = ['Correct', 'Count']
correct_wrong['Correct'] = correct_wrong['Correct'].map({True: 'Correct', False: 'Incorrect'})
st.plotly_chart(px.bar(correct_wrong, x='Correct', y='Count', color='Correct', title="Correct vs Incorrect"))

# -------------------------------------
# 📌 Insight 3: ATTEMPT PATTERNS
# -------------------------------------
st.header("📌 Insight 3: ATTEMPT PATTERNS")

st.subheader("A. Attempt Distribution")
attempts_count = df['attempts'].value_counts().reset_index()
attempts_count.columns = ['Attempts', 'Count']
st.plotly_chart(px.bar(attempts_count.sort_values(by='Attempts'), x='Attempts', y='Count', title="Attempt Distribution"))

st.subheader("B. Avg attempts per question")
avg_attempts = df.groupby('question_no')['attempts'].mean().reset_index()
st.plotly_chart(px.line(avg_attempts, x='question_no', y='attempts', title="Avg Attempts per Question"))

st.subheader("C. Users who completed all questions")
total_qs = df['question_no'].nunique()
completed = df.groupby('user_id')['question_no'].nunique() == total_qs
st.metric("Users Completed All", completed.sum())

st.subheader("D. Correct on first attempt")
first_correct = df[(df['attempts'] == 1) & (df['is_correct'])]['user_id'].nunique()
st.metric("Correct First Attempt", first_correct)

st.subheader("E. Users with >1 attempt")
more_than_once = df[df['attempts'] > 1]['user_id'].nunique()
st.metric("Users With >1 Attempt", more_than_once)

st.subheader("F. Users with all wrong")
all_wrong = df.groupby('user_id')['is_correct'].sum() == 0
st.metric("All Wrong Users", all_wrong.sum())

# -------------------------------------
# 📌 Insight 4: ERROR PATTERN ANALYSIS
# -------------------------------------
st.header("📌 Insight 4: ERROR PATTERN ANALYSIS")

st.subheader("A. Top wrong options selected")
wrong_opts = df[df['is_correct'] == False]['selected_option'].value_counts().reset_index().head(5)
wrong_opts.columns = ['selected_option', 'count']
st.plotly_chart(px.bar(wrong_opts, x='selected_option', y='count', title="Top Wrong Options"))

st.subheader("B. Repeated same wrong answers")
repeat = df[df['is_correct'] == False].groupby(['user_id', 'quiz_question_id', 'selected_option']).size().reset_index(name='count')
repeat_same = repeat[repeat['count'] > 1]
st.metric("Repeated Wrong Answers", repeat_same.shape[0])

# -------------------------------------
# 📌 Insight 5: SCORING TRENDS
# -------------------------------------
st.header("📌 Insight 5: SCORING TRENDS")

st.subheader("A. Score histogram")
score_bins = pd.cut(df['total_score'], bins=[0,2,5,8,10], labels=["0-2", "3-5", "6-8", "9-10"])
score_dist = score_bins.value_counts().reset_index()
score_dist.columns = ['Range', 'Count']
st.plotly_chart(px.pie(score_dist, names='Range', values='Count', title="Score Distribution Ranges"))

st.subheader("B. Score range per question")
range_q = df.groupby('question_no')['total_score'].agg(['min', 'max']).reset_index()
st.dataframe(range_q)
