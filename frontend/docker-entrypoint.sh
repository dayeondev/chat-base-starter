#!/bin/sh
set -e

# Generate runtime config from environment variables
cat > /usr/share/nginx/html/config.js << EOF
window.__ENV__ = {
  VITE_API_URL: '${VITE_API_URL:-http://localhost:8080}'
};
EOF

echo "Runtime config generated: VITE_API_URL=${VITE_API_URL:-http://localhost:8080}"

# Start nginx
exec nginx -g 'daemon off;'
