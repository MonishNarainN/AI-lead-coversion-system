# AI Lead Conversion System

An advanced full-stack AI-powered lead conversion and scoring system designed to help businesses prioritize and analyze their sales leads to maximize conversions.

## System Overview

The **AI Lead Conversion System** is built with a powerful machine learning backbone running on Python (Flask) and a modern, interactive frontend built with React (Vite). The system allows users to upload datasets (CSV or Excel) of sales leads, automatically diagnoses schema structure, cleans and preprocesses the data, runs an ensemble prediction model, and provides an actionable dashboard with rich insights and downloadable reports.

## Features

*   **Lead Scoring & Prediction:** Upload bulk lead datasets to get conversion probabilities and categorical decisions (Hot, Warm, Cold).
*   **Automated Data Processing:** The backend automatically identifies schema structure, handles missing values, and processes data using a dedicated ML preprocessing pipeline.
*   **Explainable AI (XAI):** See exactly *why* leads are scored the way they are using permutation feature importance and business recommendations generated dynamically based on dataset statistics.
*   **Insights Dashboard:** Visualize lead conversion rates, distributions, and feature importance directly from a React-based interactive dashboard built with Chart.js.
*   **Comprehensive Reporting:** Download standard predictions or rich analytical reports in multiple formats including CSV, Excel spreadsheet, plain text insights, and PDF.

## Tech Stack

### Frontend
*   **Framework:** React 18, built with Vite
*   **Styling:** Tailwind CSS (via `tailwind-merge` and `clsx`)
*   **Icons & Animation:** Lucide React, Framer Motion
*   **Visualization:** Chart.js with `react-chartjs-2`
*   **Routing:** React Router DOM

### Backend
*   **Framework:** Flask (Python)
*   **Machine Learning:** Scikit-Learn (Ensemble Models), Pandas for data manipulation
*   **Data Validation:** Custom validation, preprocessing, and schema detection services
*   **APIs & Integrations:** Custom configured REST API with CORS support

### Deployment & Infrastructure
*   **Containerization:** Docker & Docker Compose
*   **Reverse Proxy:** Nginx

## Getting Started

### Prerequisites
*   [Node.js](https://nodejs.org/) (v18+)
*   [Python](https://www.python.org/) 3.10+
*   [Docker](https://www.docker.com/) (Optional, for containerized deployment)

### Local Development Setup

#### 1. Backend Setup (Flask Server)
```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server (runs on port 5000 by default)
python app.py
```

#### 2. Frontend Setup (React App)
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the Vite development server (runs on port 5173 by default)
npm run dev
```

### Running with Docker

You can easily spin up the entire application stack using Docker Compose:

```bash
# Build and run the containers in detached mode
docker-compose up --build -d
```
This will start:
*   **Backend** on `http://localhost:5000`
*   **Frontend** on `http://localhost:5173` (internal Vite server)
*   **Nginx Reverse Proxy** on `http://localhost:80`

## API Endpoints Overview

*   `GET /health` : Returns system health status
*   `GET /metrics` : Returns application metrics and cached prediction count
*   `POST /upload` : Uploads dataset and detects schema
*   `POST /predict` : Runs ML pipeline on uploaded dataset and returns full insights & dataset
*   `POST /reports/download` : Generates and downloads reports (CSV, Excel, PDF, textual insights)

## License

This project is licensed under the MIT License.
