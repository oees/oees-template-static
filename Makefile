# Quality gate and packaging for the static site. CI runs `make check`.
# Run `make check-fast` while you work, `make check` before you package, `make package` to send.
.PHONY: install dev format check-fast check package

install:
	npm ci

dev:
	npm run dev

format:
	npm run format

check-fast:
	npm run lint
	npm run format:check
	npm run typecheck
	npm run test

check: check-fast
	python3 -m unittest discover -s scripts
	npm run build
	npm audit --omit=dev --audit-level=high

package:
	python3 scripts/package.py
