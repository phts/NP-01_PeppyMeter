#/usr/bin/env bash
set -e

CURRENT_COMMIT=$(git rev-parse HEAD)

ssh volumio <<EOF
  cd /data/plugins/miscellanea/peppy_screensaver/peppymeter/
  git fetch
  git checkout np-01-config
  git stash
  git rebase --onto ${CURRENT_COMMIT} HEAD~1 np-01-config
  git stash pop
EOF
