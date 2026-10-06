# Privacy: no access log (it would record place searches); errors only.
bind = "0.0.0.0:" + __import__("os").environ.get("PORT", "8080")
workers = int(__import__("os").environ.get("WEB_CONCURRENCY", "1"))  # one copy of the ~165 MB place index
threads = 4             # Swiss Ephemeris settings are per-thread; engine handles this
timeout = 30
accesslog = None
errorlog = "-"
loglevel = "warning"
preload_app = True   # load the place index once, share across workers
