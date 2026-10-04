# Athenachka

This repository is a static narrative archive. Open `index.html` in a browser,
or serve the checkout using Python's standard library:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Then visit http://127.0.0.1:8000/. No npm installation or build is required.
Stop the server with Ctrl+C.

The reader pages provide HTML downloads for offline reading. The previously
advertised PDF files are absent from this checkout; no replacement PDFs are
claimed or generated.

Validate the archive and its local links with:

```sh
python -m unittest discover -s tests -v
```

Related public reading sites:
- https://athenachka.neocities.org
- https://athenachka-nexus.neocities.org
- https://athenachka.wordpress.com

Two downloads remain under explicit publication review holds:
`athenasglobalplan.html` and `avatarandgenius.html` still reference their absent
original PDFs. Both pages are preserved unchanged from the pinned public base.
The other 20 download links now resolve to existing HTML pages. The validator
permits only the two exact held links, verifies their original Git blobs, and
checks all other links. See `tests/publication_holds.json` for source identities
and held status.
