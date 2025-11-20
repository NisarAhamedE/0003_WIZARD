#!/bin/sh
# Inject environment variables into React build

# Create runtime config
cat <<EOT > /usr/share/nginx/html/env-config.js
window._env_ = {
  REACT_APP_API_URL: "${REACT_APP_API_URL:-http://localhost:8000/api/v1}"
};
EOT
