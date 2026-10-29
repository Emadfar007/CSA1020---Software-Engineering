# CSA1020 — Software Engineering

Software engineering experiments by **Emadfar007**.

[Open all 25 experiments](#all-25-experiments) · [Browser Docker lab](browser-lab/README.md) · [Docker troubleshooting guide](<reports/Docker Troubleshooting Guide Causes and Fixes.docx>)

## Browser Docker lab

Docker Experiments **11, 12, 13, 14, 16, 17, 18 and 19** have an on-demand private GitHub Codespaces runtime. Docker images, build cache and application data run on the cloud machine rather than the laptop's Docker Desktop engine. Experiments 13, 14 and 19 also use this lab as their current automatic deployment target; original Render records remain available in their reports.

[Open the browser IDE](https://miserable-cobweb-4j9pjv79r7w7fjrqw.github.dev/) · [Manage or restart the Codespace](https://github.com/codespaces) · [Browser lab guide](browser-lab/README.md)

Sign in as **Emadfar007**, resume the Codespace if stopped, and run the command for the experiment before opening its private app link:

| Experiment | Start command in the browser terminal | Open the application |
| --- | --- | --- |
| 11 Orbital Fieldnotes | `bash browser-lab/bin/lab start 11` | [Website](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8087.app.github.dev/) |
| 12 ParcelPilot | `bash browser-lab/bin/lab start 12 --kubernetes` | [Docker API](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8088.app.github.dev/) · [Kubernetes NodePort](https://miserable-cobweb-4j9pjv79r7w7fjrqw-30088.app.github.dev/) |
| 13 ReleaseHarbor | `bash browser-lab/bin/lab start 13` | [ReleaseHarbor](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8091.app.github.dev/) · [Jenkins](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/) · [Verified build 8](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/8/) |
| 14 FocusLane | `bash browser-lab/bin/lab start 14` | [FocusLane](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8094.app.github.dev/) · [Verified run 6.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740905728) |
| 16 Morrow | `bash browser-lab/bin/lab start 16` | [Task studio](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8096.app.github.dev/) |
| 17 Meridian Atlas | `bash browser-lab/bin/lab start 17` | [Builder A](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8097.app.github.dev/) · [Receiver B](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8098.app.github.dev/) |
| 18 SproutHouse | `bash browser-lab/bin/lab start 18` | [Seed library](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8180.app.github.dev/) · [Headlamp dashboard](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8181.app.github.dev/c/SproutHouse-Lab/deployments?namespace=sprouthouse-exp18) |
| 19 Packlight | `bash browser-lab/bin/lab start 19` | [Packlight](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8099.app.github.dev/) · [Verified run 5.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740904579) |

**Start all three CI/CD targets:** `bash browser-lab/bin/lab start cicd` starts ReleaseHarbor, FocusLane and Packlight together, plus Jenkins and the outbound Actions deployment agent. Use `bash browser-lab/bin/lab stop cicd` to stop this group without deleting data.

Starting a profile stops the other lab profiles while keeping their data. Use `bash browser-lab/bin/lab stop all` and stop the Codespace when finished. Jenkins automatic polling uses the saved `lab resume-ci` choice; use `lab pause-ci` to pause new builds. Ports remain private and require the existing GitHub login. The Codespace has a **30-minute idle timeout** and **30-day inactive retention**. Paid usage is blocked; monthly free compute and storage limits still apply. Original Docker Desktop commands and screenshots remain the historical experiment record. Private Jenkins credentials and task databases stay outside this public repository.

## All 25 experiments

All **25 experiment reports** and **179 screenshot files** are included in this repository. Use each report link for the aim, tools required, algorithm, output screenshots and result; the adjacent links open the original work and the complete screenshot gallery.

**Access:** Trello, Figma, Jira, Confluence and private GitHub projects may require your existing sign-in. The websites for Experiments 02, 03, 09, 10 and 15 remain local testing apps; their launch instructions are in their reports. Browser Docker experiments require resuming the [Codespace](https://miserable-cobweb-4j9pjv79r7w7fjrqw.github.dev/) and starting the matching profile in the [lab guide](browser-lab/README.md).

**Automatic deployment update - 28 October 2026:** Experiments **13, 14 and 19** now target the existing private Codespaces lab. Run `bash browser-lab/bin/lab start cicd` before pushing application changes. Jenkins deploys Experiment 13 inside its dedicated TLS Docker daemon; Actions builds and publishes Experiments 14 and 19, then waits for the private deployment agent to verify and activate the exact images. An unavailable lab fails deployment clearly. Original Render services remain quota-suspended; active deployment stages no longer call Render. The **$0 budget blocks paid usage**, while monthly free quotas still apply. [Automatic deployment records](browser-lab/automatic-deployment-2026-10-28.json) · [Earlier runtime verification](browser-lab/verification-2026-10-28.json).

**Verified deliveries:** [Jenkins build #8](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/8/) · [FocusLane run 6.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740905728) · [Packlight run 5.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740904579). All three running APIs matched their deployed source/build identity, and the CI/CD group retained the new releases after a real stop/start.

| Experiment | Description | Report, original work and screenshots |
| --- | --- | --- |
| 01 | Trello Kanban board with five sample tasks and workflow simulation | [Kanban Board](experiments/experiment-01-kanban-board/README.md) · [Open Trello board](https://trello.com/b/TZ9X6tdQ/website-project-kanban-board) · [Screenshots](experiments/experiment-01-kanban-board/screenshots/) |
| 02 | Desktop Figma prototype and local bus booking website with accounts, editable tickets, and personal reviews | [Bus Ticket Booking](experiments/experiment-02-bus-ticket-booking/README.md) · [Open Figma design](https://www.figma.com/design/1Y71bhdPTjVX7d3ubsW6LV/Bus-Ticket-Booking-System---Prototype?node-id=11-177&p=f) · [Screenshots](experiments/experiment-02-bus-ticket-booking/screenshots/) |
| 03 | E-commerce mobile prototype in Figma, with a local shopping app and stakeholder review workflow | [E-commerce Stakeholder Prototype](experiments/experiment-03-ecommerce-mobile-app/README.md) · [Open Figma design](https://www.figma.com/design/eOVcbMChHuLdyBYFjy3JN3?node-id=5-210) · [Screenshots](experiments/experiment-03-ecommerce-mobile-app/screenshots/) |
| 04 | Jira Scrum project with eight prioritized stories, a one-week sprint, workflow simulation, and dated Timeline categories | [Jira Scrum](experiments/experiment-04-jira-scrum/README.md) · [Open Jira sprint board](https://emadfar2020.atlassian.net/jira/software/c/projects/CDS/boards/2) · [Screenshots](experiments/experiment-04-jira-scrum/screenshots/) |
| 05 | Library Management System requirements categorized and justified using MoSCoW in an Excel workbook | [Library MoSCoW Prioritization](experiments/experiment-05-library-moscow/README.md) · [Open Excel workbook](experiments/experiment-05-library-moscow/Library_Management_System_MoSCoW.xlsx) · [Screenshots](experiments/experiment-05-library-moscow/screenshots/) |
| 06 | Jira and Confluence integration for Library Management System task tracking and sprint progress monitoring | [Jira and Confluence Integration](experiments/experiment-06-jira-confluence/README.md) · [Open Confluence overview](https://emadfar2020.atlassian.net/wiki/spaces/OOP/pages/1114113/Library+Management+System+Project+Overview) · [Screenshots](experiments/experiment-06-jira-confluence/screenshots/) |
| 07 | Task Management System requirements prioritized using MoSCoW and Kano in Jira, with a sample sprint and progress reporting | [Task Management Prioritization](experiments/experiment-07-task-management-prioritization/README.md) · [Open Jira decision record](https://emadfar2020.atlassian.net/browse/TMS-17) · [Screenshots](experiments/experiment-07-task-management-prioritization/screenshots/) |
| 08 | Online Learning Platform requirements prioritized using MoSCoW and Kano in Jira, with a sample sprint, timeline, and progress reporting | [Online Learning Prioritization](experiments/experiment-08-online-learning-prioritization/README.md) · [Open Jira board](https://emadfar2020.atlassian.net/jira/software/projects/OLP/boards/5) · [Screenshots](experiments/experiment-08-online-learning-prioritization/screenshots/) |
| 09 | Git/GitHub fork, clone, feature branch, pull request, disclosed self-review, follow-up fixes, and merge | [GitHub Collaboration](experiments/experiment-09-github-collaboration/README.md) · [Open collaboration PR](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/1) · [Screenshots](experiments/experiment-09-github-collaboration/screenshots/) |
| 10 | Real Git branch divergence, two-file merge conflict, manual combined resolution, and a FairSeat feature pull request | [Branching and Merge Conflicts](experiments/experiment-10-merge-conflicts/README.md) · [Open conflict-resolution PR](https://github.com/Emadfar007/CSA1020---Software-Engineering/pull/1) · [Screenshots](experiments/experiment-10-merge-conflicts/screenshots/) |
| 11 | Original static website packaged in a Docker image and served locally by Nginx, with a healthy container and verified browser workflow | [Docker Static Website](experiments/experiment-11-docker-static-website/README.md) · [Browser lab - start 11](browser-lab/README.md) · [Screenshots](experiments/experiment-11-docker-static-website/screenshots/) |
| 12 | Flask delivery-estimate API built and pushed with Docker, then deployed to Kubernetes through NodePort, with scaling and pod-recovery verification | [Flask, Docker and Kubernetes](experiments/experiment-12-flask-docker-kubernetes/README.md) · [Browser lab - start 12](browser-lab/README.md) · [Screenshots](experiments/experiment-12-flask-docker-kubernetes/screenshots/) |
| 13 | Browser Jenkins CI/CD with tested Docker images, commit polling and verified automatic deployment inside its private TLS Docker daemon | [Jenkins CI/CD with Docker](experiments/experiment-13-jenkins-cicd/README.md) · [Open ReleaseHarbor](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8091.app.github.dev/) · [Jenkins](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/) · [Screenshots](experiments/experiment-13-jenkins-cicd/screenshots/) |
| 14 | GitHub Actions testing and Docker Hub publication with verified automatic deployment through the private browser-lab agent | [GitHub Actions Continuous Deployment](experiments/experiment-14-github-actions-cd/README.md) · [Open FocusLane](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8094.app.github.dev/) · [Open Actions workflow](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-14-cd.yml) · [Screenshots](experiments/experiment-14-github-actions-cd/screenshots/) |
| 15 | Team project with module branches, reviewed pull requests, follow-up commits, genuine conflict resolution and a verified KitCrew application | [Team Version Control](experiments/experiment-15-team-version-control/README.md) · [Open private team repository](https://github.com/Emadfar007/kitcrew-team-project) · [Screenshots](experiments/experiment-15-team-version-control/screenshots/) |
| 16 | Persistent Flask to-do app containerized with Docker, verified task workflows and restart recovery, and published Docker Hub image | [Morrow Flask To Do App](experiments/experiment-16-flask-todo-docker/README.md) · [Browser lab - start 16](browser-lab/README.md) · [Screenshots](experiments/experiment-16-flask-todo-docker/screenshots/) |
| 17 | Original static website built, tagged and pushed to Docker Hub, then pulled and verified on an isolated receiving Docker engine | [Docker Hub Push and Pull](experiments/experiment-17-dockerhub-push-pull/README.md) · [Browser lab - start 17](browser-lab/README.md) · [Screenshots](experiments/experiment-17-dockerhub-push-pull/screenshots/) |
| 18 | Three-tier seed library on Kubernetes with Nginx, Flask, persistent PostgreSQL, real Headlamp monitoring and frontend scaling | [Multi-Container Kubernetes Application](experiments/experiment-18-sprouthouse-kubernetes/README.md) · [Browser lab - start 18](browser-lab/README.md) · [Screenshots](experiments/experiment-18-sprouthouse-kubernetes/screenshots/) |
| 19 | Flask application tested and published by GitHub Actions, then automatically deployed and verified in the private browser lab | [Flask CI/CD with GitHub Actions](experiments/experiment-19-github-actions-flask/README.md) · [Open Packlight](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8099.app.github.dev/) · [Open Actions workflow](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-19-cicd.yml) · [Screenshots](experiments/experiment-19-github-actions-flask/screenshots/) |
| 20 | Private personal repository initialized with a README, cloned locally, updated, staged, committed and pushed with verified Git history | [GitHub Repository Setup](experiments/experiment-20-github-repository-setup/README.md) · [Open private personal repository](https://github.com/Emadfar007/little-milestones-journal) · [Screenshots](experiments/experiment-20-github-repository-setup/screenshots/) |
| 21 | Existing public repository cloned locally and a one-line README clarification saved, with the original edit left uncommitted | [Clone and Edit a Repository](experiments/experiment-21-clone-and-edit/README.md) · [Open source repository](https://github.com/Emadfar007/learnloop-collaboration-demo) · [Screenshots](experiments/experiment-21-clone-and-edit/screenshots/) |
| 22 | Saved README change staged, committed with the exact message Updated README, and pushed with matching local and remote commits | [Commit and Push Changes](experiments/experiment-22-commit-and-push/README.md) · [Open pushed commit](https://github.com/Emadfar007/learnloop-collaboration-demo/commit/e711339b1c18a6258cbf7de1973ab0e9bbe23217) · [Screenshots](experiments/experiment-22-commit-and-push/screenshots/) |
| 23 | Approved same-account collaborator simulation in a second clone, followed by git pull origin main and verification of the update | [Pull Collaborator Updates](experiments/experiment-23-pull-collaborator-updates/README.md) · [Open pulled update](https://github.com/Emadfar007/learnloop-collaboration-demo/commit/8d9569910648791e4a0531233889c0ab402e1217) · [Screenshots](experiments/experiment-23-pull-collaborator-updates/screenshots/) |
| 24 | feature-login branch, standalone Python login function, pushed feature commit and a merged pull request into main | [Feature Branch and Login Pull Request](experiments/experiment-24-feature-login-pull-request/README.md) · [Open merged login PR](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/3) · [Screenshots](experiments/experiment-24-feature-login-pull-request/screenshots/) |
| 25 | Existing fork cloned and fetched, additive JSON progress export feature pushed on a new branch, and an open pull request into the user's fork | [Fork, Feature Branch and Pull Request](experiments/experiment-25-fork-feature-pull-request/README.md) · [Open feature PR](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/4) · [Screenshots](experiments/experiment-25-fork-feature-pull-request/screenshots/) |

Each experiment includes only Aim, Tools Required, Algorithm, Output Screenshots, and Result.

## Experiments completed on 28 October 2026

| Experiment | Open the work or verification | Report and screenshots |
| --- | --- | --- |
| 18 - Multi-container Kubernetes | [SproutHouse app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8180.app.github.dev/) · [Kubernetes dashboard](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8181.app.github.dev/c/SproutHouse-Lab/deployments?namespace=sprouthouse-exp18) | [Experiment 18](experiments/experiment-18-sprouthouse-kubernetes/README.md) |
| 19 - Flask CI/CD | [Packlight browser app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8099.app.github.dev/) · [Verified browser deployment run 5.1](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40740904579) | [Experiment 19](experiments/experiment-19-github-actions-flask/README.md) |
| 20 - Repository setup | [Original private project](https://github.com/Emadfar007/little-milestones-journal) · [README snapshot](experiments/experiment-20-github-repository-setup/project/README.md) | [Experiment 20](experiments/experiment-20-github-repository-setup/README.md) |
| 21 - Clone and save an edit | [Saved README](experiments/experiment-21-clone-and-edit/project/README.md) · [Change patch](experiments/experiment-21-clone-and-edit/evidence/README-change.patch) | [Experiment 21](experiments/experiment-21-clone-and-edit/README.md) |
| 22 - Commit and push | [Updated README commit](https://github.com/Emadfar007/learnloop-collaboration-demo/commit/e711339b1c18a6258cbf7de1973ab0e9bbe23217) | [Experiment 22](experiments/experiment-22-commit-and-push/README.md) |
| 23 - Pull updates (simulation) | [Update pulled from GitHub](https://github.com/Emadfar007/learnloop-collaboration-demo/commit/8d9569910648791e4a0531233889c0ab402e1217) | [Experiment 23](experiments/experiment-23-pull-collaborator-updates/README.md) |
| 24 - Login feature branch | [Merged pull request #3](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/3) · [Login function](https://github.com/Emadfar007/learnloop-collaboration-demo/blob/main/login.py) | [Experiment 24](experiments/experiment-24-feature-login-pull-request/README.md) |
| 25 - Fork and feature PR | [Open pull request #4](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/4) · [Feature branch](https://github.com/Emadfar007/learnloop-collaboration-demo/tree/feature/progress-export) | [Experiment 25](experiments/experiment-25-fork-feature-pull-request/README.md) |

Experiment 18 requires the private Codespace to be running. Experiment 19 now uses the same private browser lab; start its profile or the three-app `cicd` group before opening Packlight. The original Experiment 20 project remains private; its submitted README snapshot is included here. Experiment 23 explicitly records a two-clone simulation under Emadfar007.

## Quick access - experiments completed on 26 October 2026

| Experiment | Open the application | Open tools and progress | Full report and screenshots |
| --- | --- | --- | --- |
| 11 - Orbital Fieldnotes | [Private browser website](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8087.app.github.dev/) | [Health check](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8087.app.github.dev/healthz) | [Experiment 11](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-11-docker-static-website#quick-access-links) |
| 12 - ParcelPilot | [Kubernetes app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-30088.app.github.dev/) · [Docker app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8088.app.github.dev/) | [API specification](https://miserable-cobweb-4j9pjv79r7w7fjrqw-30088.app.github.dev/openapi.json) · [Docker Hub](https://hub.docker.com/r/coastrider7/csa1020-exp12-parcelpilot-api/tags) | [Experiment 12](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-12-flask-docker-kubernetes#quick-access-links) |
| 13 - ReleaseHarbor | [ReleaseHarbor browser app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8091.app.github.dev/) | [Jenkins job](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/) · [Latest successful build](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8090.app.github.dev/job/ReleaseHarbor-CICD/lastSuccessfulBuild/) · [Render](https://dashboard.render.com/web/srv-dbflq8vb9u1s73de444g) | [Experiment 13](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-13-jenkins-cicd#quick-access-links) |
| 14 - FocusLane | [FocusLane browser app](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8094.app.github.dev/) | [GitHub Actions](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/workflows/experiment-14-cd.yml) · [Docker Hub](https://hub.docker.com/r/coastrider7/csa1020-exp14-focuslane/tags) · [Render](https://dashboard.render.com/web/srv-dbfnbggm7kps739nrok0) | [Experiment 14](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-14-github-actions-cd#quick-access-links) |
| 15 - KitCrew | [Local application](http://127.0.0.1:4845/) | [Private team repository](https://github.com/Emadfar007/kitcrew-team-project) · [Module reviews](https://github.com/Emadfar007/kitcrew-team-project/pulls?q=is%3Apr) · [Passing checks](https://github.com/Emadfar007/kitcrew-team-project/actions/runs/40360742707) | [Experiment 15](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-15-team-version-control#quick-access-links) |

Each report's **Tools Required → Quick access links** table includes the current app, source, screenshots, checks and platform links. Docker experiment app links below use private Codespaces ports and require the profile command listed above. KitCrew remains a separate local app on port 4845. GitHub and Jenkins management use their existing logins. Current app links use Codespaces; the original Render deployments remain quota-suspended.

## Experiment 16 quick access

| Open the app | Container image | Source and configuration | Report and screenshots |
| --- | --- | --- | --- |
| [Morrow browser workspace](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8096.app.github.dev/) · [Readiness](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8096.app.github.dev/readyz) | [Docker Hub](https://hub.docker.com/r/coastrider7/csa1020-exp16-morrow/tags) | [Dockerfile](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/experiments/experiment-16-flask-todo-docker/Dockerfile) · [Compose](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/experiments/experiment-16-flask-todo-docker/compose.yaml) | [Report and quick links](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-16-flask-todo-docker#quick-access-links) · [Ten screenshots](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-16-flask-todo-docker/screenshots) |

Morrow now runs in the private browser lab. Run `bash browser-lab/bin/lab start 16` from the repository root, then open its app link. Its task database stays private in `/workspaces/.lab-data/morrow` when the profile stops.

## Experiment 17 quick access

| Open the websites | Published image | Docker commands and source | Report and screenshots |
| --- | --- | --- | --- |
| [Builder A](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8097.app.github.dev/) · [Receiver B](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8098.app.github.dev/) | [Docker Hub tags](https://hub.docker.com/r/coastrider7/csa1020-exp17-meridian-atlas/tags) | [Dockerfile](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/experiments/experiment-17-dockerhub-push-pull/Dockerfile) · [Actual commands and output](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/experiments/experiment-17-dockerhub-push-pull/evidence/docker-commands-and-output.txt) | [Report and quick links](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-17-dockerhub-push-pull#quick-access-links) · [Twelve screenshots](https://github.com/Emadfar007/CSA1020---Software-Engineering/tree/main/experiments/experiment-17-dockerhub-push-pull/screenshots) · [Verified results](https://github.com/Emadfar007/CSA1020---Software-Engineering/blob/main/experiments/experiment-17-dockerhub-push-pull/screenshots/12-verification-summary.jpg) |

Run `bash browser-lab/bin/lab start 17` to open both private Codespaces environments. Receiver B remains an isolated-engine simulation; both builder and receiver run on the cloud machine. Docker Hub and recorded evidence are available independently of the running profile.

## Experiment previews

### Kanban board

![Trello Kanban board with To Do, In-Progress and Done lists](experiments/experiment-01-kanban-board/screenshots/kanban-board.png)

### Bus booking desktop prototype

![Desktop trip search screen designed in Figma](experiments/experiment-02-bus-ticket-booking/screenshots/01-search-figma.png)

### E-commerce mobile prototype

![Editable Figma shopping flow and stakeholder comparison](experiments/experiment-03-ecommerce-mobile-app/screenshots/01-figma-flow.png)

### Jira Scrum project

![Active sample sprint with To Do, In Progress, and Done work](experiments/experiment-04-jira-scrum/screenshots/07-sample-progress-board.jpg)

The sample Jira project includes a dated Timeline and detailed ownership, acceptance criteria, and dependencies. Its current simulated progress snapshot shows four stories To Do, three In Progress, and one Done. Original sprint-start and sprint-end screenshots are included in Experiment 04.

### Library Management System priorities

![MoSCoW summary and justified Library Management System requirements](experiments/experiment-05-library-moscow/screenshots/01-requirements-and-summary.png)

Experiment 05 includes a downloadable Excel workbook with all ten requirements, impact, feasibility, and priority justification. The workbook can also be imported into Google Sheets.

### Library Management System task tracking

![Confluence overview with linked Jira tasks and overall sprint completion](experiments/experiment-06-jira-confluence/screenshots/01-confluence-overview.jpg)

Experiment 06 links seven Jira stories to a Confluence project overview. Its simulated checkpoint shows two Done, three In Progress, and two To Do tasks, with a manually updated completion snapshot of **28.6%**.

### Task Management System prioritization

![Native Jira MoSCoW and Kano classifications for the Task Management System](experiments/experiment-07-task-management-prioritization/screenshots/01-requirement-comparison.jpg)

Experiment 07 includes twelve requirements across four feature epics, independent MoSCoW and Kano fields, detailed rationale, eight tested filters, 26 prerequisite links, and nine screenshots. Its one-week sample sprint demonstrates To Do, In Progress, In Review, and Done work. Kano classifications remain unvalidated hypotheses, and workflow statuses represent simulated progress.

### Online Learning Platform prioritization

![Native Jira MoSCoW and Kano classifications for the Online Learning Platform](experiments/experiment-08-online-learning-prioritization/screenshots/06-priority-matrix.jpg)

Experiment 08 includes all six requested features within nine detailed requirements, three epics, 16 prerequisite links, seven tested model filters, and ten screenshots. The one-week sample sprint demonstrates progress across four workflow stages. Kano classifications are unvalidated hypotheses, and workflow progress is simulated.

### Git and GitHub collaboration

![Merged LearnLoop pull request with the feature and follow-up commits](experiments/experiment-09-github-collaboration/screenshots/08-merged-pull-request.jpg)

Experiment 09 includes ten screenshots documenting a fork of octocat/Spoon-Knife, a working LearnLoop dashboard, two feature commits, review feedback, passing checks, and [merged pull request #1](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/1). Its navigation follow-up adds distinct Learning path, My progress, and Workflow guide views, verified across 16 browser checkpoints and merged in [pull request #2](https://github.com/Emadfar007/learnloop-collaboration-demo/pull/2). All 13 tests passed. Only Emadfar007 was used, so the review is explicitly a self-review informed by assistant code inspection, without independent human approval. The merges target the user's fork's main branch.

### Git branching and merge conflicts

![FairSeat workshop planner after preserving both branches' requirements](experiments/experiment-10-merge-conflicts/screenshots/04-fairseat-dashboard.jpg)

Experiment 10 demonstrates genuine conflicts in the seat allocator and release policy, generated through two local clones using Emadfar007. The manual resolution preserves VIP-first ordering, overflow waiting lists, capacity validation, and valid attendee records. The experiment includes captured Git output, nine screenshots, a local evidence journal, 20 passing tests, and ten planner browser checks. [Pull request #1](https://github.com/Emadfar007/CSA1020---Software-Engineering/pull/1) is merged into main, preserving the actual two-parent conflict-resolution commit and publishing the completed report and app.

### Static website with Docker and Nginx

![Orbital Fieldnotes running through Docker and Nginx](experiments/experiment-11-docker-static-website/screenshots/01-website-docker.jpg)

Experiment 11 includes the Orbital Fieldnotes website, Dockerfile, Nginx configuration, a restricted build context, six screenshots, and recorded build/runtime evidence. The image was built successfully, the container became healthy, and all eleven browser checks passed. The website runs locally at port 8087, with no host directory mounts or public deployment.

### Flask API with Docker and Kubernetes

![ParcelPilot quote studio running through Kubernetes NodePort](experiments/experiment-12-flask-docker-kubernetes/screenshots/02-delivery-estimate.jpg)

Experiment 12 includes the ParcelPilot Flask API, interactive quote studio and JSON explorer, Dockerfile, Kubernetes manifests, deployment scripts, nine screenshots, and recorded verification evidence. The image was pushed to [Docker Hub](https://hub.docker.com/r/coastrider7/csa1020-exp12-parcelpilot-api/tags) and deployed by a local kind cluster with two Ready replicas through NodePort 30088. All 17 API tests passed; replica routing, scaling to three replicas and automatic replacement of a removed test pod were verified. The final replica count is two. Rates are illustrative and quotes are stateless.

### Jenkins CI/CD with Docker

![ReleaseHarbor running from the image deployed by Jenkins](experiments/experiment-13-jenkins-cicd/screenshots/01-cloud-workspace.jpg)

Experiment 13 includes the ReleaseHarbor app, a multi-stage Dockerfile, Jenkinsfile, local Jenkins setup, deployment helpers, nine original screenshots, a browser restoration screenshot and actual build evidence. A Git commit triggered Jenkins build #7, which passed 21 tests, verified the runtime container, published a build-specific Docker Hub image and deployed its exact digest to [the original Render deployment](https://releaseharbor-exp13.onrender.com/). The running app's source SHA and build number matched Jenkins. An intentional failed gate also blocked publication and deployment. The original demonstration used local Jenkins and Render Free; the current Jenkins pipeline deploys new releases into its private Codespaces Docker daemon.

### GitHub Actions continuous deployment

![FocusLane study planner automatically deployed through GitHub Actions](experiments/experiment-14-github-actions-cd/screenshots/02-cloud-app.jpg)

Experiment 14 includes FocusLane, an editable study-sprint planner, a multi-stage Dockerfile, a hosted GitHub Actions workflow, ten original screenshots, a browser restoration screenshot and actual delivery receipts. Merging [pull request #2](https://github.com/Emadfar007/CSA1020---Software-Engineering/pull/2) automatically triggered [run #3](https://github.com/Emadfar007/CSA1020---Software-Engineering/actions/runs/40353497794), which passed 23 application tests and four CI guard checks, pushed the tested image to Docker Hub, and deployed its exact digest to [the original Render deployment](https://focuslane-exp14.onrender.com). The cloud app's version 1.1.0, source commit and run 3.1 matched the pipeline. Pull requests validate without publishing or deploying. GitHub-hosted runners operate while the local computer is off. The active deployment job now waits for the running Codespaces agent to activate and verify the exact image; original Render services remain quota-suspended.

### Team project version control

![KitCrew equipment-sharing workspace](experiments/experiment-15-team-version-control/screenshots/01-kitcrew-catalog.jpg)

Experiment 15 archives KitCrew's team version-control workflow, application source, ten screenshots and recorded evidence. Three module branches were merged after documented COMMENT reviews, including a follow-up regression test and a genuine manually resolved policy conflict. All 26 module tests and 17 browser checks passed. The original workflow repository remains private; the report and captured evidence are available in this public experiment archive.

### Flask to do application with Docker

![Morrow Task Studio with a persistent task board](experiments/experiment-16-flask-todo-docker/screenshots/01-task-board.jpg)

Experiment 16 includes task creation and editing, priorities, deadlines, custom categories, search and filters, drag and drop, activity history, JSON import and export, and a persistent SQLite database. Its image passed 21 container tests, 37 live API checks and 18 browser checks; a real container restart preserved a saved task. Ten screenshots and the verified Docker Hub publication digest are included in its five-section report.

### Docker Hub push and pull

![Meridian Atlas running from the image pulled by Receiver B](experiments/experiment-17-dockerhub-push-pull/screenshots/11-receiver-website.jpg)

Experiment 17 includes an original interactive static website, Dockerfile, Nginx configuration, version and latest tags on Docker Hub, and twelve screenshots covering build, tag, push, pull and run. Receiver B began with an empty image store and a distinct engine ID. All five website files match across the source and both containers; 12 HTTP checks and 22 browser checks passed. The sample uses an approved isolated Docker engine on the same laptop to simulate a second machine.

## Local testing

For Experiment 15, run `npm start --prefix experiments/experiment-15-team-version-control/app` from the repository root and open `http://127.0.0.1:4845/`. Its [report](experiments/experiment-15-team-version-control/README.md) includes test commands and the branch/review/conflict workflow.

For Experiment 14, run `bash browser-lab/bin/lab start 14` in the Codespace and open [FocusLane in the browser](https://miserable-cobweb-4j9pjv79r7w7fjrqw-8094.app.github.dev/), or follow its [Docker commands and report](experiments/experiment-14-github-actions-cd/README.md) for local testing. Application changes pushed to `main` trigger the original hosted pipeline; its Render deployment stage remains quota-blocked. The browser profile runs the recorded successful image.

For Experiment 13, follow the [Jenkins CI/CD report](experiments/experiment-13-jenkins-cicd/README.md). On a fresh machine, run `./scripts/start-lab.ps1` from that experiment directory. When restarting an existing lab, supply its original private secret directory as documented. Open the local Jenkins job at `http://127.0.0.1:8090/job/ReleaseHarbor-CICD/`; commit polling operates while this computer, Docker and Jenkins are running.

For Experiment 12, follow its [report and commands](experiments/experiment-12-flask-docker-kubernetes/README.md). With Docker running, create the supplied kind cluster once, then run `./scripts/deploy.ps1` from the experiment directory. Access the application at `http://127.0.0.1:30088/` on the computer running the cluster. The API runs locally for testing; its container image is published to Docker Hub.

For Experiment 11, open a terminal in `experiments/experiment-11-docker-static-website/` with Docker running, then run:

```powershell
docker build --pull -t orbital-fieldnotes:1.0 .
docker run -d --name orbital-fieldnotes-exp11 -p 127.0.0.1:8087:80 orbital-fieldnotes:1.0
```

Open `http://127.0.0.1:8087/`. If the experiment's container already exists, use `docker start orbital-fieldnotes-exp11` instead of creating another container. See the Experiment 11 report for verification and stop commands.

Run `node experiments/experiment-10-merge-conflicts/app/scripts/serve.js` from the repository root and open `http://127.0.0.1:4831/`. The captured conflict journal is available at `/evidence/` on the same local server.

LearnLoop's updated application source is included in [Experiment 09's app folder](experiments/experiment-09-github-collaboration/app/). From the repository root, run `node experiments/experiment-09-github-collaboration/app/scripts/serve.js` and open `http://127.0.0.1:4829/learning-progress/`. The Learning path, My progress, and Workflow guide views share saved lesson progress.

The bus booking website and FORME e-commerce app use HTML, CSS, and JavaScript. Their source is included in Experiments 02 and 03. See each experiment's README for local testing instructions. Both apps use Node.js to run their loopback-only testing servers. SwiftBus includes local account registration/login, editable passenger and travel-point details, PDF tickets, and personal bus reviews.

Both apps are testing prototypes with sample data and simulated bookings or orders. They have not been deployed; no real reservations, payments, or email delivery are connected. Experiment 03 includes two interface directions and a local feedback and approval log; real stakeholder approval remains pending.
