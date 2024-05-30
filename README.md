# Dublin Bikes Web Application

An intuitive web application for finding and using Dublin Bikes, integrating real-time bike availability and weather information. 
The app leverages scraped data to provide both historical availability and predictive analytics for future bike availability.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Contributors](#contributors)

## Overview

![journeyPlanner](https://github.com/Conor-O-Mahony/DublinBikes/assets/98984802/84b4378c-7a72-4c22-b70f-f04aaaa2b461)

This project provides an interface to check Dublin Bikes availability, weather conditions, and plan routes. It leverages data from JCDecaux and OpenWeather APIs.

## Features

![Availability](https://github.com/Conor-O-Mahony/DublinBikes/assets/98984802/d325d6f8-5be5-40bd-9c54-fd50c22c0651)

- **Interactive Map**: Shows all bike stations information with color-coded availability.
- **Journey Planner**: Calculates the best routes including walking and cycling segments.
- **Historical and Predictive Data**: Displays plots for bike availability based on historical and predicted data using models created upon months of availability and weather data scraping.
- **Weather Forecast**: Provides current and future weather conditions.

## Architecture

![Overall Architecture](https://github.com/Conor-O-Mahony/DublinBikes/assets/98984802/24e6101e-7d86-49a4-8398-0b97dda5e264)

- **Flask EC2 Instance**: Hosts the web application.
  - Backend: Python Flask framework. Handles HTTP requests, API interactions, and data processing.
  - Frontend: Provides the user interface using HTML, CSS, and JavaScript.
- **Scrapers EC2 Instance**: Automates data collection from JCDecaux and OpenWeather APIs.
- **RDS Instance**: Stores all data related to bike availability and weather conditions.

## Getting Started

### Prerequisites

- Python 3.x
- MySQL
- JCDecaux and OpenWeather API keys
- AWS account for EC2 and RDS setup

### Installation

1. Clone the repository:
    ```bash
    git clone repo link>
    cd DublinBikes
    ```
2. Set up a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure environment variables in a `.env` file:
    ```
    JCDECAUX_API_KEY=<your_jcdecaux_api_key>
    OPENWEATHER_API_KEY=<your_openweather_api_key>
    DATABASE_URL=mysql+pymysql://<username>:<password>@<host>/<database>
    ```

5. Set up your own EC2 instances for scraping data and populate your database with bike and weather data.

6. Run the Flask application:
    ```bash
    flask run
    ```
7. Access the application at `http://127.0.0.1:5000`.

## Contributors

- Eneko O'Kelly
- Conor O'Mahony
- Dillon Hennessy
