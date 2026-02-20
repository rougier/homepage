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
		@echo -n "Target not mounted. Trying to mount... "; \
		@osascript -e 'mount volume "https://webdav.labri.fr/perso/nrougier"'
		@if ! mount | grep -q "on $(MOUNT_PATH) "; then \
			@echo "Failed to mount $(REMOVE_URL)."; \
			exit 1; \
		fi
	fi
	@echo "Success!"
	@echo -n "Uploading website..."; \
	rsync --recursive --copy-links --verbose --inplace --update --delete --delete-after --delete-excluded --exclude-from=data/rsync-exclude.txt _site/ $(MOUNT_PATH)/
	@echo "Done!"

$(BIBSTAMP): $(BIBFILE) $(PYTHON_SCRIPT)
	@echo "Processing bibliography"
	@$(VENV_PYTHON) $(PYTHON_SCRIPT) $(BIBFILE) $(BIBDIR)
	@touch $(BIBSTAMP)

render: $(BIBSTAMP) $(BIBSTYLE)
	@echo "Rendering website"
	@quarto render 
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
