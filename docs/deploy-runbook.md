# Deploy runbook: static site

For the OEES tech team. The marketing owner sends a zip that `make package` built. You import it into a repository, review it, and merge. **The merge is the deploy, and not merging is the veto.**

Each command says if it is **READ-ONLY** or if it **CHANGES** something.

## How the deploy works

- One App Platform app per site, named `<site>-prod`, in region `ams`. It holds no secrets.
- App Platform deploys every push to `main` by itself (`deploy_on_push: true`), through the DigitalOcean GitHub app. There is no deploy workflow in `.github/`.
- `main` changes only through a pull request. The protection of `main` (step 1.1) is the only gate before production. A pull request runs `ci`: `make check` and the gitleaks `secrets` job.
- App Platform keeps its own copy of the app spec. You create the app from `.do/app.yaml` once (step 1.8). A later change to `.do/app.yaml` reaches the app only when you apply it (section 2).
- Never change the app only in the DigitalOcean console. Put the change in `.do/app.yaml` in a pull request, then apply it.

## 1. First import of a new site

1. **CHANGES** — Create `oees/<site>` from this template (**Use this template** on GitHub). Allow rebase merging only. Protect `main` with a ruleset or a branch protection rule:
   - Require a pull request with one approval.
   - Require the `ci` checks `check` and `secrets`, and require the branch to be up to date before the merge.
   - Block force pushes and deletions.
   - Allow nobody to bypass the rule, admins included: every push to `main` deploys.
2. **CHANGES** — Import the zip on a branch, so that the pull request shows only the owner's work against the template:

   ```bash
   unzip <site>-<stamp>.zip -d /tmp/import
   git clone git@github.com:oees/<site>.git && cd <site>
   git switch -c import/<yyyy-mm-dd>
   rsync -a --delete --exclude .git /tmp/import/<site>/ ./
   git add -A && git commit -m "Import <site> from marketing"
   git push -u origin HEAD
   ```

   Open a pull request into `main`.

3. **READ-ONLY** — Review:
   - `HANDOFF.md`, and every item under **For review**.
   - The diff of `.do/`, `.github/`, `Makefile`, `vite.config.ts`, `package.json` and `scripts/`. A new workflow that deploys is a reason to veto.
   - The `ci` result.
   - The agent configuration: `uvx --from git+https://github.com/oees/agents@v1.0.0 oees-agents check`. It fails if someone edited the generated rules.
4. **CHANGES** — Fix what the owner could not know, on the same branch:
   - In `.do/app.yaml`: `name: <site>-prod` and `github.repo: oees/<site>`.
   - In `.oees-agents.toml`: the `[project]` name and description. Then run `uvx --from git+https://github.com/oees/agents@v1.0.0 oees-agents update` and commit the result.
5. **CHANGES** — Once per repository: give the DigitalOcean GitHub app access to `oees/<site>`.
6. **READ-ONLY** — `doctl apps spec validate .do/app.yaml`
7. **CHANGES** — Merge. No app exists yet, so nothing deploys. To veto, request changes or close the pull request, and tell the owner what to change.
8. **CHANGES** — Create the app from `main`. App Platform builds `main` and deploys it. From now on, each merge deploys.

   ```bash
   git switch main && git pull
   doctl apps create --spec .do/app.yaml
   ```

9. **READ-ONLY** — Verify: `doctl apps list-deployments APP_ID` shows the latest deployment `ACTIVE`. Then smoke test: the home page, two other pages, an unknown path (it shows `404.html`), and the page source (the content is in the HTML).

## 2. Change the app configuration

A merged change to `.do/app.yaml` does not change the app by itself. After the merge:

1. **READ-ONLY** — Compare the live spec with the file:

   ```bash
   doctl apps spec get APP_ID > /tmp/<site>-live.yaml
   diff /tmp/<site>-live.yaml .do/app.yaml
   ```

2. If the diff shows more than the change in the pull request, someone changed the app in the console. Bring that change into `.do/app.yaml` in a pull request first.
3. **READ-ONLY** — `doctl apps spec validate .do/app.yaml`
4. **CHANGES** — `doctl apps update APP_ID --spec .do/app.yaml`. This replaces the whole configuration of the app, and deploys it.

## 3. A domain

1. Agree the hostname with the owner.
2. **CHANGES** — Add the `domains:` block to `.do/app.yaml` in a pull request. After the merge, apply it as in section 2.
3. **CHANGES** — Point DNS at the app as App Platform shows for the domain. Wait for the certificate.

## 4. Later rounds

The owner continues from the last zip that they have, not from `main`. So the changes that you make on `main` are not in their copy.

- After each merge, send the owner a zip of `main` to continue from:

  ```bash
  git archive --format=zip --prefix=<site>/ -o <site>-main.zip main
  ```

- Import each new zip as in step 1.2, on a new branch from `main`. In the review, look for lines that the import removes. An import from an old copy undoes your changes, for example the `domains:` block.
