# CSA1020 Browser Docker Lab

**Automatic deployment update - 28 October 2026:** Experiments **13, 14 and 19** use this existing Codespace as their automatic deployment target. `bash browser-lab/bin/lab start cicd` starts all three apps, Jenkins and the outbound Actions deployment agent. Jenkins deploys Experiment 13 inside its dedicated TLS Docker daemon; Actions publishes Experiments 14 and 19 and waits for verified activation by the agent. The original Render services remain quota-suspended and are no longer active deployment targets. [Automatic deployment records](automatic-deployment-2026-10-28.json) retain the captured results.

Run the Docker experiments in the private GitHub Codespaces browser environment. Images, build cache, containers and persistent task data live on the cloud machine, so Docker Desktop is not required on the laptop after migration is verified.

[Open the existing browser IDE](https://miserable-cobweb-4j9pjv79r7w7fjrqw.github.dev/) · [Manage, resume or stop the Codespace](https://github.com/codespaces)

Sign in as **Emadfar007**. The Codespace is named `miserable-cobweb-4j9pjv79r7w7fjrqw`. Resume it if stopped; app links work only after their experiment profile is started. Keep all forwarded ports **Private**.

[Cloud migration verification, 27 October 2026](verification-2026-10-27.json) records the restored data, application tests, Kubernetes resume check and independent receiver engine. [Browser restoration verification, 28 October 2026](verification-2026-10-28.json) records the restored CI/CD app runtimes, image identities, API checks and preserved Jenkins state.

| Experiment | Start command from the repository root | Private browser app |
|---|---|---|
| 11 | `bash browser-lab/bin/lab start 11` | [Orbital Fieldnotes](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8087.app.github.dev/) |
| 12 | `bash browser-lab/bin/lab start 12 --kubernetes` | [Docker API](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8088.app.github.dev/) · [Kubernetes NodePort](https://miserable-cobweb-4j9pjv79r7w7fjrqw-30088.app.github.dev/) |
| 13 | `bash browser-lab/bin/lab start 13` | [ReleaseHarbor](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8091.app.github.dev/) · [Jenkins](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/) · [Job and saved results](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/) |
| 14 | `bash browser-lab/bin/lab start 14` | [FocusLane](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8094.app.github.dev/) · [Actions](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-14-cd.yml) |
| 16 | `bash browser-lab/bin/lab start 16` | [Morrow Task Studio](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8096.app.github.dev/) |
| 17 | `bash browser-lab/bin/lab start 17` | [Builder A](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8097.app.github.dev/) · [Receiver B](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8098.app.github.dev/) |
| 18 | `bash browser-lab/bin/lab start 18` | [SproutHouse](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8180.app.github.dev/) · [Headlamp Kubernetes dashboard](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8181.app.github.dev/c/SproutHouse-Lab/deployments?namespace=sprouthouse-exp18) |
| 19 | `bash browser-lab/bin/lab start 19` | [Packlight](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8099.app.github.dev/) · [Actions](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-19-cicd.yml) |

Use the browser terminal from the repository root:

```bash
bash browser-lab/bin/lab status
bash browser-lab/bin/lab start 11
bash browser-lab/bin/lab start 12
bash browser-lab/bin/lab start 12 --kubernetes
bash browser-lab/bin/lab start 13
bash browser-lab/bin/lab start 14
bash browser-lab/bin/lab start 19
bash browser-lab/bin/lab start cicd
bash browser-lab/bin/lab stop cicd
bash browser-lab/bin/lab start 16
bash browser-lab/bin/lab start 17
bash browser-lab/bin/lab start 18
bash browser-lab/bin/lab start 18 --build
bash browser-lab/bin/lab urls
bash browser-lab/bin/lab stop all
```

Individual startup runs one experiment at a time and stops the other profiles without deleting their data or images. `lab start cicd` runs Experiments 13, 14 and 19 together and stops only the other profiles; `lab stop cicd` stops this group while retaining images and data. No application starts automatically when Codespaces opens. Experiment 12 starts the standalone API by default; `--kubernetes` also starts its real kind cluster and NodePort. Experiment 17 starts both its builder and isolated receiver. Experiment 18 creates or resumes its own kind cluster, with a Nginx frontend, two Flask API replicas, a persistent PostgreSQL database and the real Headlamp dashboard. Use `start 18 --build` to rebuild its application images after source edits. Experiments 13, 14 and 19 use ports 8091, 8094 and 8099, bootstrapping from recorded images only when no newer deployment state exists. Experiment 13 also starts Jenkins on 8090 with its saved jobs and results. The current pipeline stages deploy new tested images to this lab. Experiment 13 publishes port 8091 through the dedicated Jenkins Docker daemon. Experiments 14 and 19 use the outbound deployment agent started with their profiles; `lab start cicd` starts the agent for both, and `lab stop cicd` stops it with the apps. Use `bash browser-lab/bin/lab deploy-status` to inspect the agent. Successful deployment state is retained so a lab restart uses the most recently deployed image rather than resetting to the bootstrap image.

**Verified automatic deliveries — 28 October 2026:** [Jenkins build #8](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/8/), [FocusLane run 6.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740905728) and [Packlight run 5.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740904579) completed successfully. Live API identities matched, and a real `stop cicd` / `start cicd` preserved all three latest releases and restarted the agent. [Captured deployment evidence](automatic-deployment-2026-10-28.json).

## Private browser access

The devcontainer forwards twelve ports: 8087, 8088, 30088, 8090, 8091, 8094, 8096, 8097, 8098, 8099, 8180 and 8181. GitHub forwards them privately by default. Confirm **Private** visibility in the Ports tab before testing. `lab urls` prints the actual `https://CODESPACENAME-PORT.app.github.dev/` addresses; a URL responds only when that profile is running. Do not make Jenkins, Headlamp or the other test ports public.

## SproutHouse Kubernetes project

[Experiment 18 report and YAML files](../experiments/experiment-18-sprouthouse-kubernetes/README.md) describe the frontend → backend → PostgreSQL workflow. The database uses a retained `512Mi` persistent-volume claim. Stopping the profile preserves the node and its database rather than deleting the cluster or volume.

Headlamp uses the `SproutHouse-Lab` kubeconfig context and a rotating Kubernetes service-account token held server-side. Its role can read this project's workloads and limited cluster navigation metadata. It cannot read Secrets, modify workloads, execute into pods or access other namespaces' workloads. Access remains behind the private GitHub Codespaces port; no bearer token is included in the source or browser screenshots.

From the experiment folder in the browser terminal:

```bash
cd experiments/experiment-18-sprouthouse-kubernetes
bash scripts/lab.sh status
bash scripts/lab.sh scale 3
python3 scripts/load-check.py --expect-pods 3
```

Scaling changes only the frontend Deployment. The load check measures real HTTP responses and frontend pod identities; the dashboard displays actual Kubernetes pods, services, deployments, events and volumes.

## Saved data

Persistent data is outside the Git repository in `/workspaces/.lab-data`:

| Path under the data directory | Contents |
|---|---|
| `morrow/` | Experiment 16 SQLite task database and related files, UID 10001 |
| `jenkins-home/` | Restored Jenkins jobs, history and encrypted configuration, UID 1000 |
| `jenkins-docker/` | The Jenkins build daemon's image store |
| `jenkins-certificates/` | Jenkins build daemon client certificates |
| `meridian-receiver/` | Experiment 17 receiver image store |
| `private/jenkins-secrets/` | Existing `jenkins_admin_password` and `seed_credentials.json` |
| `private/parcelpilot-kubeconfig` | Private kind cluster access configuration |
| `private/sprouthouse-exp18/` | Experiment 18 operator kubeconfig and privately generated database password |
| `tools/` | Verified pinned kind and kubectl binaries |
| `deployments/` | Last successful image/build receipts and the Actions deployment agent state |
| `private/browser-deployment-key.pem` | Lab-only RSA private key for temporary Actions callback tokens; never commit it |

The Docker-in-Docker feature additionally supplies its own persistent Docker and containerd state volumes. SproutHouse's PostgreSQL PVC is stored inside its retained kind node volume. Do not commit private backups, databases, certificates, passwords or tokens to the public experiment repository. The runner does not copy credentials automatically. Restore the private Jenkins files before `lab start 13`; it refuses to invent replacement credentials. Restore Morrow's task files with owner `10001:10001` and Jenkins home with owner `1000:1000` before starting those experiments.

Morrow's seven tasks and original activity history, plus Jenkins configuration and job history, were restored and verified. Browser-only preferences for the old localhost sites stay in that browser origin; they are not automatically copied to the new cloud URLs. The migration does not remove browser profiles or saved browser data.

`LAB_DATA_DIR` can override the data directory when needed. `LAB_EXP11_IMAGE` and `LAB_EXP13_IMAGE` can select migrated registry images; without these, the runner builds their existing Dockerfiles in the cloud when the original local image names are unavailable. Published Experiments 12, 16 and 17 use recorded immutable digests. Experiments 13, 14 and 19 start from recorded digests only until a newer verified deployment is available; subsequent starts retain the latest deployment. Application source/build identity is baked into every image.

## Jenkins migration control

The first Jenkins start writes a small migration guard into the restored **cloud** Jenkins home and starts Jenkins in quiet mode. Existing jobs, results and credentials remain intact, while new builds wait. This prevents an initial browser-lab migration from unexpectedly publishing or deploying an application.

After reviewing the restored configuration, explicitly resume builds:

```bash
bash browser-lab/bin/lab resume-ci
```

This uses the restored administrator password privately, obtains Jenkins' CSRF crumb and cancels quiet mode. It records the choice outside Git and removes only the runner's own startup guard. To pause again:

```bash
bash browser-lab/bin/lab pause-ci
```

Neither command changes job configuration or credentials. Build and deployment permissions still belong to the existing Jenkins account and pipeline. Automatic deployment setup explicitly enables Jenkins through this command. The saved choice persists across lab restarts. Its current browser deployment stage uses the existing dedicated Docker daemon and no Render hook.

## Automatic Actions deployment

For Experiments 14 and 19, a trusted `main` build must pass tests, publish its exact runtime image and finish the build job before the deployment job creates a GitHub Deployment. The lab agent polls GitHub outbound and verifies the repository, workflow, commit, successful build and expected image repository. It checks a restricted canary before activation, verifies the actual running API and rolls back a failed activation. Actions waits up to **600 seconds** for success and fails when the lab is unavailable or verification fails. Pull requests validate only.

The requester encrypts only its short-lived Actions callback token to the committed [public key](ci/deployment-public.pem). The private key stays in `private/browser-deployment-key.pem` with private permissions; the agent decrypts the callback token only in memory. No personal access token or public deployment endpoint is added. Preserve the private key and deployment state in private backups before deleting or rebuilding the Codespace. If the private key is lost, restore the matching backup or replace the key pair and committed public key before requesting further deployments.

Keep the Codespace and matching profile running while a pipeline deploys. The free quota does not provide an always-on target. `lab stop cicd` stops the agent and three apps; `lab pause-ci` pauses new Jenkins builds without deleting its jobs or results.

## Cost and retention

GitHub Free includes a limited Codespaces allowance, not unlimited permanent hosting. Keep the verified zero-spending budget, use the 2-core machine and stop the codespace when finished. Stopped codespaces still consume storage allowance. This Codespace uses a 30-minute idle timeout and 30-day inactive retention. Paid usage is blocked, but monthly free compute and storage limits still apply. Keep source in GitHub and private data backups outside the codespace before deletion or rebuild work.

No local Docker cleanup is performed by this runner. The cloud scripts have a Codespaces guard and stop only named experiment containers. Image and data deletion is intentionally absent.

Technical references: [Codespaces billing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces), [port forwarding](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace), [Docker-in-Docker feature state](https://github.com/devcontainers/features/blob/main/src/docker-in-docker/NOTES.md).
