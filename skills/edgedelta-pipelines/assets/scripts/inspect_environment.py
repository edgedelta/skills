#!/usr/bin/env python3
"""
EdgeDelta Environment Inspection Script
Inspects Kubernetes, Linux, or Windows environments to discover monitoring opportunities

Usage:
    python3 inspect_environment.py [--verbose] [--format json|markdown]

Detects:
- Kubernetes pods, deployments, services
- Log files and directories
- Running services
- Metrics endpoints
- Common applications (Docker, Nginx, databases, etc.)
"""

import subprocess
import sys
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple

class EnvironmentInspector:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.os_type = platform.system()
        self.findings = {
            "environment": self.os_type,
            "kubernetes": {},
            "log_files": [],
            "services": [],
            "applications": [],
            "metrics_endpoints": [],
            "suggestions": []
        }

    def log(self, msg):
        if self.verbose:
            print(f"[DEBUG] {msg}")

    def run_command(self, cmd: List[str], check=False) -> Tuple[bool, str]:
        """Run command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""

    def inspect_kubernetes(self):
        """Inspect Kubernetes cluster"""
        self.log("Checking for Kubernetes...")

        # Check if kubectl is available
        success, _ = self.run_command(["kubectl", "version", "--client", "--short"])
        if not success:
            self.log("kubectl not available")
            return

        self.findings["kubernetes"]["available"] = True
        self.log("✓ kubectl found")

        # Get pods
        success, output = self.run_command([
            "kubectl", "get", "pods", "--all-namespaces",
            "-o", "json"
        ])
        if success:
            try:
                pods_data = json.loads(output)
                pod_count = len(pods_data.get("items", []))
                self.findings["kubernetes"]["pods"] = pod_count
                self.log(f"Found {pod_count} pods")

                # Sample some pod names
                pod_names = [p["metadata"]["name"] for p in pods_data.get("items", [])[:5]]
                self.findings["kubernetes"]["sample_pods"] = pod_names
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Get services
        success, output = self.run_command([
            "kubectl", "get", "services", "--all-namespaces",
            "-o", "json"
        ])
        if success:
            try:
                svc_data = json.loads(output)
                svc_count = len(svc_data.get("items", []))
                self.findings["kubernetes"]["services"] = svc_count
                self.log(f"Found {svc_count} services")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Get deployments
        success, output = self.run_command([
            "kubectl", "get", "deployments", "--all-namespaces",
            "-o", "json"
        ])
        if success:
            try:
                dep_data = json.loads(output)
                dep_count = len(dep_data.get("items", []))
                self.findings["kubernetes"]["deployments"] = dep_count
                self.log(f"Found {dep_count} deployments")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Suggestions for K8s
        if self.findings["kubernetes"].get("pods", 0) > 0:
            self.findings["suggestions"].append({
                "type": "input",
                "config": "file_input",
                "path": "/var/log/containers/*.log",
                "description": "Collect Kubernetes container logs"
            })

    def inspect_linux_logs(self):
        """Inspect Linux log directories"""
        if self.os_type != "Linux" and self.os_type != "Darwin":
            return

        self.log("Inspecting log directories...")

        common_log_dirs = [
            "/var/log",
            "/var/log/nginx",
            "/var/log/apache2",
            "/var/log/httpd",
            "/var/log/mysql",
            "/var/log/postgresql",
            "/var/log/app",
            "/var/log/application"
        ]

        for log_dir in common_log_dirs:
            path = Path(log_dir)
            if path.exists() and path.is_dir():
                try:
                    # Count log files
                    log_files = list(path.glob("*.log"))
                    if log_files:
                        self.findings["log_files"].append({
                            "directory": str(path),
                            "count": len(log_files),
                            "sample": [f.name for f in log_files[:3]]
                        })
                        self.log(f"Found {len(log_files)} log files in {log_dir}")

                        # Add suggestion
                        self.findings["suggestions"].append({
                            "type": "input",
                            "config": "file_input",
                            "path": f"{log_dir}/*.log",
                            "description": f"Collect logs from {log_dir}"
                        })
                except PermissionError:
                    self.log(f"Permission denied: {log_dir}")

    def inspect_docker(self):
        """Check for Docker"""
        self.log("Checking for Docker...")

        success, output = self.run_command(["docker", "ps", "--format", "{{.Names}}"])
        if success:
            containers = [c for c in output.strip().split("\n") if c]
            self.findings["applications"].append({
                "name": "Docker",
                "status": "running",
                "containers": len(containers),
                "sample": containers[:5]
            })
            self.log(f"✓ Docker found with {len(containers)} containers")

            self.findings["suggestions"].append({
                "type": "input",
                "config": "file_input",
                "path": "/var/lib/docker/containers/*/*.log",
                "description": "Collect Docker container logs"
            })

    def inspect_systemd_services(self):
        """Check for systemd services (Linux)"""
        if self.os_type != "Linux":
            return

        self.log("Checking for systemd services...")

        success, output = self.run_command(["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"])
        if success:
            lines = output.strip().split("\n")
            # Count services (skip header/footer)
            service_lines = [l for l in lines if ".service" in l]
            self.findings["services"] = {
                "type": "systemd",
                "count": len(service_lines),
                "sample": [l.split()[0] for l in service_lines[:5] if l.strip()]
            }
            self.log(f"Found {len(service_lines)} running systemd services")

    def inspect_common_apps(self):
        """Check for common applications"""
        apps_to_check = [
            ("nginx", ["nginx", "-v"]),
            ("apache2", ["apache2", "-v"]),
            ("httpd", ["httpd", "-v"]),
            ("mysql", ["mysql", "--version"]),
            ("postgresql", ["psql", "--version"]),
            ("redis-server", ["redis-server", "--version"]),
            ("mongod", ["mongod", "--version"])
        ]

        for app_name, cmd in apps_to_check:
            success, output = self.run_command(cmd)
            if success:
                self.findings["applications"].append({
                    "name": app_name,
                    "status": "installed",
                    "version": output.strip().split("\n")[0][:100]
                })
                self.log(f"✓ Found {app_name}")

    def inspect_metrics_endpoints(self):
        """Check for common metrics endpoints"""
        # Check for Prometheus node exporter
        success, _ = self.run_command(["curl", "-s", "http://localhost:9100/metrics", "-o", "/dev/null"])
        if success:
            self.findings["metrics_endpoints"].append({
                "type": "prometheus",
                "endpoint": "http://localhost:9100/metrics",
                "description": "Node Exporter"
            })
            self.findings["suggestions"].append({
                "type": "input",
                "config": "prometheus_scrape_input",
                "endpoint": "http://localhost:9100/metrics",
                "description": "Scrape Prometheus node exporter metrics"
            })

    def inspect_all(self):
        """Run all inspections"""
        print(f"{'='*80}")
        print(f"EdgeDelta Environment Inspection")
        print(f"{'='*80}")
        print(f"Platform: {self.os_type}")
        print(f"{'='*80}\n")

        self.inspect_kubernetes()
        self.inspect_linux_logs()
        self.inspect_docker()
        self.inspect_systemd_services()
        self.inspect_common_apps()
        self.inspect_metrics_endpoints()

    def generate_suggestions(self):
        """Generate pipeline configuration suggestions"""
        if not self.findings["suggestions"]:
            self.findings["suggestions"].append({
                "type": "note",
                "description": "No specific monitoring opportunities detected. Consider using template-1 with custom file paths."
            })

    def print_markdown_report(self):
        """Print findings in markdown format"""
        print(f"\n# Environment Inspection Report\n")
        print(f"**Platform:** {self.findings['environment']}\n")

        # Kubernetes
        if self.findings["kubernetes"]:
            print(f"## Kubernetes")
            k8s = self.findings["kubernetes"]
            if k8s.get("available"):
                print(f"- **Pods:** {k8s.get('pods', 0)}")
                print(f"- **Services:** {k8s.get('services', 0)}")
                print(f"- **Deployments:** {k8s.get('deployments', 0)}")
                if k8s.get("sample_pods"):
                    print(f"- **Sample pods:** {', '.join(k8s['sample_pods'])}")
                print()

        # Log Files
        if self.findings["log_files"]:
            print(f"## Log Files")
            for log_dir in self.findings["log_files"]:
                print(f"- **{log_dir['directory']}**: {log_dir['count']} files")
                if log_dir.get("sample"):
                    print(f"  - Sample: {', '.join(log_dir['sample'])}")
            print()

        # Applications
        if self.findings["applications"]:
            print(f"## Applications")
            for app in self.findings["applications"]:
                print(f"- **{app['name']}**: {app['status']}")
                if app.get("containers"):
                    print(f"  - Containers: {app['containers']}")
                if app.get("version"):
                    print(f"  - Version: {app['version']}")
            print()

        # Services
        if self.findings["services"]:
            print(f"## Services")
            svc = self.findings["services"]
            print(f"- **Type:** {svc['type']}")
            print(f"- **Running:** {svc['count']}")
            if svc.get("sample"):
                print(f"- **Sample:** {', '.join(svc['sample'])}")
            print()

        # Metrics Endpoints
        if self.findings["metrics_endpoints"]:
            print(f"## Metrics Endpoints")
            for endpoint in self.findings["metrics_endpoints"]:
                print(f"- **{endpoint['description']}**: {endpoint['endpoint']}")
            print()

        # Suggestions
        if self.findings["suggestions"]:
            print(f"## Suggested Pipeline Inputs\n")
            for idx, suggestion in enumerate(self.findings["suggestions"], 1):
                if suggestion["type"] == "input":
                    print(f"### {idx}. {suggestion['description']}")
                    print(f"```yaml")
                    print(f"- name: suggested_input_{idx}")
                    print(f"  type: {suggestion['config']}")
                    if suggestion.get("path"):
                        print(f"  path: {suggestion['path']}")
                    if suggestion.get("endpoint"):
                        print(f"  endpoint: {suggestion['endpoint']}")
                    print(f"```\n")
                else:
                    print(f"{idx}. {suggestion['description']}\n")

    def print_json_report(self):
        """Print findings in JSON format"""
        print(json.dumps(self.findings, indent=2))

def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    format_type = "markdown"  # default

    for arg in sys.argv:
        if arg.startswith("--format="):
            format_type = arg.split("=")[1]

    inspector = EnvironmentInspector(verbose=verbose)
    inspector.inspect_all()
    inspector.generate_suggestions()

    if format_type == "json":
        inspector.print_json_report()
    else:
        inspector.print_markdown_report()

if __name__ == "__main__":
    main()
