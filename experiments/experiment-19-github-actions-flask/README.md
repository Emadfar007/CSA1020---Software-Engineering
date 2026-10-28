# Experiment 19 — Packlight: Flask CI/CD with GitHub Actions

## Aim

To automate testing, Docker image building, Docker Hub publication and cloud deployment of a containerized Flask application using GitHub Actions.

**Packlight** is a small, stateless trip-packing planner. It generates quantities for essentials, clothing, weather and activities from the number of days, travelers and laundry availability.

## Tools Required

**Access status - checked 28 October 2026:** The Render deployment is currently suspended and returns HTTP 503. Render records **Free Tier Usage Exceeded** as the reason. The source, published image, recorded pipeline results and screenshots remain accessible in this submission. This is separate from normal idle sleep; refreshing the app cannot remove the quota restriction.

| Tool | Purpose |
|---|---|
| GitHub repository and GitHub Actions | Source control and automated pipeline |
| Python 3.12, Flask 3.1.3 and Gunicorn 26.2.0 | Application, API and production HTTP server |
| Docker and Buildx | Separate test/runtime images and container execution |
| Docker Hub | Store the tested, versioned image and its immutable digest |
| Render Free | Host the deployed container |

**Deployment:** [Open Packlight](https://packlight-exp19.onrender.com/) · [Health](https://packlight-exp19.onrender.com/healthz) · [Deployed build identity](https://packlight-exp19.onrender.com/api/version)

**Submission:** [Experiment source](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-19-github-actions-flask) · [Active workflow YAML](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/.github/workflows/experiment-19-cicd.yml) · [Workflow file copy](workflow/experiment-19-cicd.yml) · [Actions runs](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-19-cicd.yml) · [Docker Hub tags](https://hub.docker.com/r/coastrider7/csa1020-exp19-packlight/tags)

Render Free can sleep after inactivity and has shared usage limits; see [Render Free service limits](https://render.com/docs/free).

## Algorithm

1. Add the Flask application, tests, [Dockerfile](Dockerfile) and [workflow](workflow/experiment-19-cicd.yml) to the existing repository. Install the active workflow at `.github/workflows/experiment-19-cicd.yml`.
2. Store registry access in the existing `EXP14_DOCKERHUB_USERNAME` and `EXP14_DOCKERHUB_TOKEN` GitHub secrets. Store the new service hook in `EXP19_RENDER_DEPLOY_HOOK`; configure `EXP19_CLOUD_URL` and `EXP19_RENDER_SERVICE_ID` as repository variables. Keep credential values out of source.
3. Trigger the workflow when application or pipeline changes are pushed to `main`, when a related pull request opens or changes, or through manual dispatch. Report-only changes do not redeploy the app.
4. Check out the exact source commit and build the Docker `test` target. Run the 20 application tests inside its container; fail on missing, skipped-only or failing tests.
5. Build the non-root `runtime` target with the source SHA and build number. Run the exact runtime image and verify its health, build metadata, packing calculation and invalid-input response over HTTP.
6. On trusted `main` runs, authenticate to Docker Hub and push that same tested image under a unique run/attempt/SHA tag. Record the published `sha256` digest. Pull requests stop after validation.
7. Send the immutable image reference to the dedicated Render service. Wait for the cloud API to report the expected source SHA and build number, then verify the actual application calculation and validation response. A trusted-main deployment failure fails the pipeline.
8. Retain test, smoke-test and deployment receipts as Actions artifacts for seven days and publish a pipeline summary. Open the deployment link and generate a packing list to check the user-facing result.

The Docker stages can also be reproduced from the experiment directory:

```bash
docker build --target test -t packlight-tests .
docker run --rm packlight-tests
docker build --target runtime -t packlight .
docker run --rm -p 127.0.0.1:8000:8000 packlight
```

The example of four days, two travelers, rainy weather and a trail activity produces **47 items**, including one shared first aid kit. The deployed `/api/version` endpoint identifies the source commit and pipeline build.

## Output Screenshots

**1. Deployed Packlight application.** The working Flask interface and generated packing list.

![Deployed Packlight application](screenshots/01-packlight-app.jpg)

**2. GitHub Actions pipeline.** The recorded testing, image-publication and deployment run.

![GitHub Actions pipeline result](screenshots/02-github-actions-success.jpg)

## Result

The push-triggered [run 2](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40714300739) completed successfully for source `dd4d44cdf641f6c3883a5df0dc8f60526ab40d84`. It passed **20 Docker unit tests**, verified the runtime over HTTP, published the tested image to Docker Hub, deployed its immutable digest to Render and verified the matching live source/build identity and API behavior.

Recorded evidence: [20 test results](evidence/unit-tests.txt) · [Container HTTP checks](evidence/container-smoke.json) · [Image and verified cloud deployment](evidence/cloud-deployment.json) · [Actions run and step results](evidence/github-actions-run.json).

The cloud application is live at [packlight-exp19.onrender.com](https://packlight-exp19.onrender.com/). The 47-item API fixture passed, and the browser workflow generated 59 items for a six-day rainy trail trip for two travelers, then reduced the list to 47 with laundry enabled. The submitted YAML and deployment link demonstrate the complete automated pipeline.
