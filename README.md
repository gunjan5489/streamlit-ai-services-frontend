# AI Worker API Testing Suite

A comprehensive Streamlit-based testing frontend for the AI Worker FastAPI backend. This interactive web application provides an intuitive interface for testing and validating various AI worker API endpoints including tag resolution, translation, and image localization.

## 🚀 Features

- **Tags Resolve Multi**: Test multiple DOMX JSON documents with corresponding images
- **Tags Resolve Upload**: Test single DOMX JSON document with direct image upload
- **Translate Single**: Translate individual DOMX JSON files to target languages
- **Translate Multi**: Batch translate multiple files to multiple languages
- **Image Localization Pipeline**: Complete workflow for analyzing, suggesting, and generating localized images
- **Request History**: Track all API requests with timestamps and success metrics
- **Health Monitoring**: Real-time API health checks
- **Test Results Dashboard**: View and export comprehensive test results

## 📋 Prerequisites

### Local Development
- Python 3.11 or higher
- pip (Python package manager)

### Docker Deployment
- Docker 20.10 or higher
- Docker Compose 2.0 or higher

## 🔧 Installation

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-worker-testing-suite
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```env
API_BASE_URL=http://localhost:8000
TEST_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
streamlit run streamlit_app.py
```

The application will open automatically in your default browser at `http://localhost:8501`

### Docker Deployment

1. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API settings
```

2. **Build and start the container**
```bash
docker-compose up -d
```

3. **Access the application**
Open your browser to `http://localhost:8501`

4. **View logs**
```bash
docker-compose logs -f streamlit-frontend
```

5. **Stop the application**
```bash
docker-compose down
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Base URL of the FastAPI backend | `http://localhost:8000` |
| `TEST_API_KEY` | API key for authentication | `ws_test_YOUR_API_KEY` |

### Docker Configuration

The `docker-compose.yml` includes optional services that can be enabled:
- **PostgreSQL**: Database for storing results
- **Redis**: Caching layer
- **Nginx**: Reverse proxy for production

To enable optional services, uncomment the relevant sections in `docker-compose.yml`.

## 📖 Usage

### 1. Health Check
Use the sidebar to check API connectivity:
- Click **"Check API Health"** to verify the backend is responding

### 2. Tags Resolve Multi
Test multiple DOMX JSON files with images:
1. Navigate to the **"Tags Resolve Multi"** tab
2. Upload one or more JSON files
3. Upload corresponding images (optional) or provide S3/local paths
4. Click **"Execute Tags Resolve Multi"**

### 3. Tags Resolve Upload
Test single document processing:
1. Go to the **"Tags Resolve Upload"** tab
2. Upload a JSON file
3. Upload an image (optional)
4. Click **"Execute Tags Resolve Upload"**

### 4. Translate Single
Translate a single DOMX file:
1. Open the **"Translate Single"** tab
2. Select or enter target language
3. Upload JSON file
4. Click **"Execute Translation"**

### 5. Translate Multi
Batch translate to multiple languages:
1. Navigate to **"Translate Multi"** tab
2. Select target languages (multiple)
3. Upload multiple JSON files
4. Click **"Execute Multi Translation"**

### 6. Image Localization Pipeline
Run the complete localization workflow:
1. Go to **"Image Localization"** tab
2. Configure target locale and website context
3. Upload image or provide path
4. Enable auto-generate for AI-generated localized images
5. Click **"Run Localization Pipeline"**

### 7. Test Results
View comprehensive test results:
- Navigate to **"Test Results"** tab
- Review stored results from all tests
- Export results as JSON
- View performance metrics and charts

## 📁 Project Structure

```
.
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🔌 API Endpoints Tested

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/tags/resolve/multi` | POST | Resolve tags for multiple documents |
| `/v1/tags/resolve/upload` | POST | Resolve tags with direct upload |
| `/v1/translate` | POST | Translate single document |
| `/v1/translate/multi` | POST | Translate multiple documents |
| `/v1/image/full-localization-pipeline` | POST | Complete image localization |

## 🎨 Sample DOMX JSON Format

```json
{
  "nodes": {
    "node1": {
      "id": "node1",
      "text": "Welcome to our website",
      "type": "heading"
    },
    "node2": {
      "id": "node2",
      "text": "Click here to learn more",
      "type": "button"
    }
  }
}
```

## 🔍 Troubleshooting

### Application won't start
- Verify Python version: `python --version` (should be 3.11+)
- Check if port 8501 is available
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### API connection errors
- Verify `API_BASE_URL` in `.env` file
- Check if the FastAPI backend is running
- Validate `TEST_API_KEY` is correct

### Docker issues
- Ensure Docker daemon is running: `docker ps`
- Check container logs: `docker-compose logs streamlit-frontend`
- Rebuild container: `docker-compose up --build`

### File upload errors
- Verify file formats (JSON, PNG, JPG, etc.)
- Check file size limits
- Ensure proper file permissions

## 🐳 Docker Commands Reference

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f streamlit-frontend

# Restart service
docker-compose restart streamlit-frontend

# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up --build --force-recreate
```

## 📊 Performance Monitoring

The application tracks:
- Total requests count
- Success/failure rates
- Average response times
- Request history with timestamps
- Performance charts and visualizations

Access metrics in the **Test Results** tab.

## 🔒 Security Considerations

- Store API keys in `.env` file (never commit to version control)
- Use environment variables for sensitive configuration
- Run container as non-root user (configured in Dockerfile)
- Enable HTTPS in production (uncomment Nginx in docker-compose.yml)