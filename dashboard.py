import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# ✅ Load data from Dropbox
url = "https://www.dropbox.com/scl/fi/ay8q5axg0lk60bkficjp8/df_cleaned_3.csv?rlkey=l0bd16aytkytv2m6za4tiojov&st=nmvq5k2h&raw=1"

try:
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    st.success("✅ File loaded from Dropbox!")
except Exception as e:
    st.error(f"❌ Failed to load file: {e}")
    st.stop()

# ✅ Begin dashboard
st.set_page_config(page_title="Student Quiz Dashboard", layout="wide")
st.title("🎓 Umagine Student Impact Dashboard")

# ---------- INSIGHT 1 ----------
st.header("📌 Insight 1: OVERALL QUIZ PERFORMANCE")

st.subheader("A. Average score per quiz")
avg_score = df['total_score'].mean()
st.metric("Average Score", f"{avg_score:.2f}")

st.subheader("B. Overall accuracy rate")
accuracy = df['is_correct'].mean() * 100
st.metric("Accuracy Rate", f"{accuracy:.2f}%")

st.subheader("C. Users who answered all questions correctly")
all_correct = df.groupby('user_id')['is_correct'].sum() == df.groupby('user_id')['question_no'].nunique()
st.metric("Users Got All Correct", all_correct.sum())

st.subheader("D. Question with the highest score")
score_by_question = df.groupby('question_no')['total_score'].mean().reset_index()
highest_q = score_by_question.loc[score_by_question['total_score'].idxmax()]['question_no']
st.success(f"Highest scoring question: {int(highest_q)}")

st.subheader("E. Question with the lowest score")
lowest_q = score_by_question.loc[score_by_question['total_score'].idxmin()]['question_no']
st.error(f"Lowest scoring question: {int(lowest_q)}")

# Histogram (Note: Fix score column name here if needed)
fig1 = px.histogram(df, x="total_score", nbins=20, title="Total Score Distribution", labels={'total_score': 'Score'})
st.plotly_chart(fig1)

# ---------- INSIGHT 2 ----------
st.header("📌 Insight 2: QUESTION-LEVEL ANALYSIS")

st.subheader("A. Most attempted questions")
attempts_per_question = df['question_no'].value_counts().reset_index()
attempts_per_question.columns = ['question_no', 'Attempts']
fig2 = px.bar(attempts_per_question.head(10), x='question_no', y='Attempts')
st.plotly_chart(fig2)

st.subheader("B. Questions with highest correct answers")
correct_rates = df[df['is_correct'] == True]['question_no'].value_counts().reset_index()
correct_rates.columns = ['question_no', 'Correct Count']
fig3 = px.bar(correct_rates.head(10), x='question_no', y='Correct Count')
st.plotly_chart(fig3)

st.subheader("C. Questions with lowest correct answers")
lowest_correct = correct_rates.sort_values(by='Correct Count').head(10)
fig4 = px.bar(lowest_correct, x='question_no', y='Correct Count')
st.plotly_chart(fig4)

st.subheader("D. Questions with most wrong answers")
wrong_answers = df[df['is_correct'] == False]['question_no'].value_counts().reset_index().head(10)
wrong_answers.columns = ['question_no', 'Wrong Count']
fig5 = px.bar(wrong_answers, x='question_no', y='Wrong Count')
st.plotly_chart(fig5)

st.subheader("E. Number of correct vs incorrect answers")
correct_vs_wrong = df['is_correct'].value_counts().reset_index()
correct_vs_wrong.columns = ['Correct', 'Count']
correct_vs_wrong['Correct'] = correct_vs_wrong['Correct'].map({True: 'Correct', False: 'Incorrect'})
fig6 = px.bar(correct_vs_wrong, x='Correct', y='Count', color='Correct')
st.plotly_chart(fig6)

# ---------- INSIGHT 3 ----------
st.header("📌 Insight 3: ATTEMPT PATTERNS")

st.subheader("A. Distribution of attempt counts")
attempt_counts = df['attempts'].value_counts().reset_index()
attempt_counts.columns = ['Attempts', 'Count']
fig7 = px.bar(attempt_counts.sort_values(by='Attempts'), x='Attempts', y='Count')
st.plotly_chart(fig7)

st.subheader("B. Average number of attempts per question")
avg_attempts = df.groupby('question_no')['attempts'].mean().reset_index()
fig8 = px.line(avg_attempts, x='question_no', y='attempts')
st.plotly_chart(fig8)

st.subheader("C. Users who completed all questions")
total_qs = df['question_no'].nunique()
user_question_counts = df.groupby('user_id')['question_no'].nunique()
completed_all = user_question_counts[user_question_counts == total_qs].count()
st.metric("Users Completed All Questions", completed_all)

st.subheader("D. Users answered correctly in first attempt")
first_attempts_correct = df[(df['attempts'] == 1) & (df['is_correct'] == True)]['user_id'].nunique()
st.metric("Correct on First Attempt", first_attempts_correct)

st.subheader("E. Users who needed more than one attempt")
more_than_one = df[df['attempts'] > 1]['user_id'].nunique()
st.metric("Users With >1 Attempt", more_than_one)

st.subheader("F. Students who got all answers wrong")
users_all_wrong = df.groupby('user_id')['is_correct'].sum() == 0
st.metric("Users Got All Wrong", users_all_wrong.sum())

# ---------- INSIGHT 4 ----------
st.header("📌 Insight 4: ERROR PATTERN ANALYSIS")

st.subheader("A. Most common incorrect options selected")
wrong_options = df[df['is_correct'] == False]['selected_option'].value_counts().reset_index().head(5)
wrong_options.columns = ['selected_option', 'count']
fig9 = px.bar(wrong_options, x='selected_option', y='count')
st.plotly_chart(fig9)

st.subheader("B. Same wrong answer selected multiple times")
same_wrong = df[df['is_correct'] == False].groupby(['user_id', 'quiz_question_id', 'selected_option']).size().reset_index(name='Count')
repeat_wrongs = same_wrong[same_wrong['Count'] > 1]
st.metric("Repeated Same Wrong Answers", repeat_wrongs.shape[0])

# ---------- INSIGHT 5 ----------
st.header("📌 Insight 5: SCORING TRENDS")

st.subheader("A. Score distribution histogram")
total_score_bins = pd.cut(df['total_score'], bins=[0, 2, 5, 8, 10], labels=["0-2", "3-5", "6-8", "9-10"])
total_score_dist = total_score_bins.value_counts().reset_index()
total_score_dist.columns = ['Range', 'Count']
fig10 = px.pie(total_score_dist, names='Range', values='Count')
st.plotly_chart(fig10)

st.subheader("B. Score range per question")
total_score_range = df.groupby('question_no')['total_score'].agg(['min', 'max']).reset_index()
st.dataframe(total_score_range)

