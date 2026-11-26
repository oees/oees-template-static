# Troubleshooting a deploy: static site

Start with the `deploy` workflow run in GitHub Actions: it prints the App Platform build and deploy logs. For more, run these **read-only** commands:

```bash
doctl apps list-deployments APP_ID          # ACTIVE or ERROR?
doctl apps logs APP_ID site --type build    # build failures
doctl apps spec get APP_ID                  # the live config
```

| Symptom                                                            | Likely cause                                                                                           | Fix                                                                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `deploy` fails with "`NAME` is referenced in the spec but not set" | A `${NAME}` in `.do/app.yaml` has no `env:` line in `deploy.yml`, or the secret is not in `production` | A static site must not have secrets. Remove the `${NAME}`, or move the feature to the Django template. |
| The build fails at dependency install                              | `package-lock.json` is missing or out of date, or the Node major differs                               | Commit the lockfile. Keep `.nvmrc` and `engines.node` on the same major.                               |
| Spec validation fails on the documents                             | Both `error_document` and `catchall_document` are set                                                  | Keep one. This template uses `error_document: 404.html`.                                               |
| A page path shows the 404 page                                     | The page is not an `index.html` in its own folder                                                      | Add `<path>/index.html`. `vite.config.ts` finds every `.html` file.                                    |
| Blank page, or CSS and JS return 404                               | `base` in `vite.config.ts` is not `/`, or `output_dir` is wrong                                        | Set `base: "/"` and `output_dir: dist`.                                                                |
| Config changed back after a deploy                                 | Someone edited the app in the console. Each deploy applies the whole spec                              | Put the setting in `.do/app.yaml`.                                                                     |
| `deploy` skipped with "main is at …"                               | A newer commit reached `main`; its own run deploys                                                     | Nothing.                                                                                               |
| A secret is in a zip or in git                                     | Committed or zipped by mistake                                                                         | Rotate it now. If it reached git, scrub the history.                                                   |
