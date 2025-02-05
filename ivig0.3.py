import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def ivig_calculator(df, total_volume, start_time):
    try:
        current_time = datetime.strptime(start_time, "%H:%M")
        infused_volume = 0
        infusion_steps = []

        for index, row in df.iterrows():
            rate = row["Rate (mL/hr)"]
            duration = row["Duration (minutes)"]
            
            if infused_volume >= total_volume:
                break
            
            time_at_rate = timedelta(minutes=duration)
            volume_at_rate = (rate / 60) * duration  # Convert mL/hr to mL/min * duration
            
            if infused_volume + volume_at_rate > total_volume:
                time_needed = (total_volume - infused_volume) / (rate / 60)
                time_at_rate = timedelta(minutes=time_needed)
                volume_at_rate = total_volume - infused_volume
                
            infused_volume += volume_at_rate
            end_time = current_time + time_at_rate
            
            infusion_steps.append([rate, duration, current_time.strftime("%H:%M"), end_time.strftime("%H:%M"), round(volume_at_rate, 2), round(infused_volume, 2)])
            
            current_time = end_time  # Move to next step

        df = pd.DataFrame(infusion_steps, columns=["Rate (mL/hr)", "Duration (minutes)", "Start Time", "End Time", "Volume Infused (mL)", "Cumulative Volume (mL)"])
        return df
    
    except ValueError:
        return "Invalid time format. Use HH:MM (24-hour format)."

# Streamlit UI
st.title("IVIG Infusion Calculator")

start_time = st.text_input("Enter start time (HH:MM)", "14:00")
total_volume = st.number_input("Enter total volume (mL)", min_value=1, value=400)

st.subheader("Adjust Rate Schedule")

# Create an editable table
initial_data = {
    "Rate (mL/hr)": [30, 60, 90],
    "Duration (minutes)": [30, 30, 30]
}

df = pd.DataFrame(initial_data)
edited_df = st.data_editor(df, num_rows="dynamic")

# Automatically update table in real time
if not edited_df.empty:
    schedule = ivig_calculator(edited_df, total_volume, start_time)
    st.subheader("Infusion Schedule")
    st.dataframe(schedule)
