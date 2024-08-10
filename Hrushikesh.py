import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import datetime

# Initialize the Geolocator
geolocator = Nominatim(user_agent="shop_locator")

# Sample Data: Replace this with your API or database call
shops_data = {
    "Shop Name": ["Daily Mart", "Quick Shop", "Night Store", "Express Mart"],
    "Latitude": [37.7749, 37.7849, 37.7649, 37.7749],
    "Longitude": [-122.4194, -122.4094, -122.4294, -122.4394],
    "Products": [["Milk", "Bread", "Eggs"], ["Milk", "Bread"], ["Bread", "Snacks"], ["Milk", "Eggs"]],
    "Open Time": ["08:00", "09:00", "10:00", "06:00"],
    "Close Time": ["22:00", "21:00", "23:59", "20:00"],
    "Price Range": [1, 2, 3, 2]
}

shops_df = pd.DataFrame(shops_data)

# Streamlit App
st.title("Nearby Open Shops Locator")

# User Inputs
location = st.text_input("Enter your location (City, Address, etc.)", "")
product = st.text_input("Enter the product you're looking for", "")
price_range = st.slider("Select your price range", 1, 3, 2)
current_time = st.time_input("Current Time", datetime.datetime.now().time())

if location:
    # Convert location to coordinates
    location = geolocator.geocode(location)
    user_coords = (location.latitude, location.longitude)
    
    def is_shop_open(open_time, close_time, current_time):
        open_time = datetime.datetime.strptime(open_time, "%H:%M").time()
        close_time = datetime.datetime.strptime(close_time, "%H:%M").time()
        return open_time <= current_time <= close_time

    # Filter Shops
    shops_df['Distance'] = shops_df.apply(lambda x: geodesic(user_coords, (x['Latitude'], x['Longitude'])).km, axis=1)
    filtered_shops = shops_df[
        (shops_df['Products'].apply(lambda x: product in x)) &
        (shops_df['Price Range'] <= price_range) &
        (shops_df.apply(lambda x: is_shop_open(x['Open Time'], x['Close Time'], current_time), axis=1))
    ]
    
    # Display Results
    if not filtered_shops.empty:
        for i, row in filtered_shops.iterrows():
            st.write(f"**{row['Shop Name']}** - {row['Distance']:.2f} km away")
            st.write(f"Products: {', '.join(row['Products'])}")
            st.write(f"Price Range: {row['Price Range']}")
            st.write("---")
    else:
        st.write("No shops found that match your criteria.")
