# Experiment 14 — FocusLane: Continuous Deployment with GitHub Actions

## Aim

To automatically test, build and publish a Dockerized application, then deploy its exact tested image to a cloud service whenever application code is pushed to GitHub.

## Tools Required

Git/GitHub, GitHub Actions standard hosted runner, Docker and Buildx, Node.js 24, Docker Hub, Python standard library, Render Free web service, and a browser.

## Algorithm

1. Create FocusLane, a study-sprint planner with editable subjects, priorities, time budgets and dates. Generate a real daily schedule through its API, save browser drafts and export plans.
2. Use a pinned, non-root, multi-stage Dockerfile with separate test and runtime targets.
3. Install the supplied workflow at the repository root as `.github/workflows/experiment-14-cd.yml`.
4. Validate application and CI guard tests in GitHub Actions. Reject empty or failing test results before image publication.
5. Build the runtime with commit SHA and run/attempt identity, then exercise the actual container's HTTP API.
6. On trusted `main` builds, publish that same tested image to Docker Hub under a unique tag and record its registry digest. Pull requests run validation without deployment secrets.
7. Bootstrap one separate Render Free image-backed service, store its deploy hook in a GitHub Actions secret, and enable the experiment's cloud-ready variable.
8. Deploy the exact pushed digest and verify the live application's commit, run identity, health, schedule calculations and invalid-input handling.
9. Push a second visible application change and verify that the hosted workflow automatically updates the cloud application.

The workflow uses pinned actions, scoped triggers, read-only repository permissions, serialized deployments, build caching, short-lived verification artifacts and a delivery summary. No local Jenkins controller is required. Render Free sleeps when idle and is subject to shared monthly quotas; it has no fixed web-service trial-expiry date under the current offering.

## Output Screenshots

Screenshots will be added after the actual hosted runs and deployment are verified.

## Result

Implementation prepared. Hosted workflow and cloud verification are in progress; completion is not yet claimed.
