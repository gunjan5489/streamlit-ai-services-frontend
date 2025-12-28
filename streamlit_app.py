import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import io
import base64
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_API_KEY = "" #os.getenv("TEST_API_KEY")

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
def setup_logging():
    """Setup daily rotating log file"""
    log_filename = LOGS_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"

    # Create logger
    logger = logging.getLogger("AIWorkerAPI")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with daily rotation
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logging()

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
def setup_logging():
    """Setup daily rotating log file"""
    log_filename = LOGS_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"

    # Create logger
    logger = logging.getLogger("AIWorkerAPI")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with daily rotation
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="AI Worker API Testing Suite",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Log application startup
logger.info("=" * 80)
logger.info("Application started")
logger.info(f"API Base URL: {API_BASE_URL}")
logger.info(f"API Key configured: {'Yes' if TEST_API_KEY else 'No'}")

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'request_history' not in st.session_state:
    st.session_state.request_history = []
    logger.info("Initialized request history")

if 'test_results' not in st.session_state:
    st.session_state.test_results = {}
    logger.info("Initialized test results")

if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = API_BASE_URL
    logger.info(f"Initialized API Base URL: {API_BASE_URL}")

if 'api_key' not in st.session_state:
    st.session_state.api_key = TEST_API_KEY
    logger.info("Initialized API Key from environment")

# Helper Functions
def make_api_request(endpoint: str, method: str = "POST", files: Any = None, data: Dict = None, headers: Dict = None) -> Dict:
    """Make API request with error handling and logging"""
    url = f"{st.session_state.api_base_url}{endpoint}"

    logger.info(f"Making API request: {method} {endpoint}")
    logger.debug(f"Full URL: {url}")

    if headers is None:
        headers = {}

    # Add API key to headers
    headers["X-API-Key"] = st.session_state.api_key
    logger.debug(f"API Key present: {'Yes' if st.session_state.api_key else 'No'}")

    try:
        start_time = datetime.now()

        if method == "POST":
            # Handle both dict and list formats for files
            if isinstance(files, list):
                logger.debug(f"Sending {len(files)} files as list")
                response = requests.post(url, files=files, data=data, headers=headers)
            else:
                logger.debug(f"Sending files as dict: {list(files.keys()) if files else 'None'}")
                response = requests.post(url, files=files, data=data, headers=headers)
        elif method == "GET":
            logger.debug(f"GET request with params: {data}")
            response = requests.get(url, params=data, headers=headers)
        else:
            logger.debug(f"Custom method {method}")
            response = requests.request(method, url, files=files, data=data, headers=headers)

        response.raise_for_status()
        elapsed_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Request successful: {endpoint} - Status: {response.status_code} - Time: {elapsed_time:.2f}s")

        # Log to history
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "response_time": elapsed_time,
            "success": True
        }
        st.session_state.request_history.append(log_entry)

        # Check if response is binary (image)
        content_type = response.headers.get('content-type', '')
        if 'image/' in content_type:
            logger.info(f"Received binary image response: {content_type}")
            return {
                "success": True,
                "data": response.content,
                "is_binary": True,
                "content_type": content_type,
                "status_code": response.status_code,
                "response_time": elapsed_time
            }
        else:
            # Try to parse as JSON
            try:
                response_data = response.json() if response.content else {}
                logger.debug(f"Parsed JSON response with keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'list'}")
            except json.JSONDecodeError:
                logger.warning("Response is not valid JSON, treating as text")
                response_data = response.text if response.content else ""

            return {
                "success": True,
                "data": response_data,
                "is_binary": False,
                "status_code": response.status_code,
                "response_time": elapsed_time
            }

    except requests.exceptions.RequestException as e:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        status_code = getattr(e.response, 'status_code', None)
        error_message = str(e)

        logger.error(f"❌ Request failed: {endpoint} - Status: {status_code} - Error: {error_message}")
        logger.error(f"Response time before failure: {elapsed_time:.2f}s")

        if hasattr(e.response, 'text'):
            logger.error(f"Error response body: {e.response.text[:500]}")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "error": error_message,
            "success": False
        }
        st.session_state.request_history.append(log_entry)

        return {
            "success": False,
            "error": error_message,
            "status_code": status_code,
            "response": getattr(e.response, 'text', None)
        }

def display_response(response: Dict):
    """Display API response in a formatted way"""
    if response["success"]:
        st.success(f"✅ Request successful (Status: {response['status_code']}, Time: {response['response_time']:.2f}s)")

        with st.expander("📊 Response Data", expanded=True):
            if isinstance(response["data"], dict):
                st.json(response["data"])
            elif isinstance(response["data"], list):
                st.json(response["data"])
            else:
                st.write(response["data"])
    else:
        st.error(f"❌ Request failed: {response.get('error', 'Unknown error')}")
        if response.get('response'):
            with st.expander("Error Details"):
                st.text(response['response'])

def create_sample_json():
    """Create a sample DOMX JSON for testing"""
    logger.info("Generated sample DOMX JSON")
    return {
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
            },
            "node3": {
                "id": "node3",
                "text": "Contact us at info@example.com",
                "type": "paragraph"
            }
        }
    }

# Main Application
st.title("🧪 AI Worker API Testing Suite")
st.markdown("### FastAPI Backend Testing Interface")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Settings
    api_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
    api_key = st.text_input("API Key", value=st.session_state.api_key if st.session_state.api_key else "", type="password")

    if st.button("Update Settings"):
        old_url = st.session_state.api_base_url
        old_key_present = bool(st.session_state.api_key)

        st.session_state.api_base_url = api_url
        st.session_state.api_key = api_key

        logger.info("=" * 60)
        logger.info("Settings updated by user")
        logger.info(f"API Base URL changed: {old_url} -> {api_url}")
        logger.info(f"API Key updated: {old_key_present} -> {bool(api_key)}")
        logger.info("=" * 60)

        st.success("✅ Settings updated and saved!")
        st.rerun()

    st.divider()

    # Test Health
    st.header("🏥 Health Check")
    if st.button("Check API Health"):
        logger.info("User initiated health check")
        response = make_api_request("/health", method="GET")
        if response["success"]:
            st.success("✅ API is healthy!")
            logger.info("Health check passed")
        else:
            st.error("❌ API is not responding")
            logger.warning("Health check failed")

    st.divider()

    # Request History
    st.header("📜 Request History")
    if st.session_state.request_history:
        df = pd.DataFrame(st.session_state.request_history)
        st.dataframe(df[['timestamp', 'endpoint', 'success']], use_container_width=True)

        if st.button("Clear History"):
            logger.info("User cleared request history")
            st.session_state.request_history = []
            st.rerun()
    else:
        st.info("No requests yet")

# Main Content - Tabs for different endpoints
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📄 Tags Resolve Multi",
    "📤 Tags Resolve Upload",
    "🌍 Translate Single",
    "🌍 Translate Multi",
    "🖼️ Image Localization",
    "📊 Test Results"
])

# Tab 1: Tags Resolve Multi
with tab1:
    st.header("Tags Resolve Multi Testing")
    st.markdown("Test multiple DOMX JSON documents with corresponding images")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("JSON Files")
        json_files = st.file_uploader(
            "Upload JSON files",
            type=['json'],
            accept_multiple_files=True,
            key="resolve_multi_json"
        )

        if st.button("Generate Sample JSON", key="gen_sample_multi"):
            sample_json = create_sample_json()
            st.download_button(
                "Download Sample JSON",
                data=json.dumps(sample_json, indent=2),
                file_name="sample_domx.json",
                mime="application/json"
            )

    with col2:
        st.subheader("Images")
        image_files = st.file_uploader(
            "Upload images (optional)",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            accept_multiple_files=True,
            key="resolve_multi_images"
        )

        image_paths = st.text_area(
            "Or provide S3/local paths (comma-separated)",
            placeholder="s3://bucket/image1.jpg, /path/to/image2.png"
        )

    if st.button("🚀 Execute Tags Resolve Multi", type="primary", key="exec_resolve_multi"):
        if json_files:
            logger.info(f"User initiated Tags Resolve Multi with {len(json_files)} JSON files and {len(image_files)} images")

            with st.spinner("Processing..."):
                # Prepare files as list of tuples for multiple files with same field name
                files_list = []

                # Add JSON files
                for json_file in json_files:
                    files_list.append(('json_files', (json_file.name, json_file.getvalue(), 'application/json')))
                    logger.debug(f"Added JSON file: {json_file.name}")

                # Add image files if any
                for img_file in image_files:
                    files_list.append(('images', (img_file.name, img_file.getvalue(), f'image/{img_file.type.split("/")[-1]}')))
                    logger.debug(f"Added image file: {img_file.name}")

                # Prepare data dict
                data_dict = {}
                if image_paths:
                    data_dict['image_paths'] = image_paths
                    logger.debug(f"Image paths provided: {image_paths}")

                response = make_api_request("/v1/tags/resolve/multi", files=files_list, data=data_dict)

                # Display response
                if response["success"]:
                    st.success(f"✅ Request successful (Status: {response['status_code']}, Time: {response['response_time']:.2f}s)")
                    logger.info(f"Tags Resolve Multi completed successfully with {len(response['data'])} results")

                    # Display results for each file
                    st.subheader("Results")
                    for idx, result in enumerate(response["data"]):
                        with st.expander(f"📄 {result.get('filename', f'File {idx}')}"):
                            if result.get('error'):
                                st.error(f"Error: {result['error']}")
                                logger.error(f"Error in result {idx}: {result['error']}")
                            else:
                                st.write(f"**Image Source:** {result.get('image_source', 'none')}")
                                st.write("**Result:**")
                                try:
                                    result_json = json.loads(result.get('result', '{}'))
                                    st.json(result_json)
                                except:
                                    st.text(result.get('result', 'No result'))

                    # Store results
                    st.session_state.test_results["resolve_multi"] = response["data"]
                    logger.info("Results stored in session state")
                else:
                    st.error(f"❌ Request failed: {response.get('error', 'Unknown error')}")
                    if response.get('response'):
                        with st.expander("Error Details"):
                            st.text(response['response'])
        else:
            st.warning("Please upload at least one JSON file")
            logger.warning("Tags Resolve Multi attempted without JSON files")

# Tab 2: Tags Resolve Upload
with tab2:
    st.header("Tags Resolve Upload Testing")
    st.markdown("Test single DOMX JSON document with direct image upload")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("JSON File")
        json_file = st.file_uploader(
            "Upload JSON file",
            type=['json'],
            key="resolve_upload_json"
        )

        if st.button("Generate Sample JSON", key="gen_sample_upload"):
            sample_json = create_sample_json()
            st.download_button(
                "Download Sample JSON",
                data=json.dumps(sample_json, indent=2),
                file_name="sample_domx.json",
                mime="application/json",
                key="download_sample_upload"
            )

    with col2:
        st.subheader("Image File")
        image_file = st.file_uploader(
            "Upload image (optional)",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            key="resolve_upload_image"
        )

        if image_file:
            st.image(image_file, caption="Uploaded Image", use_column_width=True)

    if st.button("🚀 Execute Tags Resolve Upload", type="primary", key="exec_resolve_upload"):
        if json_file:
            logger.info(f"User initiated Tags Resolve Upload with JSON: {json_file.name}")
            if image_file:
                logger.info(f"Image file included: {image_file.name}")

            with st.spinner("Processing..."):
                files_dict = {
                    'json_file': (json_file.name, json_file.getvalue(), 'application/json')
                }

                if image_file:
                    files_dict['image_file'] = (image_file.name, image_file.getvalue(), f'image/{image_file.type}')

                response = make_api_request("/v1/tags/resolve/upload", files=files_dict)
                display_response(response)

                # Store results
                if response["success"]:
                    st.session_state.test_results["resolve_upload"] = response["data"]
                    logger.info("Tags Resolve Upload completed successfully")
        else:
            st.warning("Please upload a JSON file")
            logger.warning("Tags Resolve Upload attempted without JSON file")

# Tab 3: Translate Single
with tab3:
    st.header("Translate Single Testing")
    st.markdown("Translate a single DOMX JSON file to a target language")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Settings")
        target_language = st.selectbox(
            "Target Language",
            ["Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese", "Korean", "Arabic", "Hindi"],
            key="translate_single_lang"
        )

        custom_language = st.text_input("Or enter custom language")

    with col2:
        st.subheader("JSON File")
        json_file = st.file_uploader(
            "Upload DOMX JSON file",
            type=['json'],
            key="translate_single_json"
        )

        if st.button("Generate Sample JSON", key="gen_sample_translate"):
            sample_json = create_sample_json()
            st.download_button(
                "Download Sample JSON",
                data=json.dumps(sample_json, indent=2),
                file_name="sample_domx.json",
                mime="application/json",
                key="download_sample_translate"
            )

    if st.button("🚀 Execute Translation", type="primary", key="exec_translate_single"):
        if json_file:
            target_lang = custom_language or target_language
            logger.info(f"User initiated single translation to {target_lang} with file: {json_file.name}")

            with st.spinner(f"Translating to {target_lang}..."):
                files_dict = {
                    'json_file': (json_file.name, json_file.getvalue(), 'application/json')
                }

                data_dict = {
                    'language': target_lang
                }

                response = make_api_request("/v1/translate", files=files_dict, data=data_dict)
                display_response(response)

                # Store and display translated nodes
                if response["success"] and "translated_json" in response["data"]:
                    st.session_state.test_results["translate_single"] = response["data"]
                    logger.info(f"Single translation to {target_lang} completed successfully")

                    st.subheader("Translated Nodes")
                    try:
                        translated_nodes = json.loads(response["data"]["translated_json"])
                        for node in translated_nodes:
                            st.write(f"**Node {node['id']}:** {node['text']}")
                    except:
                        st.json(response["data"]["translated_json"])
        else:
            st.warning("Please upload a JSON file")
            logger.warning("Single translation attempted without JSON file")

# Tab 4: Translate Multi
with tab4:
    st.header("Translate Multi Testing")
    st.markdown("Translate multiple DOMX JSON files to multiple languages")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Languages")
        selected_languages = st.multiselect(
            "Select Target Languages",
            ["Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese", "Korean", "Arabic", "Hindi"],
            default=["Spanish", "French"],
            key="translate_multi_langs"
        )

        custom_languages = st.text_input(
            "Additional languages (comma-separated)",
            placeholder="Dutch, Russian, Swedish"
        )

    with col2:
        st.subheader("JSON Files")
        json_files = st.file_uploader(
            "Upload DOMX JSON files",
            type=['json'],
            accept_multiple_files=True,
            key="translate_multi_json"
        )

    if st.button("🚀 Execute Multi Translation", type="primary", key="exec_translate_multi"):
        if json_files and (selected_languages or custom_languages):
            all_languages = selected_languages.copy()
            if custom_languages:
                all_languages.extend([lang.strip() for lang in custom_languages.split(',')])

            logger.info(f"User initiated multi translation: {len(json_files)} files to {len(all_languages)} languages")
            logger.info(f"Target languages: {', '.join(all_languages)}")

            with st.spinner(f"Translating {len(json_files)} files to {len(all_languages)} languages..."):
                files_list = []
                for json_file in json_files:
                    files_list.append(('json_files', (json_file.name, json_file.getvalue(), 'application/json')))
                    logger.debug(f"Added file for translation: {json_file.name}")

                data_dict = {
                    'languages': ','.join(all_languages)
                }

                response = make_api_request("/v1/translate/multi", files=files_list, data=data_dict)
                display_response(response)

                # Display results in a structured way
                if response["success"]:
                    st.session_state.test_results["translate_multi"] = response["data"]
                    logger.info(f"Multi translation completed successfully for {len(response['data'])} files")

                    st.subheader("Translation Results")
                    for filename, translations in response["data"].items():
                        with st.expander(f"📄 {filename}"):
                            if isinstance(translations, dict):
                                for lang, content in translations.items():
                                    st.write(f"**{lang}:**")
                                    if content.startswith("Error"):
                                        st.error(content)
                                        logger.error(f"Translation error for {filename} in {lang}: {content}")
                                    else:
                                        try:
                                            nodes = json.loads(content)
                                            for node in nodes[:3]:
                                                st.write(f"  - {node.get('text', 'N/A')[:100]}...")
                                        except:
                                            st.text(content[:500] + "..." if len(content) > 500 else content)
                            else:
                                st.error(translations)
        else:
            st.warning("Please upload JSON files and select at least one language")
            logger.warning("Multi translation attempted without proper inputs")

# Tab 5: Image Localization Pipeline
with tab5:
    st.header("Full Image Localization Pipeline")
    st.markdown("Complete pipeline: Analyze → Suggest → Generate localized image")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Localization Settings")
        target_locale = st.text_input(
            "Target Locale",
            value="Japanese market",
            placeholder="e.g., Japanese market, Spanish audience"
        )

        website_context = st.text_area(
            "Website Context",
            value="Professional B2B software company website",
            placeholder="Describe the website/brand context"
        )

        auto_generate = st.checkbox("Auto-generate localized image", value=True)

        if auto_generate:
            custom_prompt = st.text_area(
                "Custom Generation Prompt (optional)",
                placeholder="Leave empty to auto-generate prompt based on analysis"
            )

    with col2:
        st.subheader("Original Image")

        upload_method = st.radio("Image Source", ["Upload", "S3 Path", "Local Path"])

        original_image = None
        image_path = None

        if upload_method == "Upload":
            original_image = st.file_uploader(
                "Upload original image",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
                key="localize_image"
            )
            if original_image:
                st.image(original_image, caption="Original Image", use_column_width=True)

        elif upload_method == "S3 Path":
            image_path = st.text_input(
                "S3 Image Path",
                placeholder="s3://bucket-name/path/to/image.jpg"
            )

        else:
            image_path = st.text_input(
                "Local Image Path",
                placeholder="/path/to/local/image.jpg"
            )

    if st.button("🚀 Run Localization Pipeline", type="primary", key="exec_localization"):
        if (original_image or image_path) and target_locale and website_context:
            logger.info("User initiated image localization pipeline")
            logger.info(f"Target locale: {target_locale}")
            logger.info(f"Auto-generate: {auto_generate}")
            logger.info(f"Upload method: {upload_method}")

            with st.spinner("Running localization pipeline..."):
                files_dict = {}
                data_dict = {
                    'target_locale': target_locale.strip(),
                    'website_context': website_context.strip(),
                    'auto_generate': str(auto_generate).lower()
                }

                if original_image:
                    files_dict['original_image'] = (original_image.name, original_image.getvalue(), f'image/{original_image.type}')
                    logger.debug(f"Uploaded image: {original_image.name}")

                if image_path:
                    data_dict['original_image_path'] = image_path
                    logger.debug(f"Image path: {image_path}")

                if auto_generate and custom_prompt and custom_prompt.strip():
                    data_dict['custom_generation_prompt'] = custom_prompt
                    logger.debug("Custom generation prompt provided")

                response = make_api_request("/v1/image/full-localization-pipeline", files=files_dict, data=data_dict)

                if response["success"]:
                    st.session_state.test_results["localization"] = response
                    logger.info("Image localization pipeline completed successfully")

                    # Check if response is binary (image) or JSON
                    if response.get("is_binary", False):
                        st.success("✅ Localized image generated successfully!")
                        logger.info("Received generated localized image")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Original Image")
                            if original_image:
                                st.image(original_image, caption="Original", use_column_width=True)
                            elif image_path:
                                st.info(f"Original: {image_path}")

                        with col2:
                            st.subheader("Generated Localized Image")
                            st.image(response["data"], caption="Localized", use_column_width=True)

                        st.download_button(
                            "📥 Download Localized Image",
                            data=response["data"],
                            file_name=f"localized_{target_locale.replace(' ', '_').lower()}.png",
                            mime="image/png",
                            type="primary"
                        )
                    else:
                        # JSON response with analysis
                        if isinstance(response["data"], dict):
                            if "analysis" in response["data"]:
                                st.subheader("📊 Analysis Results")
                                analysis = response["data"]["analysis"]
                                logger.info(f"Analysis score: {analysis.get('overallSuitabilityScore', 'N/A')}/10")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Suitability Score", f"{analysis.get('overallSuitabilityScore', 'N/A')}/10")

                                with col2:
                                    st.metric("Problematic Elements", len(analysis.get('problematicElements', [])))

                                with st.expander("✅ Positive Elements"):
                                    for element in analysis.get('positiveElements', []):
                                        st.write(f"• {element}")

                                with st.expander("⚠️ Problematic Elements"):
                                    for element in analysis.get('problematicElements', []):
                                        st.write(f"**{element.get('element', 'N/A')}**")
                                        st.write(f"   🔍 Reason: {element.get('reason', 'N/A')}")
                                        st.write(f"   💡 Suggestion: {element.get('suggestedChange', 'N/A')}")
                                        st.divider()

                            if "suggestions" in response["data"]:
                                st.subheader("💡 Localization Suggestions")
                                st.info(response["data"]["suggestions"])

                            if "generated_image_available" in response["data"] and not response["data"]["generated_image_available"]:
                                error_msg = response['data'].get('generation_error', 'Unknown error')
                                st.warning(f"⚠️ Image generation was not successful: {error_msg}")
                                logger.warning(f"Image generation failed: {error_msg}")
                        else:
                            st.warning("Unexpected response format")
                            logger.warning("Unexpected response format received")
                            with st.expander("Raw Response"):
                                st.text(str(response["data"]))
                else:
                    st.error(f"❌ Pipeline failed: {response.get('error', 'Unknown error')}")
        else:
            st.warning("⚠️ Please provide an image and fill in all required fields")
            logger.warning("Image localization attempted with missing inputs")

# Tab 6: Test Results Summary
with tab6:
    st.header("📊 Test Results Summary")

    if st.session_state.test_results:
        st.subheader("Stored Test Results")

        for test_name, results in st.session_state.test_results.items():
            with st.expander(f"Test: {test_name}"):
                st.json(results)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export All Results"):
                all_results = json.dumps(st.session_state.test_results, indent=2)
                logger.info("User exported all test results")
                st.download_button(
                    "Download Results JSON",
                    data=all_results,
                    file_name=f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("Clear All Results"):
                logger.info("User cleared all test results")
                st.session_state.test_results = {}
                st.rerun()
    else:
        st.info("No test results yet. Run some tests to see results here.")

    # Request Statistics
    if st.session_state.request_history:
        st.subheader("Request Statistics")

        df = pd.DataFrame(st.session_state.request_history)

        col1, col2, col3 = st.columns(3)

        with col1:
            total_requests = len(df)
            st.metric("Total Requests", total_requests)

        with col2:
            success_rate = (df['success'].sum() / len(df) * 100) if len(df) > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")

        with col3:
            avg_response_time = df[df['success'] == True]['response_time'].mean() if df[df['success'] == True].shape[0] > 0 else 0
            st.metric("Avg Response Time", f"{avg_response_time:.2f}s")

        # Charts
        st.subheader("Performance Charts")

        # Response time over time
        if 'response_time' in df.columns:
            st.line_chart(df[df['success'] == True].set_index('timestamp')['response_time'])

        # Success/Failure distribution
        success_counts = df['success'].value_counts()
        st.bar_chart(success_counts)

        logger.info(f"Statistics displayed: {total_requests} total requests, {success_rate:.1f}% success rate")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    AI Worker API Testing Suite v1.0 | Built with Streamlit
</div>
""", unsafe_allow_html=True)

# Log application state on completion
logger.info(f"Session state - Request history: {len(st.session_state.request_history)} entries")
logger.info(f"Session state - Test results: {len(st.session_state.test_results)} tests stored")