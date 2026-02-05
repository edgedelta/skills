#!/usr/bin/env python3
"""
EdgeDelta Pipeline Deployment Script
Creates and deploys pipeline v3 configurations to EdgeDelta API

Usage:
    # Create NEW pipeline
    python3 deploy_pipeline.py <pipeline.yaml> <org_id> <api_token> [environment]
    python3 deploy_pipeline.py <pipeline.yaml> --env-file <path_to_.env> [environment]

    # Update EXISTING pipeline
    python3 deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> <org_id> <api_token>
    python3 deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> --env-file <path_to_.env>

Environment options: Linux (default), Windows, Kubernetes
"""

import sys
import json
import requests
import yaml
import time
from datetime import datetime
from pathlib import Path

API_BASE = "https://api.edgedelta.com/v1"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2  # Exponential backoff: 2, 4, 8 seconds

def print_error(message: str):
    """Print a prominent error message"""
    print(f"\n{'!'*80}")
    print(f"ERROR: {message}")
    print(f"{'!'*80}\n")

def is_retryable_error(status_code: int) -> bool:
    """Check if the HTTP error is retryable (server-side errors)"""
    return status_code >= 500 and status_code < 600

class PipelineDeployer:
    def __init__(self, org_id: str, api_token: str):
        self.org_id = org_id
        self.api_token = api_token
        self.headers = {
            "X-ED-API-Token": api_token,
            "accept": "application/json",
            "Content-Type": "application/json"
        }

    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic for transient errors"""
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=self.headers, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=self.headers, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # If successful or non-retryable error, return immediately
                if response.status_code < 500:
                    return response

                # Server error - log and potentially retry
                last_error = f"HTTP {response.status_code}: {response.text}"

                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))  # Exponential backoff
                    print(f"⚠ Server error (attempt {attempt}/{MAX_RETRIES}): {response.status_code}")
                    print(f"  Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print_error(f"Server error after {MAX_RETRIES} attempts: {response.status_code}")
                    print(f"Response: {response.text}")
                    return response

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                    print(f"⚠ Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
                    print(f"  Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print_error(f"Request failed after {MAX_RETRIES} attempts: {e}")
                    raise

        # Should not reach here, but just in case
        raise Exception(f"Request failed: {last_error}")

    def create_pipeline(self, tag: str, environment: str = "Linux", description: str = ""):
        """Create a new base pipeline"""
        url = f"{API_BASE}/orgs/{self.org_id}/pipelines"

        payload = {
            "tag": tag
        }

        print(f"Creating pipeline '{tag}'...")
        try:
            response = self._request_with_retry("POST", url, json=payload)
        except Exception as e:
            print_error(f"Failed to create pipeline: {e}")
            return None

        if response.status_code not in [200, 201]:
            print_error(f"Failed to create pipeline (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return None

        result = response.json()
        pipeline_id = result.get("id")

        if not pipeline_id:
            print_error("No pipeline ID in response")
            return None

        print(f"✓ Pipeline created: {pipeline_id}")
        return pipeline_id

    def deploy_config(self, pipeline_id: str, yaml_path: str, tag: str, environment: str = "Linux", description: str = ""):
        """Deploy configuration to existing pipeline using 3-step process"""

        # Read YAML content
        try:
            with open(yaml_path, 'r') as f:
                content = f.read()
        except Exception as e:
            print_error(f"Failed to read YAML file: {e}")
            return False

        # Step 1: Save configuration
        save_url = f"{API_BASE}/orgs/{self.org_id}/pipelines/{pipeline_id}/save"

        # Properly encode YAML content in JSON payload
        save_payload = {"content": content}

        print(f"Step 1/3: Saving configuration to pipeline {pipeline_id}...")
        try:
            response = self._request_with_retry("POST", save_url, json=save_payload, timeout=60)
        except Exception as e:
            print_error(f"Failed to save config: {e}")
            return False

        if response.status_code not in [200, 201]:
            print_error(f"Failed to save config (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return False

        result = response.json()
        error = result.get("error")

        if error and error != "null" and error is not None:
            print_error(f"Validation error: {error}")
            return False

        print(f"✓ Configuration saved")

        # Step 2: Get version (timestamp) from history
        history_url = f"{API_BASE}/orgs/{self.org_id}/pipelines/{pipeline_id}/history"

        print(f"Step 2/3: Getting version from history...")
        try:
            response = self._request_with_retry("GET", history_url)
        except Exception as e:
            print_error(f"Failed to get history: {e}")
            return False

        if response.status_code != 200:
            print_error(f"Failed to get history (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return False

        history = response.json()
        if not history or len(history) == 0:
            print_error("No history found for pipeline")
            return False

        # Get latest version (first item, highest timestamp)
        # API returns 'timestamp' field, not 'lastUpdated'
        version = str(history[0].get("timestamp"))
        print(f"✓ Got version: {version}")

        # Step 3: Deploy with version
        deploy_url = f"{API_BASE}/orgs/{self.org_id}/pipelines/{pipeline_id}/deploy/{version}"

        print(f"Step 3/3: Deploying version {version}...")
        try:
            response = self._request_with_retry("POST", deploy_url)
        except Exception as e:
            print_error(f"Failed to deploy: {e}")
            return False

        if response.status_code not in [200, 201]:
            print_error(f"Failed to deploy (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return False

        print(f"✓ Pipeline deployed successfully")
        return True

    def verify_pipeline(self, pipeline_id: str):
        """Verify pipeline exists and get details"""
        url = f"{API_BASE}/orgs/{self.org_id}/confs"

        try:
            response = self._request_with_retry("GET", url, timeout=30)
        except Exception as e:
            print_error(f"Failed to verify pipeline: {e}")
            return False

        if response.status_code != 200:
            print_error(f"Failed to verify pipeline (HTTP {response.status_code})")
            print(f"Response: {response.text}")
            return False

        pipelines = response.json()

        for p in pipelines:
            if p.get("id") == pipeline_id:
                print(f"\n{'='*80}")
                print("PIPELINE DETAILS")
                print(f"{'='*80}")
                print(f"ID:          {p.get('id')}")
                print(f"Tag:         {p.get('tag')}")
                print(f"Description: {p.get('description')}")
                print(f"Environment: {p.get('environment')}")
                print(f"Created:     {p.get('created')}")
                print(f"Updated:     {p.get('updated')}")
                print(f"\nView at: https://app.edgedelta.com/pipelines/{pipeline_id}")
                print(f"\nDeploy command:")
                print(f"  ED_API_KEY={pipeline_id} bash -c \"$(curl -L https://release.edgedelta.com/release/install.sh)\"")
                print(f"{'='*80}\n")
                return True

        print(f"✗ Pipeline {pipeline_id} not found in organization")
        return False

    def update_existing_pipeline(self, pipeline_id: str, yaml_path: str):
        """Update an existing pipeline with new configuration"""
        print(f"\n{'='*80}")
        print(f"Updating Existing Pipeline: {pipeline_id}")
        print(f"{'='*80}\n")

        # Deploy config to existing pipeline
        if not self.deploy_config(pipeline_id, yaml_path, "", "", ""):
            print(f"✗ Update failed for pipeline {pipeline_id}")
            return None

        # Verify
        self.verify_pipeline(pipeline_id)

        return pipeline_id

    def full_deployment(self, yaml_path: str, environment: str = "Linux", description: str = ""):
        """Complete deployment: create + deploy + verify"""
        # Read YAML to get tag from settings
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)

            tag = config.get("settings", {}).get("tag", "deployed-pipeline")
        except Exception as e:
            print(f"✗ Failed to read YAML: {e}")
            return None

        # Add timestamp to make tag unique
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_tag = f"{tag}-{timestamp}"

        if not description:
            description = f"Pipeline deployed via edgedelta-pipelines skill"

        # Step 1: Create pipeline
        pipeline_id = self.create_pipeline(unique_tag, environment, description)
        if not pipeline_id:
            return None

        # Step 2: Deploy config
        if not self.deploy_config(pipeline_id, yaml_path, unique_tag, environment, description):
            print(f"✗ Deployment failed, but pipeline {pipeline_id} was created")
            return None

        # Step 3: Verify
        self.verify_pipeline(pipeline_id)

        return pipeline_id

def load_credentials_from_env(env_file: str):
    """Load credentials from .env file"""
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")

        org_id = env_vars.get('ED_ORG_ID') or env_vars.get('EDGEDELTA_ORG_ID')
        api_token = env_vars.get('ED_API_TOKEN') or env_vars.get('ED_ORG_API_TOKEN') or env_vars.get('EDGEDELTA_API_TOKEN')

        if not org_id or not api_token:
            print(f"✗ Missing credentials in {env_file}")
            print(f"  Required: ED_ORG_ID and ED_ORG_API_TOKEN")
            return None, None

        return org_id, api_token
    except Exception as e:
        print(f"✗ Failed to read .env file: {e}")
        return None, None

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  # Create NEW pipeline")
        print("  python3 deploy_pipeline.py <pipeline.yaml> <org_id> <api_token> [environment]")
        print("  python3 deploy_pipeline.py <pipeline.yaml> --env-file <path_to_.env> [environment]")
        print("")
        print("  # Update EXISTING pipeline")
        print("  python3 deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> <org_id> <api_token>")
        print("  python3 deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> --env-file <path_to_.env>")
        print("\nEnvironment options: Linux (default), Windows, Kubernetes")
        sys.exit(1)

    yaml_path = sys.argv[1]
    pipeline_id_to_update = None
    environment = "Linux"

    # Parse arguments
    args = sys.argv[2:]

    # Check for --pipeline-id flag (update existing pipeline)
    if "--pipeline-id" in args:
        idx = args.index("--pipeline-id")
        pipeline_id_to_update = args[idx + 1]
        args = args[:idx] + args[idx + 2:]  # Remove --pipeline-id and its value

    # Check if using --env-file
    if len(args) >= 2 and args[0] == "--env-file":
        org_id, api_token = load_credentials_from_env(args[1])
        environment = args[2] if len(args) > 2 else "Linux"
    elif len(args) >= 2:
        org_id = args[0]
        api_token = args[1]
        environment = args[2] if len(args) > 2 else "Linux"
    else:
        print("✗ Missing credentials")
        sys.exit(1)

    if not org_id or not api_token:
        print("✗ Missing credentials")
        sys.exit(1)

    # Verify YAML file exists
    if not Path(yaml_path).exists():
        print(f"✗ File not found: {yaml_path}")
        sys.exit(1)

    print(f"\n{'='*80}")
    print("EdgeDelta Pipeline Deployment")
    print(f"{'='*80}")
    print(f"YAML:        {yaml_path}")
    print(f"Org ID:      {org_id}")
    if pipeline_id_to_update:
        print(f"Mode:        UPDATE EXISTING")
        print(f"Pipeline ID: {pipeline_id_to_update}")
    else:
        print(f"Mode:        CREATE NEW")
        print(f"Environment: {environment}")
    print(f"{'='*80}\n")

    deployer = PipelineDeployer(org_id, api_token)

    if pipeline_id_to_update:
        # Update existing pipeline
        result = deployer.update_existing_pipeline(pipeline_id_to_update, yaml_path)
    else:
        # Create new pipeline
        result = deployer.full_deployment(yaml_path, environment)

    if result:
        print(f"✓✓✓ DEPLOYMENT SUCCESSFUL ✓✓✓")
        sys.exit(0)
    else:
        print(f"✗✗✗ DEPLOYMENT FAILED ✗✗✗")
        sys.exit(1)

if __name__ == "__main__":
    main()
