import streamlit as st
import pandas as pd
import altair as alt

# 1. PAGE SETUP
st.set_page_config(page_title="How Spaghetti?", page_icon="🍝", layout="wide")

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🍝 How Spaghetti?")
    st.caption("The definitive taxonomy of the Western genre.")

# 2. LOAD DATA
@st.cache_data
def load_data():
    # We load the CSV we just created
    df = pd.read_csv("westerns.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ critical error: westerns.csv not found. Did you upload it to GitHub?")
    st.stop()

# 3. THE "SPAGHETTI PLOT" (Top Section)
st.subheader("The Sauce Spectrum")
blob_chart = alt.Chart(df).mark_circle().encode(
    x=alt.X('Year', scale=alt.Scale(domain=[1950, 2025]), title='Release Year'),
    y=alt.Y('Spaghetti_Intensity', scale=alt.Scale(domain=[0, 5]), title='Spaghetti-ness (0-5)'),
    size=alt.Size('Avg_Rating', legend=None, scale=alt.Scale(range=[100, 500])),
    color=alt.Color('Type', legend=alt.Legend(title="Sub-Genre")),
    tooltip=['Title', 'Year', 'Spaghetti_Intensity', 'Avg_Rating']
).properties(
    height=350
).interactive()

st.altair_chart(blob_chart, use_container_width=True)

# 4. THE DATA DIRECTORY (Middle Section)
st.subheader("Movie Directory")

event = st.dataframe(
    df,
    column_config={
        "Poster_URL": st.column_config.ImageColumn("Art", width="small"),
        "Title": st.column_config.TextColumn("Title", width="medium"),
        "Spaghetti_Intensity": st.column_config.ProgressColumn(
            "How Spaghetti?", 
            format="%.1f 🍝", 
            min_value=0, 
            max_value=5,
        ),
        "Remaster_Avail": st.column_config.CheckboxColumn("Restored?", disabled=True),
        "Avg_Rating": st.column_config.NumberColumn("Enjoyment", format="%.1f ⭐"),
        "Type": st.column_config.TextColumn("Primary Type"),
    },
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 5. THE DRILL DOWN (Bottom Section)
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    movie = df.iloc[selected_index]
    
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 2])
    
    with c1:
        st.image(movie["Poster_URL"], caption=f"{movie['Year']}")
    
    with c2:
        st.markdown(f"### Review: *{movie['Title']}*")
        st.write(f"**Current Type:** {movie['Type']}")
        
        st.markdown("#### 📼 Which copy did you watch?")
        version = st.radio(
            "Version", 
            ["Standard / Original", "Remastered / 4K"], 
            horizontal=False,
            label_visibility="collapsed"
        )
        
        if version == "Remastered / 4K":
            st.success("Tracking visual fidelity for Remaster.")
            st.slider("✨ Visual Upgrade Score", 1, 5, 3)

    with c3:
        st.markdown("#### 🍝 The Sauce Scale")
        st.slider("How Spaghetti is it?", 0.0, 5.0, float(movie['Spaghetti_Intensity']))
        st.button("Submit Rating", type="primary")