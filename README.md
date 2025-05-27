# Global Market Bot ADK

A comprehensive financial analysis and recommendation system built using Google's Agent Development Kit (ADK).

## Project Demo

[![Watch the video](https://img.youtube.com/vi/EwlJXowPYgI/0.jpg)](https://www.youtube.com/embed/EwlJXowPYgI)

## Project Structure

```
src/
├── sub_agent/
│   └── research/
│       ├── analysis_team/
│       │   ├── fundamental_agent.py      # Fundamental analysis of stocks
│       │   ├── technical_agent.py        # Technical analysis and indicators
│       │   ├── sentiment_agent.py        # Market sentiment analysis
│       │   └── risk_analysis_agent.py    # Risk assessment and metrics
│       ├── recommendation_team/
│       │   └── equity_product_recommendation_agent.py  # Stock recommendations
│       ├── writing_team/
│       │   └── writing_agents.py         # Report generation and review
│       ├── search_team/                  # Market research and data collection
│       ├── utils/
│       │   └── file_utils.py            # File handling utilities
│       └── prompts.py                    # Centralized agent instructions
├── utils/
│   └── pdf_generator.py                 # PDF report generation
├── agents_sample_reports/                # Example analysis reports
├── apps/                                # Application scripts
│   └── agent.py                         # Sample agent that creates report for a single stock leveraging the sub agents
└── archived/                           # Archived code and resources
```

## Features

### Analysis Team
- **Fundamental Analysis**: Financial statements, ratios, and growth metrics
- **Technical Analysis**: Price action, trends, and technical indicators
- **Sentiment Analysis**: News sentiment, analyst recommendations, and market sentiment
- **Risk Analysis**: Volatility, financial risk, and market risk assessment

### Recommendation Team
- Equity product recommendations (buy, sell, hold)
- Focus on delta one products (stocks, ADRs)

### Writing Team
- Report generation with executive summaries
- Multi-stage review process
- PDF report generation
- Professional formatting and structure

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/joycel-github/finance-agent-adk.git
cd finance-agent-adk
```

2. Set up the virtual environment:
```bash
python -m venv global_market_bot_env
source global_market_bot_env/bin/activate  # On Windows: global_market_bot_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   You can get your Gemini API key from the [Google AI Studio](https://makersuite.google.com/app/apikey)

5. Run the ADK web interface:
```bash
cd src
adk web --port 8080
```

## Usage

1. Access the web interface at `http://localhost:8080`
2. Select the type of analysis you want to perform
3. Enter the stock symbol or other relevant information
4. Review the generated analysis and recommendations

## Development

### Adding New Agents
1. Create a new agent file in the appropriate team directory
2. Add the agent's prompt to `prompts.py`
3. Update the agent's configuration in the main application

### Modifying Existing Agents
1. Update the agent's prompt in `prompts.py`
2. Modify the agent's implementation in its respective file
3. Test the changes using the ADK web interface

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google's Agent Development Kit (ADK)
- yfinance for financial data
- All contributors and users of the system

