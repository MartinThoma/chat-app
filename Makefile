PORT ?= 8000

.PHONY: help run bump check-version

help:
	@echo "make run                  Start a local web server (PORT=$(PORT)) and show your local IP"
	@echo "make bump VERSION=x.y.z   Set the app version in index.html and version.json"
	@echo "make check-version        Check that index.html and version.json agree"

run:
	@python3 serve.py $(PORT)

bump:
	@test -n "$(VERSION)" || { echo "Usage: make bump VERSION=x.y.z"; exit 1; }
	@perl -pi -e 's/^const APP_VERSION = ".*";/const APP_VERSION = "$(VERSION)";/' index.html
	@printf '{"version": "%s"}\n' "$(VERSION)" > version.json
	@$(MAKE) --no-print-directory check-version

check-version:
	@html=$$(sed -nE 's/^const APP_VERSION = "(.*)";/\1/p' index.html); \
	json=$$(python3 -c 'import json; print(json.load(open("version.json"))["version"])'); \
	if [ "$$html" = "$$json" ]; then echo "Version $$html"; \
	else echo "Version mismatch: index.html=$$html version.json=$$json"; exit 1; fi
