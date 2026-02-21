# Path to the virtual environment python
VENV_PYTHON = .venv/bin/python3
PYTHON_SCRIPT = scripts/split-bib.py
BIBNAME = rougier
BIBFILE = data/$(BIBNAME).bib
BIBDIR = _bibliography
BIBSTAMP = $(BIBDIR)/.last-update
BIBSTYLE = data/rougier.csl
# Variables for webdav mount
WEBDAV_REMOTE = https://webdav.labri.fr/perso/nrougier
WEBDAV_LOCAL = /Volumes/nrougier

all: render

publish: 
	@if ! mount | grep -q "on $(WEBDAV_LOCAL) "; then          \
		echo -n "Target not mounted. Trying to mount... "; \
		osascript -e 'mount volume "$(WEBDAV_REMOTE)"';    \
		if ! mount | grep -q "on $(WEBDAV_LOCAL) "; then   \
			echo "Failed to mount $(WEBDAV_REMOTE).";  \
			exit 1;                                    \
		fi;                                                \
		echo "Success!";                                   \
	fi
	@echo "Uploading website..."; 
	@rsync --recursive --copy-links --verbose --size-only --update --delete --delete-after --delete-excluded --exclude-from=data/rsync-exclude.txt _site/ $(WEBDAV_LOCAL)/
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
