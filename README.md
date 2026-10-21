# Student Internship Tracker — DevOps Case Study

A Flask + SQLite web app with three pages (Dashboard, Add Internship, Applications), containerized with Docker and deployed to Docker Desktop Kubernetes by Jenkins.

## Prerequisites (Windows)
- Python 3.11+ (Python 3.12 recommended)
- Git for Windows
- Docker Desktop, with Kubernetes enabled
- Jenkins with Pipeline and Git plugins
- `kubectl` available to the Jenkins process
- A Docker Hub account and a GitHub repository

## 1. Configure the repository
1. Replace `YOUR_DOCKERHUB_USERNAME` in `Jenkinsfile` and `k8s/deployment.yaml` with your Docker Hub username.
2. Commit and push all project files to GitHub.
3. In Jenkins, create a Pipeline job, choose **Pipeline script from SCM**, choose Git, enter the repository URL, and set Script Path to `Jenkinsfile`.

## 2. Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
$env:DATABASE_PATH = "$PWD\data\internships.db"
py -m flask --app app run --debug
```
Open http://127.0.0.1:5000. Pages: `/`, `/add`, `/applications`. Health endpoint: `/health`.

Run tests:
```powershell
py -m pytest -q
```

## 3. Run with Docker
```powershell
docker build -t student-internship-tracker:local .
docker run --rm -p 8081:5000 -v "${PWD}/data:/data" -e DATABASE_PATH=/data/internships.db student-internship-tracker:local
```
Open http://127.0.0.1:8081.

## 4. Prepare Docker Hub
1. Create a Docker Hub repository named `student-internship-tracker`.
2. In Jenkins, open **Manage Jenkins → Credentials → (global) → Add Credentials**.
3. Kind: **Username with password**; Username: your Docker Hub username; Password: a Docker Hub access token; ID: `dockerhub-credentials`.
4. Replace `YOUR_DOCKERHUB_USERNAME` in `Jenkinsfile` and `k8s/deployment.yaml`.
5. Commit and push the changes.

Use a Docker Hub access token rather than your account password.

## 5. Enable Docker Desktop Kubernetes
1. Open Docker Desktop → Settings → Kubernetes.
2. Enable Kubernetes and wait until it reports that the cluster is running.
3. In PowerShell, check:
```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```
The Jenkins process must use the same kubeconfig/context. A Windows Jenkins service may run as LocalSystem or another account and may not see your user kubeconfig. For a local class demo, run Jenkins under the same Windows user as Docker Desktop, or configure a dedicated Jenkins agent under that user. Verify `kubectl config current-context` from the Jenkins job itself.

## 6. Jenkins requirements
- Install Jenkins plugins: Pipeline, Git, Credentials Binding, and (optionally) GitHub.
- Install Python and Docker CLI on the Jenkins agent, and ensure `py`, `docker`, and `kubectl` are on that agent's PATH.
- The provided Jenkinsfile uses Windows `bat` steps. If your Jenkins agent runs Linux, replace those commands with shell commands.
- Docker Desktop Kubernetes uses the host's local kubeconfig. Do not assume a Jenkins Windows service can access a desktop user's Kubernetes context automatically.

## 7. Configure GitHub webhook
A webhook needs a URL reachable by GitHub. `http://localhost:8080/github-webhook/` will NOT work from GitHub because localhost refers to GitHub's servers, not your computer.
1. Make the Jenkins URL reachable from the internet using a school-approved tunnel or a properly configured public host. Do not expose Jenkins without authentication and appropriate security controls.
2. In GitHub: repository → **Settings → Webhooks → Add webhook**.
3. Payload URL: `https://YOUR-REACHABLE-JENKINS-URL/github-webhook/`
4. Content type: `application/json`.
5. Select **Just the push event**, then save.
6. In Jenkins job configuration, enable **GitHub hook trigger for GITScm polling**.
7. Push a small change and check GitHub webhook deliveries and the Jenkins build history.

If you cannot expose Jenkins, use Jenkins SCM polling as a classroom alternative (job → Configure → Build Triggers → Poll SCM; for example `H/2 * * * *`). It is polling, not an immediate webhook trigger.

## 8. Run the pipeline and verify
Push code to GitHub or click **Build Now** for the first run. Check each stage in the Jenkins console:
1. Checkout
2. Test Flask application
3. Build Docker image
4. Login and push to Docker Hub
5. Deploy to Kubernetes

Then verify:
```powershell
kubectl get deployments
kubectl get pods
kubectl get services
kubectl rollout status deployment/student-internship-tracker
```
Open http://localhost:30080.

## Important SQLite note
The Kubernetes manifest uses a PersistentVolumeClaim so SQLite data is stored outside the container filesystem. This is appropriate for a single-replica classroom demo, not a high-availability production database. SQLite should not be shared among multiple replicas.

## Common troubleshooting
- **`py` not recognized:** install Python and enable PATH; restart Jenkins/agent after PATH changes.
- **`docker` not recognized / access denied:** install Docker Desktop, confirm Docker works for the Jenkins account, and restart the agent.
- **`kubectl` cannot connect:** check `kubectl config current-context` and verify Jenkins can read the correct kubeconfig.
- **ImagePullBackOff:** check the image name, Docker Hub repository visibility, and whether the image was pushed successfully.
- **Webhook delivery fails:** Jenkins must be reachable at the configured public HTTPS URL; `localhost` does not work for GitHub webhooks.
- **PVC pending:** check `kubectl describe pvc student-internship-tracker-pvc`; Docker Desktop Kubernetes normally provides a default storage class.

## Academic project scope
This project demonstrates automated test, image build/push, and Kubernetes deployment. It does not include production-grade authentication, authorization, secret management, database backups, or high availability.
