Smart Prompt Refiner Agent
Overview

Smart Prompt Refiner is an AI agent built with Google ADK that improves raw, unclear user prompts into structured, high-quality prompts optimized for better AI outputs.

Features
Analyzes user intent and detects ambiguity
Enhances clarity and structure of prompts
Adds missing context intelligently
Generates multiple refined prompt variations
Fully deployable on Cloud Run using Vertex AI
Tech Stack
Google ADK (Agent Development Kit)
Vertex AI (Gemini model)
LangChain Community tools
Python
Project Structure
prompt_refiner_agent/
│── agent.py
│── __init__.py
│── requirements.txt
│── .env
Setup
1. Create Virtual Environment
uv venv
source .venv/bin/activate
2. Install Dependencies
uv pip install -r requirements.txt
Environment Configuration
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=prompt-refiner-service

cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL="gemini-2.5-flash"
EOF

source .env
Enable Required Services
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
IAM Setup
gcloud iam service-accounts create ${SA_NAME} \
  --display-name="Prompt Refiner Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
Deploy to Cloud Run
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west1 \
  --service_name=prompt-refiner-agent \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=prompt-refiner \
  --service-account=$SERVICE_ACCOUNT
How It Works
User provides a raw prompt
Analyzer agent identifies intent and gaps
Refiner agent improves the prompt
Formatter outputs clean refined prompts + variations
Example

Input:

make me a project using ai

Output:

Refined prompt with clear objective
Structured instructions
Multiple variations for different use cases
Notes
No external APIs used
Fully compliant with Google Cloud services
Designed for scalability and modular extension
