#/usr/bin/env bash
set -e

CURRENT_COMMIT=$(git rev-parse HEAD)

ssh volumio <<EOF
  cd /data/plugins/miscellanea/peppy_screensaver/peppymeter/
  git fetch
  git checkout ${CURRENT_COMMIT}
EOF

for arg in "$@"; do
  if [ "$arg" == "--restart" ]; then
    ssh volumio 'sudo systemctl restart volumio'
    echo "Restarting..."
  fi
done
