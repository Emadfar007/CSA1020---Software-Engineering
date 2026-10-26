# Experiment 13 — ReleaseHarbor: Jenkins CI/CD with Docker

## Aim

To automate the building, testing, publication and cloud deployment of a containerized release-readiness application using a local Jenkins pipeline.

## Tools Required

Docker Desktop, Docker Compose, Jenkins LTS, Git/GitHub, Node.js 24, Docker Hub, Render Free web service, PowerShell and a browser.

## Algorithm

1. Create the dependency-free ReleaseHarbor application with editable release details, a readiness checklist, critical blockers, a timeline, local drafts and JSON export.
2. Build separate Docker test and runtime targets. Run the final application as a non-root user.
3. Start Jenkins with the supplied Compose stack. Its Docker builds use a dedicated Docker-in-Docker daemon over TLS; the Windows host Docker socket is not mounted.
4. Keep administrator and deployment secrets outside Git, and import them into Jenkins credentials. Expose Jenkins only on local loopback port 8090, with anonymous read-only access to the demonstration job.
5. Load the Jenkinsfile directly from the Software Engineering repository. Poll once per minute for application, Dockerfile or CI configuration commits; report-only changes and unrelated experiments are excluded.
6. Run checkout, test-image build, automated JUnit tests, runtime-image build and HTTP smoke checks. A failed stage blocks publication and deployment.
7. Publish the tested runtime image to Docker Hub using an immutable build-specific tag. Record its digest.
8. Trigger the separate Render image-backed service through a secret deploy hook using the exact pushed image digest. Verify cloud health and the source commit/build number.
9. Demonstrate an intentional test-gate failure, then make a real source change and verify that SCM polling automatically builds and deploys it.
10. Capture the Jenkins stages, test results, commit trigger and cloud application. Preserve the evidence with this report.

Render is restricted to Free compute with no database, disk, paid service or scheduled keep-alive. Free web services have no fixed trial-expiry date in the current documentation, but sleep after 15 idle minutes and share monthly quotas with the workspace. Bandwidth and other platform usage remain subject to Render's current plan rules; unlimited always-on hosting is not provided.

## Output Screenshots

Screenshots will be added after the actual Jenkins and cloud workflow is verified.

## Result

Implementation prepared. Runtime Jenkins, commit-trigger and Render verification are in progress; this is not yet a completion claim.
