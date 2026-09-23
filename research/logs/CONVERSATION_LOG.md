# Conversation / Decision Log

## 2026-09-23

User reported a GitHub Pages 404 while visiting the root host `https://vishnuvcr.github.io/`.

Diagnosis: `Paper-Trade-v1` is a GitHub Pages **project site**, not the account-level user site. GitHub project sites are served at `https://<owner>.github.io/<repositoryname>/`.

Action: documented the correct URL as `https://vishnuvcr.github.io/Paper-Trade-v1/`, changed the Pages workflow to deploy on every push to `main`, and triggered a deployment via the resulting commit.

No manuscript is being generated.