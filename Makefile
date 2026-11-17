PORT ?= 8000

.PHONY: help run bump check-version icons

help:
	@echo "make run                  Start a local HTTPS server (PORT=$(PORT)) and show your local IP"
	@echo "make bump VERSION=x.y.z   Set the app version in index.html and version.json"
	@echo "make check-version        Check that index.html and version.json agree"
	@echo "make icons                Render the app icons (PNG) from icons/*.svg (needs rsvg-convert)"

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

icons:
	rsvg-convert -w 192 -h 192 icons/icon.svg -o icons/icon-192.png
	rsvg-convert -w 512 -h 512 icons/icon.svg -o icons/icon-512.png
	rsvg-convert -w 512 -h 512 icons/icon-maskable.svg -o icons/icon-maskable-512.png
	rsvg-convert -w 180 -h 180 icons/icon-maskable.svg -o icons/apple-touch-icon.png
