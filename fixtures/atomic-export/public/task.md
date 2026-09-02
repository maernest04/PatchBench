# Atomic export command

Update `export.py` so `export_items` atomically replaces the requested output file with a JSON array of the supplied items followed by a newline. If replacing the staged export fails, an existing output file must remain unchanged.
