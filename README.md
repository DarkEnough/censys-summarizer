# 🔍 Censys Data Summarization Agent

An AI-powered full-stack application that generates intelligent summaries of Censys host data using either Groq's Llama 3.1 or HuggingFace's BART model.

## 🌐 Live Demo

**Try it now:** [https://censys-summarizer.vercel.app](https://censys-summarizer.vercel.app)

- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Render
- **Note**: The cloud demo only includes Groq API summaries (Llama 3.1 8B). HuggingFace BART summaries are disabled in production due to model size constraints (~1.6GB). For full local functionality with both AI models, follow the installation instructions below.

## 🌟 Features

- **Dual AI Summarization**: Choose between Groq (cloud-based) or HuggingFace (local) models
- **Batch Processing**: Summarize multiple hosts in a single request
- **Interactive UI**: Clean, modern interface for uploading and viewing summaries
- **Sample Data**: Pre-loaded sample hosts for quick testing
- **RESTful API**: FastAPI backend with clear endpoints
- **Extensible Architecture**: Easy to add new summarization models

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (optional, for serving frontend)
- Groq API key (optional, for Groq summarizer)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/DarkEnough/censys-summarizer.git
cd censys-summarizer
```

2. **Set up the backend**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional for Groq)
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

3. **Run the backend**:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

4. **Open the frontend**:
**Important**: Serve the frontend with a local server (don't open the HTML file directly):
```bash
# Using Python (recommended)
cd frontend
python3 -m http.server 3000

# Then open: http://localhost:3000
```

**Note**: Opening `index.html` directly in the browser won't work due to environment detection requirements.

## 📊 Using the Application

### Web Interface

1. Navigate to the frontend in your browser
2. Choose your summarizer (Groq or HuggingFace)
3. Either:
   - Upload a JSON file with host data
   - Click "Load hosts_dataset" to use the real Censys interview data
4. Click "Generate Summaries"
5. View the AI-generated summaries with expandable details

### API Endpoints

- **GET `/health`**: Health check
  ```bash
  curl http://localhost:8000/health
  ```

- **POST `/batch_summarize`**: Summarize hosts
  ```bash
  curl -X POST http://localhost:8000/batch_summarize \
    -H "Content-Type: application/json" \
    -d '{
      "hosts": [{"ip": "192.168.1.1", "services": [...]}],
      "summarizer": "groq"
    }'
  ```

- **POST `/upload_dataset`**: Upload JSON file
  ```bash
  curl -X POST http://localhost:8000/upload_dataset \
    -F "file=@data/sample_hosts.json" \
    -F "summarizer=huggingface"
  ```

## 🧪 Testing

Run the test suite:
```bash
cd tests
python test_summarizer.py

# Or using pytest
pytest test_summarizer.py -v
```

## 📁 Project Structure

```
censys-summarizer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── summarizer_groq.py   # Groq API integration
│   ├── summarizer_hf.py     # HuggingFace local model
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Web interface
│   └── styles.css           # Styling
├── data/
│   └── sample_hosts.json    # Sample Censys data
├── tests/
│   └── test_summarizer.py   # Unit tests
├── .env.example             # Environment template
└── README.md
```

## 🔧 Configuration

### Groq API Setup (Optional)

1. Get an API key from [Groq Console](https://console.groq.com/keys)
2. Add it to your `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

### HuggingFace Model

The HuggingFace summarizer uses the BART model locally. First run will download the model (~1.6GB).

## 🎯 AI Techniques & Prompt Engineering

### Prompt Engineering Strategy

1. **Role-Based Context**: Each prompt begins with establishing the AI as a "cybersecurity analyst" to prime domain-specific responses.

2. **Structured Output Requirements**: The prompt explicitly lists 5 key areas to cover:
   - Identifying information
   - Services and ports
   - Software versions
   - Security observations
   - Notable configurations

3. **Conciseness Constraint**: "2-3 sentences" requirement ensures actionable summaries without overwhelming detail.

4. **Temperature Tuning**: Groq uses `temperature=0.3` for consistent, factual outputs rather than creative variations.

### Model Selection Rationale

- **Groq (Llama 3.1 8B)**: Fast inference, good at technical content, cost-effective
- **HuggingFace (BART)**: Local processing, no API costs, good for privacy-sensitive data

## 🚀 Future Enhancements

If given more time, here's what I would add:

### 1. Advanced Features
- **Vulnerability Detection**: Integrate with CVE databases to highlight known vulnerabilities
- **Risk Scoring**: Implement a risk assessment algorithm based on open ports, outdated software, and CVEs
- **Comparative Analysis**: Compare multiple hosts to identify patterns and anomalies
- **Export Functionality**: Generate PDF/CSV reports of summaries

### 2. Technical Improvements
- **Caching Layer**: Redis cache for repeated summarizations
- **Async Processing**: Background job queue for large batch operations
- **WebSocket Support**: Real-time progress updates for batch processing
- **Rate Limiting**: Protect API endpoints from abuse
- **Authentication**: JWT-based auth for production deployment

### 3. AI Enhancements
- **Fine-tuned Models**: Train custom models on Censys-specific data
- **Multi-Model Ensemble**: Combine outputs from multiple models for better accuracy
- **Confidence Scoring**: Add certainty metrics to summaries
- **Custom Prompts**: User-configurable prompt templates
- **RAG Integration**: Use vector databases to provide context from historical scans

### 4. UI/UX Improvements
- **React/Vue Frontend**: Modern SPA with state management
- **Data Visualization**: D3.js charts for service distribution, geographic mapping
- **Filtering & Search**: Advanced filtering by IP range, services, vulnerabilities
- **Dark Mode**: Theme toggling for better accessibility
- **Bulk Actions**: Select multiple hosts for batch operations

### 5. DevOps & Monitoring
- **Docker Containerization**: Multi-stage Dockerfile for easy deployment
- **Kubernetes Manifests**: Helm charts for scalable deployment
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Structured logging with ELK stack integration

### 6. Data Processing
- **Stream Processing**: Handle real-time Censys data streams
- **Data Normalization**: Standardize various input formats
- **Incremental Updates**: Track changes in host configurations over time
- **ML-based Clustering**: Group similar hosts automatically

## 🤝 Assumptions Made

1. **Input Format**: Host data follows Censys JSON structure with common fields (ip, services, etc.)
2. **Model Availability**: Users have internet for Groq or sufficient resources for local BART
3. **Browser Compatibility**: Modern browser with JavaScript enabled
4. **Python Environment**: Python 3.8+ with pip available
5. **CORS**: Enabled for all origins in development (should be restricted in production)

## 📝 Notes

- The Groq summarizer requires an API key (free tier available)
- HuggingFace model downloads on first use (~1.6GB)
- Sample data includes realistic Censys-style host information
- Frontend uses vanilla JavaScript for simplicity (no build step required)

## 🐛 Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**: 
   - Create `.env` file from `.env.example`
   - Add your Groq API key

2. **"Cannot connect to API"**:
   - Ensure backend is running on port 8000
   - Check CORS settings if accessing from different origin

3. **HuggingFace model download fails**:
   - Check internet connection
   - Ensure sufficient disk space (~2GB)
   - Try manually downloading: `python -c "from transformers import pipeline; pipeline('summarization', model='facebook/bart-large-cnn')"`

4. **Frontend not loading**:
   - Open browser console for errors
   - Ensure backend is running
   - Check browser allows local file access

## 📄 License

This project is created as part of a technical assessment for Censys.

---

Built with ❤️ for the Censys 2026 Summer Internship
