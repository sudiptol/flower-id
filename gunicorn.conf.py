# Settings for gunicorn, the production web server used online (Render).
# Gunicorn reads this file automatically when started with:  gunicorn app:app

import os

# Listen on the port Render chooses (it says which in the PORT setting); 8000 when trying it on the Mac.
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")

# Two copies of the app, so one slow identification doesn't block the next request.
workers = 2

# Stop any request still running after 40 seconds. This must be longer than every limit
# inside it: Wikipedia 5 s < Pl@ntNet 20 s < the page's own 35 s < 40 s here.
# Gunicorn's default is 30 s, which could cut off a slow identification.
timeout = 40
