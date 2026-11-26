# Troubleshooting a deploy: static site

Start with the app's **Activity** tab in the DigitalOcean console: it lists each deployment with its logs. For more, run these **read-only** commands:

```bash
doctl apps list-deployments APP_ID          # ACTIVE or ERROR?
doctl apps logs APP_ID site --type build    # build failures
doctl apps spec get APP_ID                  # the live config
```

| Symptom                                | Likely cause                                                                                        | Fix                                                                                                                          |
| -------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| A static site needs a secret           | It cannot have one: everything in it ships to the browser                                           | Move the feature to the Django template.                                                                                     |
| The build fails at dependency install  | `package-lock.json` is missing or out of date, or the Node major differs                            | Commit the lockfile. Keep `.nvmrc` and `engines.node` on the same major.                                                     |
| Spec validation fails on the documents | Both `error_document` and `catchall_document` are set                                               | Keep one. This template uses `error_document: 404.html`.                                                                     |
| A page path shows the 404 page         | The page is not an `index.html` in its own folder                                                   | Add `<path>/index.html`. `vite.config.ts` finds every `.html` file.                                                          |
| Blank page, or CSS and JS return 404   | `base` in `vite.config.ts` is not `/`, or `output_dir` is wrong                                     | Set `base: "/"` and `output_dir: dist`.                                                                                      |
| `.do/app.yaml` and the live app differ | Someone changed the app in the console, or nobody applied a merged spec change                      | Compare `doctl apps spec get APP_ID` with `.do/app.yaml`. Fix the file in a pull request, then apply it (runbook section 2). |
| A merge did not deploy                 | `deploy_on_push` is off in the live spec, or the DigitalOcean GitHub app cannot read the repository | Check `doctl apps spec get APP_ID` and the repository access of the GitHub app.                                              |
| A secret is in a zip or in git         | Committed or zipped by mistake                                                                      | Rotate it now. If it reached git, scrub the history.                                                                         |
