# Path to the virtual environment python
VENV_PYTHON = .venv/bin/python3
PYTHON_SCRIPT = scripts/split-bib.py
BIBNAME = rougier
BIBFILE = data/$(BIBNAME).bib
BIBDIR = _bibliography
BIBSTAMP = $(BIBDIR)/.last-update
BIBSTYLE = data/rougier.csl

# Variables for webdav mount
REMOTE_URL = https://webdav.labri.fr/perso/nrougier
MOUNT_PATH = /Volumes/nrougier

all: render

publish: render
	@if ! mount | grep -q "on $(MOUNT_PATH) "; then \
		@echo "Target not mounted. Attempting to mount $(REMOTE_URL)..."; \
		@open "nodevice://$(REMOTE_URL)" || open "$(REMOTE_URL)"; \
		@echo "Waiting for mount to settle..."; \
		@sleep 5; \
	fi
	@if [ ! -d $(MOUNT_PATH) ]; then \
		@echo "Error: Could not mount $(MOUNT_PATH). Please mount manually."; \
		exit 1; \
	fi
	@echo "Uploading..."; \
	rsync --recursive --copy-links --verbose --inplace --update --delete --delete-after --delete-excluded --exclude-from=data/rsync-exclude.txt _site/ $(MOUNT_PATH)/


$(BIBSTAMP): $(BIBFILE) $(PYTHON_SCRIPT)
	@echo "Processing bibliography"
	@$(VENV_PYTHON) $(PYTHON_SCRIPT) $(BIBFILE) $(BIBDIR)
	@touch $(BIBSTAMP)

render: $(BIBSTAMP) $(BIBSTYLE)
	@echo "Rendering website"
	@quarto render --incremental
	@cd _site && ln -sf ../external/* . || true
	@cd _site && ln -sf ../images/* images/ 2> /dev/null || true
#       The commands take care of linking old material in the new website
#       using absolute paths to avoid recursion with rsync.
	@cd _site && ln -sf /Users/rougier/Documents/Homepage/images/* \
                            /Users/rougier/Documents/Homepage/_site/images/
	@cd _site && ln -sf /Users/rougier/Documents/Homepage/thumbnails/* \
                            /Users/rougier/Documents/Homepage/_site/thumbnails/


preview: $(BIBSTAMP) $(BIBSTYLE)
	quarto preview .

clean:
	rm -rf $(BIBDIR)
	rm -rf _site/
