dist:
	tar czvf tide-dist.tar.gz --exclude='*.swp' tide.py ui

.PHONY: dist
