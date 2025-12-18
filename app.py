import streamlit as st
import pandas as pd
import altair as alt
from streamlit_gsheets import GSheetsConnection

# 1. PAGE SETUP
st.set_page_config(page_title="How Spaghetti?", page_icon="🍝", layout="wide")

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🍝 How Spaghetti?")
    st.caption("The definitive 0-10 taxonomy of the Western genre.")

# 2. CONNECT TO GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data():
    try:
        df = conn.read()
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Connection Error: Could not read Google Sheet.")
    st.stop()

# 3. INITIALIZE MISSING COLUMNS (Auto-fixer)
# This ensures code doesn't crash if a column is empty in the sheet
metrics = [
    "Classically_Mythic", "Spaghettiness", "Grit", "Darkness", 
    "Weird", "Shenanigans", "Wild_Adventure", "Cinematography", "Sound_Score"
]

# Ensure we have a Vote_Count and Sum column for every metric
if "Vote_Count" not in df.columns:
    df["Vote_Count"] = 1
if "Sum_Rating" not in df.columns:
    df["Sum_Rating"] = df["Avg_Rating"]

for m in metrics:
    if m not in df.columns:
        df[m] = 5.0 # Default mid-point
    if f"Sum_{m}" not in df.columns:
        df[f"Sum_{m}"] = df[m]

# 4. THE SCATTERPLOT (Year vs Quality)
st.subheader("The Western Landscape")
st.caption("X: Year | Y: Overall Rating | Size: Spaghettiness")

scatter = alt.Chart(df).mark_circle().encode(
    x=alt.X('Year', scale=alt.Scale(domain=[1930, 2025]), title='Release Year'),
    y=alt.Y('Avg_Rating', scale=alt.Scale(domain=[0, 10]), title='Overall Rating (0-10)'),
    size=alt.Size('Spaghettiness', legend=None, scale=alt.Scale(range=[50, 500])),
    color=alt.Color('Type', legend=alt.Legend(title="Sub-Genre")),
    tooltip=['Title', 'Year', 'Avg_Rating', 'Spaghettiness', 'Classically_Mythic']
).properties(height=400).interactive()

st.altair_chart(scatter, use_container_width=True)

# 5. THE DATA DIRECTORY (RockAuto Style)
st.subheader("Movie Directory")
event = st.dataframe(
    df,
    column_order=("Poster_URL", "Title", "Year", "Type", "Avg_Rating", "Spaghettiness", "Classically_Mythic", "Grit", "Weird"),
    column_config={
        "Poster_URL": st.column_config.ImageColumn("Art", width="small"),
        "Title": st.column_config.TextColumn("Title", width="medium"),
        "Avg_Rating": st.column_config.NumberColumn("⭐ Rating", format="%.1f"),
        "Spaghettiness": st.column_config.ProgressColumn("🍝 Spaghetti", format="%.1f", min_value=0, max_value=10),
        "Classically_Mythic": st.column_config.ProgressColumn("🏛️ Mythic", format="%.1f", min_value=0, max_value=10),
        "Grit": st.column_config.ProgressColumn("🌵 Grit", format="%.1f", min_value=0, max_value=10),
        "Weird": st.column_config.NumberColumn("👽 Weird", format="%.1f"),
    },
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 6. THE REVIEW FORM (The DNA Matrix)
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    movie = df.iloc[selected_index]
    
    st.divider()
    c1, c2 = st.columns([1, 3])
    
    with c1:
        st.image(movie["Poster_URL"], caption=f"{movie['Year']}")
        st.metric("Current Rating", f"{movie['Avg_Rating']} / 10")
    
    with c2:
        st.subheader(f"Rate: {movie['Title']}")
        with st.form("rating_form"):
            st.write(" **0 = Absent | 10 = Maximum Intensity**")
            
            # Group 1: The Soul
            st.markdown("### 🎭 The Soul")
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                user_mythic = st.slider("🏛️ Classically Mythic", 0, 10, int(movie.get('Classically_Mythic', 5)))
                st.caption("Americana, John Wayne, Righteousness")
            with col_a2:
                user_spag = st.slider("🍝 Spaghettiness", 0, 10, int(movie.get('Spaghettiness', 5)))
                st.caption("Cynicism, Twang, Stare-downs")
            with col_a3:
                user_grit = st.slider("🌵 Grit", 0, 10, int(movie.get('Grit', 5)))
                st.caption("Mud, Blood, Sweat, Realism")

            # Group 2: The Vibe
            st.markdown("### 🔮 The Vibe")
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                user_dark = st.slider("md Darkness", 0, 10, int(movie.get('Darkness', 0)))
                st.caption("Bleak, Nihilistic, Evil")
            with col_b2:
                user_weird = st.slider("👽 Weirdo Factor", 0, 10, int(movie.get('Weird', 0)))
                st.caption("Surreal, Psychedelic, Off-wall")
            with col_b3:
                user_shenan = st.slider("🃏 Shenanigans", 0, 10, int(movie.get('Shenanigans', 0)))
                st.caption("Comedy, Parody, Slapstick")

            # Group 3: The Craft
            st.markdown("### 🎬 The Craft & Action")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                user_wild = st.slider("🐎 Wild Adventure", 0, 10, int(movie.get('Wild_Adventure', 5)))
                st.caption("Quests, Gold Rushes, Excitement")
            with col_c2:
                user_cine = st.slider("🎥 Cinematography", 0, 10, int(movie.get('Cinematography', 5)))
                st.caption("Visuals, Framing, Beauty")
            with col_c3:
                user_sound = st.slider("🎵 Sound & Score", 0, 10, int(movie.get('Sound_Score', 5)))
                st.caption("Morricone Twangs, Epic Swells")

            st.divider()
            user_overall = st.slider("⭐ Overall Rating (Your Enjoyment)", 0.0, 10.0, float(movie.get('Avg_Rating', 5.0)))

            submitted = st.form_submit_button("Submit 10-Point Rating", type="primary")
            
            if submitted:
                # Helper to calc new weighted average
                current_votes = float(movie.get("Vote_Count", 1))
                new_votes = current_votes + 1
                
                def calc_new(old_val, col_sum, user_input):
                    # If column missing, assume old_val * votes
                    curr_sum = float(movie.get(col_sum, old_val * current_votes))
                    new_sum = curr_sum + user_input
                    return new_sum, new_sum / new_votes

                # 1. Update Vote Count
                df.at[selected_index, "Vote_Count"] = new_votes

                # 2. Update Overall Rating
                n_sum, n_avg = calc_new(movie['Avg_Rating'], "Sum_Rating", user_overall)
                df.at[selected_index, "Sum_Rating"] = n_sum
                df.at[selected_index, "Avg_Rating"] = n_avg

                # 3. Update The 9 Metrics
                pairs = [
                    ("Classically_Mythic", user_mythic), ("Spaghettiness", user_spag),
                    ("Grit", user_grit), ("Darkness", user_dark),
                    ("Weird", user_weird), ("Shenanigans", user_shenan),
                    ("Wild_Adventure", user_wild), ("Cinematography", user_cine),
                    ("Sound_Score", user_sound)
                ]

                for metric_name, user_val in pairs:
                    sum_col = f"Sum_{metric_name}" # e.g. Sum_Grit
                    # Default old value to 5.0 if missing
                    old_val = float(movie.get(metric_name, 5.0))
                    
                    n_sum, n_avg = calc_new(old_val, sum_col, user_val)
                    
                    df.at[selected_index, sum_col] = n_sum
                    df.at[selected_index, metric_name] = n_avg
                
                # 4. Push to Cloud
                conn.update(data=df)
                st.success("✅ DNA Updated! Refreshing...")
                st.cache_data.clear()
                st.rerun()
