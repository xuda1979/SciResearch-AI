# Deploying the US College Admission Counseling application to Google Cloud Run

This guide explains how to deploy the [US College Admission Counseling](https://github.com/xuda1979/US_college_admission_counseling) project as a publicly accessible web service on Google Cloud Run. It assumes you have a **Google Cloud account** with billing enabled and basic familiarity with the command line.

## Prerequisites

Before you begin, ensure the following tools and resources are available on your machine:

1. **Google Cloud CLI** – Install from the [official instructions](https://cloud.google.com/sdk/docs/install) and authenticate with your account:
   ```bash
   gcloud auth login
   gcloud config set project <your‑gcp‑project‑id>
   ```
2. **Docker** – Required for building container images locally. If you prefer not to install Docker, you can use Google Cloud Build exclusively; see the notes at the end of this guide.
3. **Access to the project source code** – Clone the repository locally:
   ```bash
   git clone https://github.com/xuda1979/US_college_admission_counseling.git
   cd US_college_admission_counseling
   ```

## Overview of the deployment process

Deploying to Cloud Run consists of the following high‑level steps:

1. **Enable required services** – Cloud Run and Artifact Registry need to be enabled in your Google Cloud project.
2. **Create an Artifact Registry repository** – This repository stores your container image.
3. **Build a container image** – Use Docker (or Cloud Build) to create an image from the project’s Dockerfile.
4. **Push the image to Artifact Registry** – Upload the built image so it can be used by Cloud Run.
5. **Deploy to Cloud Run** – Launch a Cloud Run service using the pushed image and configure environment variables.

## Step‑by‑step instructions

### 1. Configure your project and enable services

Set the active project and enable the APIs used by Artifact Registry and Cloud Run:

```bash
gcloud config set project <your‑gcp‑project‑id>
gcloud services enable artifactregistry.googleapis.com run.googleapis.com
```

### 2. Create an Artifact Registry repository

Choose a **region** (e.g., `us‑central1`) where both the registry and Cloud Run service will reside. Create the repository (if it does not already exist):

```bash
gcloud artifacts repositories create college-counselor-repo \
  --repository-format=docker \
  --location=<region> \
  --description="Repository for College Counselor container images"
```

### 3. Build the container image

From the root of the project (the directory with the `Dockerfile`), build the image using Docker. Replace `<your‑gcp‑project‑id>` and `<image-name>` with appropriate values:

```bash
docker build -t gcr.io/<your‑gcp‑project‑id>/<image-name> .
```

> **Tip:** The provided `deploy_to_gcloud.sh` script automates the build and push steps. Edit the variables at the top of the script with your project ID, region, and service name, then run:
> 
> ```bash
> chmod +x deploy_to_gcloud.sh
> ./deploy_to_gcloud.sh
> ```

### 4. Push the image to Artifact Registry

Authenticate Docker to push to Artifact Registry and upload the image:

```bash
gcloud auth configure-docker --quiet
docker push gcr.io/<your‑gcp‑project‑id>/<image-name>
```

### 5. Deploy the image to Cloud Run

Use `gcloud run deploy` to create or update a Cloud Run service. Specify the service name, region, and environment variables required by the application:

```bash
gcloud run deploy <service-name> \
  --image gcr.io/<your‑gcp‑project‑id>/<image-name> \
  --platform managed \
  --region <region> \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=<your-openai-api-key>,JWT_SECRET_KEY=<your-jwt-secret-key>,CORS_ORIGINS=* \
  --port 8080
```

The deployment may take a minute. Once completed, the command will output a URL where the service can be accessed. Visit this URL in a browser to confirm that the application is running.

## Alternative: Using Cloud Build exclusively

If you prefer not to install Docker locally, you can delegate the build and push operations to Google Cloud Build:

```bash
gcloud builds submit --tag gcr.io/<your‑gcp‑project‑id>/<image-name>
```

This command reads the `Dockerfile` and uploads the image directly to Artifact Registry. After the build finishes, proceed with the Cloud Run deployment as shown above.

## Environment variables and secrets

The US College Admission Counseling application expects several runtime configuration values, such as the OpenAI API key, JWT secret, and allowed CORS origins. Set these variables via the `--set-env-vars` flag when deploying. **Never hard‑code secrets in your source code or Dockerfile**. For production deployments, consider storing secrets in [Secret Manager](https://cloud.google.com/secret-manager) and referencing them in Cloud Run.

## Conclusion

By following this guide you will have a fully containerized version of the US College Admission Counseling application running on Google Cloud Run. Cloud Run manages scaling, security, and networking for you, allowing you to focus on the application itself. For subsequent updates, rebuild and push a new image, then run the `gcloud run deploy` command again to apply changes.
