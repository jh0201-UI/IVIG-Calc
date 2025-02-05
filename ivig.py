import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def ivig_calculator(start_time, total_volume, rate_schedule):
    try:
        current_time = datetime.strptime(start_time, "%H:%M")
        infused_volume = 0
        infusion_steps = []

        for rate, duration in rate_schedule:
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
            
            infusion_steps.append([
                rate, current_time.strftime("%H:%M"), end_time.strftime("%H:%M"), round(volume_at_rate, 2), round(infused_volume, 2)
            ])
            
            current_time = end_time  # Move to next step

        df = pd.DataFrame(infusion_steps, columns=["Rate (mL/hr)", "Start Time", "End Time", "Volume Infused (mL)", "Cumulative Volume (mL)"])
        return df

    except ValueError:
        return "Invalid time format. Use HH:MM (24-hour format)."

# Streamlit UI
st.title("IVIG Infusion Calculator")

start_time = st.text_input("Enter start time (HH:MM)", "14:00")
total_volume = st.number_input("Enter total volume (mL)", min_value=1, value=400)

st.subheader("Enter Rate Schedule")
rate_schedule = []
rate_count = st.number_input("How many rate steps?", min_value=1, max_value=10, value=3)

for i in range(rate_count):
    rate = st.number_input(f"Rate {i+1} (mL/hr)", min_value=1, value=30, key=f"rate_{i}")
    duration = st.number_input(f"Duration {i+1} (minutes)", min_value=1, value=30, key=f"duration_{i}")
    rate_schedule.append((rate, duration))

if st.button("Calculate Infusion Schedule"):
    schedule = ivig_calculator(start_time, total_volume, rate_schedule)
    st.write(schedule)

