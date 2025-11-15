# 🌆 UrbanPULSE — AI-Driven Urban Forecasting Platform  
*A real-time city intelligence system built using Graph Neural Networks, geospatial visualization, and multi-factor urban simulation.*

---

## 🚀 Overview  
UrbanPhase is an AI-powered platform that predicts **traffic**, **air quality**, and **weather-driven effects** using a custom-built **Graph Neural Network (GNN)** pipeline.  
It provides planners and researchers with a real-time map interface to visualize current city conditions and simulate future scenarios.

Built end-to-end within a hackathon timeframe.

---

## 🧠 Key Features

### **1. GNN-Based Prediction Engine**
- Custom graph constructed from real city road networks  
- Node features extracted from satellite imagery  
- Multi-modal inputs: traffic → AQI → weather correlations  
- Predicts congestion, AQI levels, and environmental hotspots  

### **2. Interactive Urban Simulation Dashboard**
- Live geospatial dashboard powered by **MapLibre GL**  
- Toggle between Traffic, AQI, and Weather layers  
- Dynamic color gradients based on prediction severity  
- Timeline scrubber for future simulations  

### **3. FastAPI Backend**
- `/predict` → GNN inference endpoint  
- `/data/traffic` → real/processed data  
- `/data/aqi`  
- `/data/weather`  
- Clean modular router-based backend  

### **4. Modern Frontend (React + Vite)**
- Smooth map rendering  
- Metric panels & simulation controls  
- Layer switching without page reload  
- Clean, fast UI  

### **5. Scalable Architecture**
- Frontend & backend fully decoupled  
- Easy to swap datasets or add new ML models  
- Cloud deployment ready  

---

## 🏗️ Tech Stack

### **Frontend**
- React (Vite)
- MapLibre GL JS  
- TailwindCSS  
- Axios  

### **Backend**
- FastAPI  
- Python 3.10+  
- Uvicorn  

### **Machine Learning**
- PyTorch  
- PyTorch Geometric  
- Numpy / Pandas  
- Satellite image feature extraction  

---

## 📁 Project Structure

```bash
UrbanPhase/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── gnn_predict.py
│   │   └── data_routes.py
│   ├── gnn_pipeline/
│   │   ├── model.py
│   │   ├── inference.py
│   │   └── image_features.py
│   └── utils/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── MapView.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── architecture_diagram.png
│   ├── demo_screenshots/
│   └── presentation.pdf
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 🔧 1. Clone the Repository
```bash
git clone https://github.com/PranayGupta987/UrbanPhase.git
cd UrbanPhase
```

---

# 🟦 Backend Setup (FastAPI)

### 1. Create and Activate Virtual Environment
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate      # Mac/Linux
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the Backend
```bash
uvicorn main:app --reload
```

Backend runs at:  
👉 **http://localhost:8000**

---

# 🟩 Frontend Setup (React)

### Install dependencies
```bash
cd frontend
npm install
```

### Run development server
```bash
npm run dev
```

Frontend runs at:  
👉 **http://localhost:5173**

---

## 🔥 API Endpoints

### 🎯 GNN Prediction
```http
GET /predict
```
**Returns:** Predicted traffic & AQI for next snapshots.

### 📊 Data Endpoints
```http
GET /data/traffic
GET /data/aqi
GET /data/weather
```

Used by the frontend to populate map layers.

---

## 🧩 How It Works — System Flow

1. **Graph Construction**  
   Each road segment becomes a node; edges represent connected paths.

2. **Feature Extraction**  
   - Satellite imagery  
   - Historical traffic data  
   - AQI patterns  
   - Weather parameters  

3. **GNN Inference**  
   The model predicts future congestion & AQI hotspots.

4. **Backend Serving**  
   FastAPI packages predictions into JSON endpoints.

5. **Frontend Visualization**  
   MapLibre reads the data and renders interactive layers.

---

## 📌 Future Enhancements

- 📍 Multi-city graph support  
- 🔁 LSTM-GNN hybrid for better temporal modeling  
- 🌧️ Extreme weather simulation (rainfall, heatwaves)  
- 🛰️ Integrate real-time APIs (OpenWeather, AQI India)  
- 📱 Mobile dashboard  
- ☁️ Docker + cloud deployment (Render / AWS / DigitalOcean)  

---

## 🧑‍💻 Team
- **Pranay Gupta** 
- **AYUSH**
- **ANIMESH**
- **AVNI MAHAJAN**
- **DIVANSHI**

---

## ⭐ Support the Project
If you like this project, consider giving it a **⭐ star** on GitHub — it helps visibility and motivates the team!

---
