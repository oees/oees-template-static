# Deploy runbook: static site

For the OEES tech team. The marketing owner sends a zip that `make package` built. You import it into a repository, review it, and merge. **The merge is the deploy, and not merging is the veto.**

Each command says if it is **READ-ONLY** or if it **CHANGES** something.

## How the deploy works

- One App Platform app per site, named `<site>-prod`, in region `ams`. The whole app configuration is `.do/app.yaml`. It holds no secrets.
- A pull request runs `ci` (`make check` and the gitleaks `secrets` job). A merge to `main` runs `ci` again. When it passes, `deploy` applies `.do/app.yaml` with `digitalocean/app_action`, in the GitHub environment `production`.
- `deploy_on_push` is `false`. CI is the only way in. The first run of `deploy` creates the app.
- Each deploy applies the whole spec. A setting made only in the DigitalOcean console disappears at the next deploy.

## 1. First import of a new site

1. **CHANGES** — Create `oees/<site>` from this template (**Use this template** on GitHub). Allow rebase merging only. Protect `main`. Require the `ci` checks `check` and `secrets`.
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
   - The diff of `.do/`, `.github/`, `Makefile`, `vite.config.ts`, `package.json` and `scripts/`.
   - The `ci` result.
   - The agent configuration: `uvx --from git+https://github.com/oees/agents@v1.0.0 oees-agents check`. It fails if someone edited the generated rules.
4. **CHANGES** — Fix what the owner could not know, on the same branch:
   - In `.do/app.yaml`: `name: <site>-prod` and `github.repo: oees/<site>`. If they do not match the repository, `deploy` fails before it changes anything.
   - In `.oees-agents.toml`: the `[project]` name and description. Then run `uvx --from git+https://github.com/oees/agents@v1.0.0 oees-agents update` and commit the result.
5. **CHANGES** — Once per repository: give the DigitalOcean GitHub app access to `oees/<site>`. Create the environment `production` with the secret `DIGITALOCEAN_ACCESS_TOKEN`.
6. **READ-ONLY** — `doctl apps spec validate .do/app.yaml`
7. **CHANGES** — Merge. `deploy` creates `<site>-prod` and deploys it. To veto, request changes or close the pull request, and tell the owner what to change.
8. **READ-ONLY** — Smoke test: the home page, two other pages, an unknown path (it shows `404.html`), and the page source (the content is in the HTML).

## 2. A domain

1. Agree the hostname with the owner.
2. **CHANGES** — Add the `domains:` block to `.do/app.yaml` in a pull request.
3. **CHANGES** — Point DNS at the app as App Platform shows for the domain. Wait for the certificate.

## 3. Later rounds

The owner continues from the last zip that they have, not from `main`. So the changes that you make on `main` are not in their copy.

- After each merge, send the owner a zip of `main` to continue from:

  ```bash
  git archive --format=zip --prefix=<site>/ -o <site>-main.zip main
  ```

- Import each new zip as in step 1.2, on a new branch from `main`. In the review, look for lines that the import removes. An import from an old copy undoes your changes, for example the `domains:` block.
