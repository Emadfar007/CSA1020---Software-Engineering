# CSA1020 Browser Docker Lab

Run the Docker experiments in the private GitHub Codespaces browser environment. Images, build cache, containers and persistent task data live on the cloud machine, so Docker Desktop is not required on the laptop after migration is verified.

[Open the existing browser IDE](https://miserable-cobweb-4j9pjv79r7w7fjrqw.github.dev/) · [Manage, resume or stop the Codespace](https://github.com/codespaces)

Sign in as **Emadfar007**. The Codespace is named `miserable-cobweb-4j9pjv79r7w7fjrqw`. Resume it if stopped; app links work only after their experiment profile is started. Keep all forwarded ports **Private**.

[Cloud migration verification, 27 October 2026](verification-2026-10-27.json) records the restored data, application tests, Kubernetes resume check and independent receiver engine.

| Experiment | Start command from the repository root | Private browser app |
|---|---|---|
| 11 | `bash browser-lab/bin/lab start 11` | [Orbital Fieldnotes](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8087.app.github.dev/) |
| 12 | `bash browser-lab/bin/lab start 12 --kubernetes` | [Docker API](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8088.app.github.dev/) · [Kubernetes NodePort](https://miserable-cobweb-4j9pjv79r7w7fjrqw-30088.app.github.dev/) |
| 13 | `bash browser-lab/bin/lab start 13` | [Jenkins](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/) · [Job and saved results](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/) |
| 14 | No cloud lab profile required | [FocusLane](https://focuslane-exp14.onrender.com/) · [Actions](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-14-cd.yml) |
| 16 | `bash browser-lab/bin/lab start 16` | [Morrow Task Studio](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8096.app.github.dev/) |
| 17 | `bash browser-lab/bin/lab start 17` | [Builder A](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8097.app.github.dev/) · [Receiver B](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8098.app.github.dev/) |

Use the browser terminal from the repository root:

```bash
bash browser-lab/bin/lab status
bash browser-lab/bin/lab start 11
bash browser-lab/bin/lab start 12
bash browser-lab/bin/lab start 12 --kubernetes
bash browser-lab/bin/lab start 13
bash browser-lab/bin/lab start 16
bash browser-lab/bin/lab start 17
bash browser-lab/bin/lab urls
bash browser-lab/bin/lab stop all
```

Start one experiment at a time. Starting a profile stops the other lab profiles without deleting their data or images. No application starts automatically when Codespaces opens. Experiment 12 starts the standalone API by default; `--kubernetes` also starts its real kind cluster and NodePort. Experiment 17 starts both its builder and isolated receiver. Experiment 14 already runs through hosted GitHub Actions and Render; `lab start 14` displays those existing links.

## Private browser access

The devcontainer forwards ports 8087, 8088, 30088, 8090, 8096, 8097 and 8098. GitHub forwards them privately by default. Confirm **Private** visibility in the Ports tab before testing. `lab urls` prints the actual `https://CODESPACENAME-PORT.app.github.dev/` addresses; a URL responds only when that profile is running. Do not make Jenkins or the other test ports public.

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
| `tools/` | Verified pinned kind and kubectl binaries |

The Docker-in-Docker feature additionally supplies its own persistent Docker and containerd state volumes. Do not commit private backups, databases, certificates, passwords or tokens to the public experiment repository. The runner does not copy credentials automatically. Restore the private Jenkins files before `lab start 13`; it refuses to invent replacement credentials. Restore Morrow's task files with owner `10001:10001` and Jenkins home with owner `1000:1000` before starting those experiments.

Morrow's seven tasks and original activity history, plus Jenkins configuration and job history, were restored and verified. Browser-only preferences for the old localhost sites stay in that browser origin; they are not automatically copied to the new cloud URLs. The migration does not remove browser profiles or saved browser data.

`LAB_DATA_DIR` can override the data directory when needed. `LAB_EXP11_IMAGE` and `LAB_EXP13_IMAGE` can select migrated registry images; without these, the runner builds their existing Dockerfiles in the cloud when the original local image names are unavailable. Published Experiments 12, 16 and 17 use verified immutable image digests.

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

Neither command changes job configuration or credentials. Build and deployment permissions still belong to the existing Jenkins account and pipeline.

## Cost and retention

GitHub Free includes a limited Codespaces allowance, not unlimited permanent hosting. Keep the verified zero-spending budget, use the 2-core machine and stop the codespace when finished. Stopped codespaces still consume storage allowance. This Codespace uses a 30-minute idle timeout and 30-day inactive retention. Paid usage is blocked, but monthly free compute and storage limits still apply. Keep source in GitHub and private data backups outside the codespace before deletion or rebuild work.

No local Docker cleanup is performed by this runner. The cloud scripts have a Codespaces guard and stop only named experiment containers. Image and data deletion is intentionally absent.

Technical references: [Codespaces billing](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces), [port forwarding](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace), [Docker-in-Docker feature state](https://github.com/devcontainers/features/blob/main/src/docker-in-docker/NOTES.md).
