# ⚡ TruthLens: Dynamic Fake News Detection System

**TruthLens** is a production-ready, real-time news verification platform designed for high accuracy and performance on low-resource systems. It leverages the latest AI technologies to bring transparency back to the digital world.

Unlike traditional detectors that rely on static datasets, TruthLens performs **Internet-Verified AI Analysis**. It fetches live information from the web to check the validity of breaking news stories and claims instantly.

---

## 🚀 Key Features

- **🌍 Real-time Web Verification**: Every analysis triggers a live search to cross-reference claims with trusted internet sources.
- **🧠 Gemini 3 Flash Engine**: Powered by Google's latest **Gemini 3 Flash** model for advanced claim extraction, source comparison, and high-speed reasoning.
- **🎨 Futuristic UI/UX**: A sleek "Glassmorphism" interface with neon accents, smooth animations, and a responsive result dashboard.
- **📊 Detailed Result Dashboard**:
  - **Verdict**: CLEAR (Real), FAKE, or MISLEADING.
  - **Confidence Meter**: Visual progress bar showing the AI's certainty.
  - **AI Reasoning**: Explains *why* a claim is flag as fake or real.
  - **Verified Sources**: Clickable links to the actual articles used for verification.
  - **Keyword Highlighting**: Automatically identifies and highlights suspicious words in the input.
- **📜 History Tracking**: Access previous analyses and download professional PDF reports.
- **⚡ Performance Optimized**: Uses multi-threaded scraping and lightweight processing to ensure zero lag on average hardware.

---

## 📸 Visual Overview

![Verification Result](https://raw.githubusercontent.com/user-attachments/assets/demo_screenshot.png)
*(Example analysis showing the TruthLens verdict and AI reasoning components)*

---

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, Flask, Waitress (Production Server)
- **AI/ML**: Google Gemini 3 Flash (via `google-genai` SDK)
- **Search**: DuckDuckGo Search (via `ddgs`)
- **Scraping**: BeautifulSoup4, Requests
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+)
- **Reporting**: ReportLab (PDF Generation)

---

## ⚙️ Installation & Setup

### 1. Requirements
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
```bash
pip install flask google-genai duckduckgo-search requests beautifulsoup4 reportlab waitress
```

### 3. API Configuration
1. Get a **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
2. Open `config.py` and replace the `GEMINI_API_KEY` with your key.
3. Ensure `ENABLE_DYNAMIC_VERIFICATION` is set to `True`.

### 4. Run the Application
```bash
python app.py
```
The system will be available at `http://127.0.0.1:5000`.

---

## 🧪 How to Use

1. **Navigate to Analyze**: Click the "Analyze" button on the navbar.
2. **Input News**: Paste a **URL** of a news article or directly type a **claim/text**.
3. **Verify**: Click "Verify Claim". The system will extract key claims, search the web, and summarize findings.
4. **View Result**: Analyze the verdict, confidence score, and check the verified sources.
5. **Download Report**: Use the "Download Report" button to save a PDF of the analysis.

---

## 🛠️ Troubleshooting

### 1. Quota Exceeded (429 Error)
If you see a "Quota exceeded" error, it means you've hit the Rate Limit of your Gemini API key. 
- **Solution**: Switch to the **Flash** model (already default) which has higher limits, or wait a few seconds before the next request.

### 2. Service Unavailable (503 Error)
Google's API may occasionally experience high demand.
- **Solution**: This is a temporary server-side issue. Please wait a minute and try your request again.

### 3. Server Not Updating
Waitress is a production server and does not auto-reload.
- **Solution**: If you change `config.py` or `verifier.py`, you **must** stop the `python app.py` process and start it again.

---

*TruthLens — Bringing Transparency back to the Digital World.*
