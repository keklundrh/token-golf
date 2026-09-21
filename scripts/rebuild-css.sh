#!/bin/bash
# rebuild-css.sh - Rebuild Tailwind CSS
# Usage: ./scripts/rebuild-css.sh

set -e

echo "Rebuilding Tailwind CSS..."

# Check if we're in a container or on host
if [ -f "/.dockerenv" ]; then
    # Inside container
    npm run tailwind:build
else
    # On host - use Podman
    podman run --rm \
        -v "$(pwd)/static:/app/static:z" \
        -v "$(pwd)/app:/app/app:z" \
        -v "$(pwd)/templates:/app/templates:z" \
        -v "$(pwd)/tailwind.config.js:/app/tailwind.config.js:z" \
        -v "$(pwd)/package.json:/app/package.json:z" \
        -w /app \
        node:20-alpine \
        sh -c "npm install --silent && npm run tailwind:build"
fi

echo "✓ Tailwind CSS rebuilt successfully"
echo "  Output: static/css/output.css"
