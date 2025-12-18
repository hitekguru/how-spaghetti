import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
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

# 3. INITIALIZE COLUMNS
metrics = [
    "Classically_Mythic", "Spaghettiness", "Grit", "Darkness", 
    "Weird", "Shenanigans", "Wild_Adventure", "Cinematography", "Sound_Score"
]

if "Vote_Count" not in df.columns:
    df["Vote_Count"] = 1
if "Sum_Rating" not in df.columns:
    df["Sum_Rating"] = df["Avg_Rating"]

for m in metrics:
    if m not in df.columns:
        df[m] = 5.0 
    if f"Sum_{m}" not in df.columns:
        df[f"Sum_{m}"] = df[m]

# 4. THE GENRE DNA EXPLORER (With Labels!)
st.subheader("🧬 Genre DNA Explorer")

# Controls
c1, c2, c3, c4 = st.columns(4)
with c1:
    x_axis = st.selectbox("X-Axis", metrics, index=1)
with c2:
    y_axis = st.selectbox("Y-Axis", metrics, index=2)
with c3:
    z_axis = st.selectbox("Size", ["Avg_Rating"] + metrics, index=0)
with c4:
    show_labels = st.checkbox("Show Movie Titles", value=True)

# Build the Chart
base = alt.Chart(df).encode(
    x=alt.X(x_axis, scale=alt.Scale(domain=[-0.5, 10.5]), title=x_axis),
    y=alt.Y(y_axis, scale=alt.Scale(domain=[-0.5, 10.5]), title=y_axis),
    tooltip=['Title', 'Year', 'Avg_Rating', x_axis, y_axis]
)

# 1. The Bubbles
bubbles = base.mark_circle().encode(
    size=alt.Size(z_axis, legend=None, scale=alt.Scale(range=[100, 1000])),
    color=alt.Color('Type', legend=alt.Legend(title="Sub-Genre", orient="bottom"))
)

# 2. The Text Labels
text = base.mark_text(
    align='center',
    baseline='middle',
    dy=-15,  # Shift text up slightly
    fontSize=10,
    color='white'
).encode(
    text='Title'
)

# Combine them
if show_labels:
    chart = (bubbles + text).properties(height=600).interactive()
else:
    chart = bubbles.properties(height=600).interactive()

st.altair_chart(chart, use_container_width=True)

# 5. MOVIE DIRECTORY
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
    height=800,
    on_select="rerun",
    selection_mode="single-row"
)

# 6. DRILL DOWN: RADAR CHART + REVIEW FORM
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    movie = df.iloc[selected_index]
    
    st.divider()
    
    # --- RADAR CHART SECTION ---
    r1, r2 = st.columns([1, 2])
    
    with r1:
        st.image(movie["Poster_URL"], caption=f"{movie['Year']} | {movie['Type']}")
        st.metric("Overall Enjoyment", f"{movie['Avg_Rating']} / 10")
    
    with r2:
        st.subheader(f"Genre Fingerprint: {movie['Title']}")
        
        # Prepare Data for Plotly
        radar_data = pd.DataFrame(dict(
            r=[movie[m] for m in metrics],
            theta=metrics
        ))
        
        # Draw Plotly Chart
        fig = px.line_polar(radar_data, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', line_color='#ff4b4b')
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], showticklabels=False),
            ),
            margin=dict(t=20, b=20, l=40, r=40),
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- SLIDERS SECTION ---
    st.subheader("🧬 Update the DNA")
    with st.form("rating_form"):
        st.write("Adjust sliders to refine the taxonomy.")
        
        c_a1, c_a2, c_a3 = st.columns(3)
        with c_a1: u_mythic = st.slider("🏛️ Mythic", 0, 10, int(movie.get('Classically_Mythic', 5)))
        with c_a2: u_spag = st.slider("🍝 Spaghettiness", 0, 10, int(movie.get('Spaghettiness', 5)))
        with c_a3: u_grit = st.slider("🌵 Grit", 0, 10, int(movie.get('Grit', 5)))

        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1: u_dark = st.slider("🌑 Darkness", 0, 10, int(movie.get('Darkness', 0)))
        with c_b2: u_weird = st.slider("👽 Weird", 0, 10, int(movie.get('Weird', 0)))
        with c_b3: u_shenan = st.slider("🃏 Shenanigans", 0, 10, int(movie.get('Shenanigans', 0)))

        c_c1, c_c2, c_c3 = st.columns(3)
        with c_c1: u_wild = st.slider("🐎 Wild Adventure", 0, 10, int(movie.get('Wild_Adventure', 5)))
        with c_c2: u_cine = st.slider("🎥 Cinematography", 0, 10, int(movie.get('Cinematography', 5)))
        with c_c3: u_sound = st.slider("🎵 Sound & Score", 0, 10, int(movie.get('Sound_Score', 5)))

        st.divider()
        u_overall = st.slider("⭐ Overall Rating", 0.0, 10.0, float(movie.get('Avg_Rating', 5.0)))
        
        if st.form_submit_button("Submit Rating"):
            # Update Logic
            curr_votes = float(movie.get("Vote_Count", 1))
            new_votes = curr_votes + 1
            
            def calc_new(old_val, col_sum, user_input):
                curr_sum = float(movie.get(col_sum, old_val * curr_votes))
                new_sum = curr_sum + user_input
                return new_sum, new_sum / new_votes

            df.at[selected_index, "Vote_Count"] = new_votes
            n_s, n_a = calc_new(movie['Avg_Rating'], "Sum_Rating", u_overall)
            df.at[selected_index, "Sum_Rating"] = n_s
            df.at[selected_index, "Avg_Rating"] = n_a

            inputs = [
                ("Classically_Mythic", u_mythic), ("Spaghettiness", u_spag), ("Grit", u_grit),
                ("Darkness", u_dark), ("Weird", u_weird), ("Shenanigans", u_shenan),
                ("Wild_Adventure", u_wild), ("Cinematography", u_cine), ("Sound_Score", u_sound)
            ]
            
            for m_name, u_val in inputs:
                s_col = f"Sum_{m_name}"
                n_s, n_a = calc_new(float(movie.get(m_name, 5.0)), s_col, u_val)
                df.at[selected_index, s_col] = n_s
                df.at[selected_index, m_name] = n_a
            
            conn.update(data=df)
            st.success("✅ DNA Updated!")
            st.cache_data.clear()
            st.rerun()
