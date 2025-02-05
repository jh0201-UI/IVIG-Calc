import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def ivig_calculator(df):
    try:
        infusion_steps = []
        current_time = datetime.strptime(df["Start Time"].iloc[0], "%H:%M")
        remaining_volume = df["Volume Remaining (mL)"].iloc[0]

        for index, row in df.iterrows():
            try:
                rate = float(row["Rate (mL/hr)"])
                duration = float(row["Duration (minutes)"])
            except ValueError:
                continue  # Skip invalid rows without throwing errors
            
            if remaining_volume <= 0:
                break
            
            time_at_rate = timedelta(minutes=duration)
            volume_at_rate = (rate / 60) * duration  # Convert mL/hr to mL/min * duration
            
            if volume_at_rate > remaining_volume:
                time_needed = (remaining_volume / (rate / 60))
                time_at_rate = timedelta(minutes=time_needed)
                volume_at_rate = remaining_volume
            
            remaining_volume -= volume_at_rate
            end_time = current_time + time_at_rate
            
            infusion_steps.append([current_time.strftime("%H:%M"), rate, duration, end_time.strftime("%H:%M"), round(volume_at_rate, 2), round(remaining_volume, 2)])
            
            current_time = end_time  # Move to next step

        df = pd.DataFrame(infusion_steps, columns=["Start Time", "Rate (mL/hr)", "Duration (minutes)", "End Time", "Volume Infused (mL)", "Volume Remaining (mL)"])
        return df[df.notna().all(axis=1)]  # Show only rows with data
    
    except ValueError:
        return "Invalid time format. Use HH:MM (24-hour format)."

# Streamlit UI
st.title("Heme/Onc Clinic Infusion Calculator")

st.subheader("Infusion Schedule")

# Create an editable table with four initial steps
initial_data = {
    "Start Time": ["14:00", "14:30", "15:00", "15:30"],
    "Rate (mL/hr)": [30, 60, 90, 120],
    "Duration (minutes)": [30, 30, 30, 30],
    "Volume Remaining (mL)": [400, 400, 400, 400]
}

df = pd.DataFrame(initial_data)
edited_df = st.data_editor(df, num_rows="dynamic", height=400)

# Filter out empty and inactive rows
edited_df = edited_df.dropna(how="all")
edited_df = edited_df[edited_df.notna().all(axis=1)]

# Automatically update table in real time
if not edited_df.empty:
    schedule = ivig_calculator(edited_df)
    st.data_editor(schedule, num_rows="dynamic", height=400)
