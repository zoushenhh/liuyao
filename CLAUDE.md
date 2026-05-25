# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese I Ching (周易) divination application called "坚六爻" (Jian Liu Yao), implementing traditional Chinese fortune-telling methods including:

- **大衍筮法** (Dayan Stalk Divination) - Traditional yarrow stalk divination method
- **纳甲筮法** (Najia Divination) - Six-line divination with Ganzhi (heavenly stems and earthly branches)
- **AI-powered interpretations** - Modern LLM integration for divination readings

## Core Architecture

### Application Structure
- **Streamlit Web App** (`app.py`) - Main web interface with traditional Chinese styling
- **AI Module** (`ai_module.py`) - OpenAI-compatible API integration for intelligent interpretations
- **IChing Library** (`ichingshifa/`) - Core divination logic and data structures

### Key Components

#### Core Library (`ichingshifa/`)
- `ichingshifa.py` - Main `Iching` class implementing divination algorithms
- `data.pkl` - Serialized data containing 64 hexagrams, 4096 line combinations, and traditional Chinese metaphysics data
- `d.py` - Calendar and astronomical calculations
- `jieqi.py` - Solar terms calculations for Chinese calendar

#### AI Integration (`ai_module.py`)
- Manages AI settings and configuration (`ai_settings.json`)
- Provides structured prompts for professional I Ching interpretation
- Handles OpenAI-compatible API calls with retry logic and error handling
- Includes professional divination analysis framework

#### Web Interface (`app.py`)
- Two-column layout: traditional divination results + AI interpretation
- Manual line selection (硬币/coin method) with visual yao symbols
- Real-time divination based on date/time inputs
- Customizable AI settings sidebar

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Running the Application
```bash
# Local development
streamlit run app.py

# With custom port and address (for servers)
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Dependencies
- `streamlit` - Web application framework
- `openai` - AI API integration
- `pendulum` - Date/time handling
- `sxtwl` - Chinese calendar calculations
- `ephem` - Astronomical calculations
- `cn2an` - Chinese number conversion
- `bidict` - Bidirectional dictionaries
- `numpy` - Numerical computations

## Key Configuration Files

### AI Settings (`ai_settings.json`)
- API endpoint configuration (supports custom OpenAI-compatible endpoints)
- Model selection and parameters
- Professional divination prompts and templates
- Retry and timeout settings

### Dependencies (`requirements.txt`)
All required Python packages are listed here. The project requires Python 3.7+.

## Development Notes

### Data Dependencies
- The `ichingshifa/data.pkl` file is critical and contains all traditional I Ching data
- Do not modify or move this file - the library depends on it being in the same directory

### Chinese Character Handling
- The application uses UTF-8 encoding throughout
- All text input/output should handle Chinese characters properly
- Traditional and simplified Chinese character conversion is supported

### AI Integration Architecture
The AI module follows a structured approach:
1. **Role Definition**: Professional I Ching master persona
2. **Analysis Framework**: Step-by-step traditional analysis method
3. **Output Format**: Structured markdown with specific sections
4. **Error Handling**: Comprehensive retry logic and user-friendly error messages

### Styling and UI
- Custom CSS with traditional Chinese aesthetic (宣纸 paper colors, 朱砂 red buttons)
- Responsive design for mobile and desktop
- Traditional Chinese fonts and visual elements

### Testing
No formal test suite is currently implemented. The application can be tested by:
1. Running the Streamlit app locally
2. Testing various divination scenarios
3. Verifying AI integration with different API endpoints

### Deployment
- **Production**: Streamlit Cloud at `9bvk9s8k8kudakw9vqdcf4.streamlit.app`
- **GitHub**: `zoushenhh/liuyao` (public, auto-deploys to Streamlit Cloud on push)
- `.streamlit/config.toml` is tracked in git for theme deployment
- `ai_settings.json` is gitignored; API keys stored in browser localStorage
- Avoid `st_capture`/`redirect_stdout` for display; use `st.code()` directly
- Python 3.14 requires relaxed version pins (ephem>=4.2, sxtwl==2.0.6)
- Do not nest `st.expander` inside `st.expander` (breaks on Streamlit >=1.39)

## API Integration Notes

- The AI module supports any OpenAI-compatible API endpoint
- Configuration is done through the web interface sidebar
- The system prompts are specifically designed for professional I Ching analysis
- Error handling includes network timeouts, authentication failures, and rate limiting