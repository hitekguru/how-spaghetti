import streamlit as st
import pandas as pd
import altair as alt
from streamlit_gsheets import GSheetsConnection

# 1. PAGE SETUP
st.set_page_config(page_title="How Spaghetti?", page_icon="🍝", layout="wide")

col_header, col_logo = st.columns([4, 1])
with col_header:
    st.title("🍝 How Spaghetti?")
    st.caption("The definitive taxonomy of the Western genre.")

# 2. CONNECT TO GOOGLE SHEETS
# This looks for the secrets you just pasted!
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60) # Refresh data every 60 seconds
def load_data():
    try:
        df = conn.read()
        return df
    except Exception as e:
        return None

df = load_data()

# Error Handling if connection fails
if df is None:
    st.error("⚠️ Connection Error: Could not read Google Sheet.")
    st.info("Did you share the Sheet with the 'client_email' found in your secrets?")
    st.stop()

# Ensure critical columns exist (in case you started with a blank sheet)
if "Vote_Count" not in df.columns:
    df["Vote_Count"] = 0
if "Sum_Spaghetti" not in df.columns:
    df["Sum_Spaghetti"] = df["Spaghetti_Intensity"]

# 3. THE "SPAGHETTI PLOT"
st.subheader("The Sauce Spectrum")
blob_chart = alt.Chart(df).mark_circle().encode(
    x=alt.X('Year', scale=alt.Scale(domain=[1950, 2025]), title='Release Year'),
    y=alt.Y('Spaghetti_Intensity', scale=alt.Scale(domain=[0, 5]), title='Spaghetti-ness (0-5)'),
    size=alt.Size('Avg_Rating', legend=None, scale=alt.Scale(range=[100, 500])),
    color=alt.Color('Type', legend=alt.Legend(title="Sub-Genre")),
    tooltip=['Title', 'Year', 'Spaghetti_Intensity', 'Avg_Rating']
).properties(height=350).interactive()

st.altair_chart(blob_chart, use_container_width=True)

# 4. THE DATA DIRECTORY
st.subheader("Movie Directory")
event = st.dataframe(
    df,
    column_config={
        "Poster_URL": st.column_config.ImageColumn("Art", width="small"),
        "Title": st.column_config.TextColumn("Title", width="medium"),
        "Spaghetti_Intensity": st.column_config.ProgressColumn("How Spaghetti?", format="%.1f 🍝", min_value=0, max_value=5),
        "Remaster_Avail": st.column_config.CheckboxColumn("Restored?", disabled=True),
        "Avg_Rating": st.column_config.NumberColumn("Enjoyment", format="%.1f ⭐"),
    },
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

# 5. THE REVIEW FORM (Writes to Google Sheet)
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    movie = df.iloc[selected_index]
    
    st.divider()
    c1, c3 = st.columns([1, 2])
    
    with c1:
        st.image(movie["Poster_URL"], caption=f"{movie['Year']}")
    
    with c3:
        st.markdown(f"### Rate: *{movie['Title']}*")
        
        with st.form("rating_form"):
            user_spag = st.slider("Your Spaghetti Score", 0.0, 5.0, 2.5)
            # We don't save enjoyment yet to keep it simple, but we display the slider
            user_rate = st.slider("Your Enjoyment", 1.0, 5.0, 3.0) 
            submitted = st.form_submit_button("Submit Rating")
            
            if submitted:
                # Calculate new average
                current_votes = float(movie.get("Vote_Count", 0))
                current_sum = float(movie.get("Sum_Spaghetti", 0))
                
                new_votes = current_votes + 1
                new_sum = current_sum + user_spag
                new_avg = new_sum / new_votes
                
                # Update the data
                df.at[selected_index, "Vote_Count"] = new_votes
                df.at[selected_index, "Sum_Spaghetti"] = new_sum
                df.at[selected_index, "Spaghetti_Intensity"] = new_avg
                
                # Push to Google Sheet
                conn.update(data=df)
                st.success(f"✅ Rated! The Spaghetti Score is now {new_avg:.1f}")
                st.cache_data.clear() # Force reload
                st.rerun()
