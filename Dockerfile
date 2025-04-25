FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY streamlit_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r streamlit_requirements.txt

# Copy application file
COPY insightgen_ui.py .

# Set environment variables
ENV DEPLOYMENT_ENV=production
ENV PORT=8080
ENV API_URL=https://insightgen-api-195411721870.us-central1.run.app

# Expose port
EXPOSE 8080

# Command to run the application
CMD streamlit run insightgen_ui.py --server.port=$PORT --server.address=0.0.0.0
