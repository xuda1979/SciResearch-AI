#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Deployment script for US College Admission Counseling application
#
# This script automates the process of building a Docker image, uploading it to
# Google Artifact Registry, and deploying it to Google Cloud Run. It is
# intended for use with the project available at
# https://github.com/xuda1979/US_college_admission_counseling. Before running
# this script, install the Google Cloud SDK and authenticate with your
# Google Cloud account using `gcloud auth login`. You should also set your
# desired project with `gcloud config set project YOUR_PROJECT_ID`.
#
# Variables marked with "EDIT ME" should be replaced with values suitable for
# your environment. You can also supply them as environment variables when
# invoking the script (e.g. `PROJECT_ID=my-project ./deploy_to_gcloud.sh`).
#
# References:
# - Google Cloud Run quickstart documentation
# - Internal deployment guide for the US College Admission Counseling project
# -----------------------------------------------------------------------------

set -euo pipefail

# --------------------------- Configuration ----------------------------------

# Your Google Cloud project ID (EDIT ME).
PROJECT_ID="your-gcp-project-id"

# The region where you want to deploy the service (EDIT ME).  See
# https://cloud.google.com/run/docs/locations for available options.
REGION="us-central1"

# The name of the Artifact Registry repository to store the Docker image. If
# this repository does not exist, the script will attempt to create it.
REPOSITORY="college-counselor-repo"

# Name of the Docker image (without the tag).  This will be combined with
# PROJECT_ID to form the full image path: gcr.io/${PROJECT_ID}/${IMAGE_NAME}.
IMAGE_NAME="college-counselor"

# Name of the Cloud Run service to create or update.
SERVICE_NAME="college-counselor-service"

# Application environment variables (EDIT ME).  These variables are passed to
# Cloud Run at deployment time.  Keep secrets in a secure location (for
# example, Secret Manager) rather than hard‑coding them here.
OPENAI_API_KEY="your-openai-api-key"
JWT_SECRET_KEY="your-jwt-secret-key"
CORS_ORIGINS="*"

# -----------------------------------------------------------------------------
# You normally do not need to modify anything below this line.
# -----------------------------------------------------------------------------

echo "Starting deployment to Google Cloud Run..."

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "your-gcp-project-id" ]]; then
  echo "Error: PROJECT_ID is not set. Please edit this script and set your Google Cloud project ID." >&2
  exit 1
fi

# Enable required APIs.  If these are already enabled, the commands will
# succeed without making changes.  Artifact Registry and Cloud Run are
# necessary services for this deployment.
echo "Enabling Artifact Registry and Cloud Run APIs..."
gcloud services enable artifactregistry.googleapis.com run.googleapis.com --project "$PROJECT_ID"

# Create Artifact Registry repository if it does not exist.  Artifact Registry
# stores container images in your Google Cloud project.  The location must
# match the region you plan to deploy to or be multi‑region.  Using
# gcloud's `locations` API ensures idempotency.
echo "Ensuring Artifact Registry repository '$REPOSITORY' exists..."
if ! gcloud artifacts repositories describe "$REPOSITORY" --location "$REGION" --project "$PROJECT_ID" > /dev/null 2>&1; then
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Repository for College Counselor container images" \
    --project "$PROJECT_ID"
fi

# Configure Docker to use gcloud as a credential helper for Artifact Registry.
# This allows the `docker` CLI to push images to gcr.io or other Artifact
# Registry domains.  If you have configured this previously, the command will
# simply confirm the configuration.
echo "Configuring Docker authentication for Artifact Registry..."
gcloud auth configure-docker --quiet

# Build the container image from the Dockerfile in the current directory.  If
# your project files reside elsewhere, adjust the context (the final '.') to
# point to the project root.  You can also specify a tag (e.g., :v1) by
# appending it to IMAGE_NAME, but the default 'latest' tag is used here.
FULL_IMAGE="gcr.io/${PROJECT_ID}/${IMAGE_NAME}"
echo "Building Docker image ${FULL_IMAGE}..."
docker build -t "$FULL_IMAGE" .

# Push the image to Artifact Registry.  This step uploads the built image to
# your project's container registry so that Cloud Run can access it.
echo "Pushing image ${FULL_IMAGE} to Artifact Registry..."
docker push "$FULL_IMAGE"

# Deploy the service to Cloud Run.  The `--allow-unauthenticated` flag makes
# the service publicly accessible.  Remove it if you require authentication.
# The environment variables are passed as comma‑separated KEY=VALUE pairs.
echo "Deploying service ${SERVICE_NAME} to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$FULL_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},JWT_SECRET_KEY=${JWT_SECRET_KEY},CORS_ORIGINS=${CORS_ORIGINS}" \
  --port=8080 \
  --project "$PROJECT_ID"

echo "Deployment completed successfully."
