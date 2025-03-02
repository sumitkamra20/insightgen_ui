# InsightGen UI
Streamlit UI for the InsightGen API, providing a user-friendly interface for generating insights and headlines for market research presentations.

## Local Development

### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/sumitkamra20/insightgen_ui.git
   cd insightgen_ui
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to set your environment variables.

### Running the Application
```bash
streamlit run insightgen_ui.py
```

Or use the provided script:
```bash
./run_app.sh
```

## Deployment

### Deploying to Streamlit Cloud

1. Push your code to GitHub
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with your GitHub account

3. Click on "New app" and select your repository

4. Configure the deployment:
   - Main file path: `insightgen_ui.py`
   - Python version: 3.9 or 3.10
   - Environment variables:
     - `DEPLOYMENT_ENV`: `production`
     - `API_URL`: Your API URL (e.g., `https://insightgen.onrender.com`)

5. Click "Deploy"

### Environment Variables

- `DEPLOYMENT_ENV`: Set to `production` for deployment, otherwise defaults to development mode
- `API_URL`: URL of the InsightGen API backend
