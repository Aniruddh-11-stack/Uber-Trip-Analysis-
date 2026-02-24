# 🚗 Uber Trip Analysis — NYC

> An end-to-end data science and Generative AI project analyzing Uber pickup patterns across New York City — featuring a premium Uber-style interactive dashboard, an AI agent, LSTM demand forecasting, and GenAI-powered insights.

---

## 🖥️ Dashboard Preview

> Black background · Uber green accents · Interactive NYC heatmap · AI chat interface

Run `streamlit run app.py` to launch the live dashboard.

---

## 📁 Repository Structure

```
Uber-Trip-Analysis/
│
├── Uber_Trip_Analysis.ipynb   # 10-section analysis notebook
├── app.py                      # Uber-style Streamlit dashboard
├── requirements.txt            # All dependencies
├── .env.example                # API key template
└── README.md
```

---

## 📓 Notebook — 10 Sections

| # | Section | What It Does |
|---|---------|-------------|
| 1 | **Imports & Setup** | Load all libraries |
| 2 | **Data Loading & Feature Engineering** | Parse timestamps, extract hour/weekday/month |
| 3 | **Exploratory Data Analysis** | Trips by hour, weekday, base; demand heatmap |
| 4 | **🗺️ NYC Zone Analysis** | GeoPandas + folium choropleth — which NYC neighborhood gets the most Uber trips? |
| 5 | **Rush Hour Classifier** | Random Forest — predict if a trip is during rush hour |
| 6 | **PCA Visualization** | Dimensionality reduction on trip features |
| 7 | **LSTM Demand Forecasting** | Keras LSTM predicts next-hour trip demand |
| 8 | **🤖 LangChain ReAct Agent** | NL querying of the dataset ("Which zone is busiest at 6PM?") |
| 9 | **🧠 GenAI Insight Summarizer** | Gemini/GPT-4 auto-generates an executive analyst report |
| 10 | **Streamlit Dashboard** | Launch the full Uber-style interactive app |

---

## 🖥️ Dashboard Pages

| Page | Features |
|------|---------|
| **🏠 Home** | KPI cards (Total Trips, Peak Hour, #1 Zone, Busiest Base) · NYC live heatmap · AI chat |
| **🗺️ Zone Analysis** | Interactive choropleth map · Time-of-day filter · Top neighborhoods ranking |
| **📊 EDA Dashboard** | Hourly/weekly charts · Demand heatmap · Base share |
| **🤖 AI Analyst** | Full LangChain-powered chat — ask questions in plain English |
| **🔮 Demand Forecast** | LSTM actual vs predicted curve · MAE, RMSE, Accuracy metrics |

---

## 🗃️ Dataset

**Uber Pickups in New York City** — FiveThirtyEight  
Columns: `Date/Time`, `Lat`, `Lon`, `Base`

Download: [Kaggle](https://www.kaggle.com/datasets/fivethirtyeight/uber-pickups-in-new-york-city)

Place CSVs in the project root:
```
uber-raw-data-apr14.csv
uber-raw-data-may14.csv
uber-raw-data-jun14.csv
```

> The app runs with **sample synthetic data** if no CSV is present — perfect for demos.

---

## 🛠️ Setup

### 1. Clone
```bash
git clone https://github.com/Aniruddh-11-stack/Uber-Trip-Analysis-.git
cd Uber-Trip-Analysis-
```

### 2. Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. API Keys (for LangChain + GenAI sections)
```bash
cp .env.example .env
```
Edit `.env`:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```

### 5. Run the Dashboard
```bash
streamlit run app.py
```

### 6. Open the Notebook
```bash
jupyter notebook Uber_Trip_Analysis.ipynb
```

---

## 🔑 API Keys Required

| Service | Used In | Where to Get |
|---------|---------|-------------|
| OpenAI | Section 8 (LangChain Agent) | [platform.openai.com](https://platform.openai.com/api-keys) |
| Google Gemini | Section 9 (GenAI Summarizer) | [console.cloud.google.com](https://console.cloud.google.com) |

> ⚠️ **Never hardcode API keys.** Always use `.env` and `python-dotenv`.

---

## 🏆 Why This Project Stands Out

| Dimension | Technology |
|-----------|-----------|
| **Geospatial Analysis** | GeoPandas, Folium choropleth — NYC neighborhood-level trip density |
| **Classical ML** | scikit-learn Random Forest rush hour classifier |
| **Deep Learning** | Keras LSTM time-series demand forecasting |
| **AI Agents** | LangChain ReAct agent for natural language data querying |
| **Generative AI** | LLM-powered executive summary auto-generation |
| **Premium UI** | Uber-style dark dashboard (Streamlit + Plotly + Folium) |

---

## 📄 License

Open-source under the [MIT License](LICENSE).
