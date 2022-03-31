#!/bin/bash
mkdir /var/runit && \
mkdir /var/runit/nginx && \
/bin/bash -c "echo -e '"'#!/bin/bash\nexec nginx -g "daemon off;"\n'"' > /var/runit/nginx/run" && \
chmod +x /var/runit/nginx/run && \
ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/ && \
rm -rf /etc/nginx/sites-enabled/default && \
mkdir /var/runit/gunicorn && \
/bin/bash -c "echo -e '"'#!/bin/bash\nexec gunicorn -b 127.0.0.1:8000 --chdir /app app:app\n'"' > /var/runit/gunicorn/run" && \
chmod +x /var/runit/gunicorn/run