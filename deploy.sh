#!/bin/sh

# Exit on error
set -e

# Dump wq configuration object to file
db/manage.py dump_config --format amd > app/js/data/config.js

# Build javascript with wq.app
cd app;
wq build $1;

# Force important files through any unwanted server caching
cd ../;
sed -i "s/trywq.js/trywq.js?v="$1"/" htdocs-build/trywq.appcache
sed -i "s/trywq.css/trywq.css?v="$1"/" htdocs-build/trywq.appcache

# Preserve Django's static files (e.g. admin)
if [ -d htdocs/static ]; then
    cp -a htdocs/static htdocs-build/static
fi;

# Replace existing htdocs with new version
rm -rf htdocs;
mv -i htdocs-build/ htdocs;

# Restart Django
touch db/trywq/wsgi.py
