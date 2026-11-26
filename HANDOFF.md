# Hand-off to OEES tech

> **Agent:** keep this file current while you work, in English. The OEES tech team reads it first when the zip arrives, and decides from it what to review before they deploy. Replace every `<…>`. Do not delete sections; write "None" where nothing applies.

## The site

| Item                  | Value                                                               |
| --------------------- | ------------------------------------------------------------------- |
| Name                  | `<site>` (the same as `name` in `package.json`; lowercase, hyphens) |
| What it is for        | <one or two sentences>                                              |
| Owner in marketing    | <name>                                                              |
| Public address wanted | <hostname, or "not decided">                                        |
| Launch date wanted    | <date, or "not decided">                                            |
| Template              | `oees-template-static` <version from TEMPLATE_VERSION>              |

## Pages

| Path | What it shows |
| ---- | ------------- |
| `/`  | <…>           |

## Personal data

<"None: the site collects no data from visitors." Or, for each item: the fields, the purpose, where the data goes, how long it is kept, and if the data protection officer (dpd@octopusenergy.es) was informed.>

## Outside services

Every service the browser loads or calls: fonts, analytics, tag managers, maps, video embeds, APIs. For each one: what it is, what it receives from the visitor, and if it waits for cookie consent.

<"None.">

## For review

Decisions that tech should check before the deploy. List each one with the reason:

- anything outside the template's stack (a new framework, library with a large footprint, or service);
- every change to `.do/app.yaml`, `.github/`, `Makefile`, `vite.config.ts`, the `package.json` scripts or `scripts/`;
- prices, tariffs or savings figures on a page, and where they come from;
- legal text that still needs approval (privacy policy, cookie notice, conditions);
- files larger than 5 MB.

<"None.">

## Checks

Run on <date>, in <where: for example "the Claude chat workspace">.

| Check             | Result                      | Notes |
| ----------------- | --------------------------- | ----- |
| `make check-fast` | <passed / failed / blocked> | <…>   |
| `make check`      | <passed / failed / blocked> | <…>   |

A blocked check is not a pass. Say what blocked it.
