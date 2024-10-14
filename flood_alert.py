import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to fetch weather data from OpenWeatherMap API
def get_weather_data(api_key, location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        # Extract relevant data
        weather_data = {
            'Location': location,
            'Temperature (°C)': data['main']['temp'],
            'Weather': data['weather'][0]['description'],
            'Humidity (%)': data['main']['humidity'],
            'Wind Speed (m/s)': data['wind']['speed']
        }

        return pd.DataFrame([weather_data])
    except requests.HTTPError as e:
        print(f"HTTPError: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except requests.RequestException as e:
        print(f"RequestException: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to determine flood risk based on weather data
def assess_flood_risk(weather_df):
    if weather_df.empty:
        return "No data available for flood risk assessment."

    temp = weather_df['Temperature (°C)'][0]
    humidity = weather_df['Humidity (%)'][0]
    weather_description = weather_df['Weather'][0].lower()

    # Define criteria for flood risk (example criteria)
    high_humidity_threshold = 80
    severe_weather_conditions = ['rain', 'storm', 'heavy rain']

    if humidity > high_humidity_threshold or any(condition in weather_description for condition in severe_weather_conditions):
        return "High risk of flooding."
    else:
        return "Low risk of flooding."

# Function to send email alert
def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Your API key for OpenWeatherMap
api_key = '5d3fe59c37028268ec4128675f17b998'

# Location to check
location = 'chengannur'

# Fetch weather data
df = get_weather_data(api_key, location)

# Assess flood risk
risk_assessment = assess_flood_risk(df)

# Prepare email content
email_subject = f"Daily Flood and Weather Update for {location}"
email_body = f"""
Weather data for {location}:
{df.to_string(index=False)}

Flood Risk Assessment:
{risk_assessment}
"""

# Email configuration
to_email = 'itsmevj001@gmail.com'  # Replace with the recipient's email address
from_email = 'vijayshankarvnair21@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # Use 587 for TLS
smtp_user = 'vijayshankarvnair21@gmail.com'
smtp_password = 'qeidvajvgqmsvfxr'  # Replace with your app password

# Send email alert
send_email(email_subject, email_body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)

# Save weather data to CSV
if not df.empty:
    df.to_csv(f"{location}_weather.csv", index=False)
