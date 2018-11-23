#!/usr/bin/env bash

# Do NOT set -v or -x or your GitHub API token will be leaked!
set -ue # exit with nonzero exit code if anything fails

echo "Parse memote.ini for values."
deployment=$(awk -F '=' '{if (! ($0 ~ /^;/) && $0 ~ /deployment/) print $2}' memote.ini | tr -d ' ')
location=$(awk -F '=' '{if (! ($0 ~ /^;/) && $0 ~ /location/) print $2}' memote.ini | tr -d ' ')

echo "Configure Travis git user."
git config --global user.email "deploy@travis-ci.org"
git config --global user.name "Travis CI Deployment Bot"

if [[ "${TRAVIS_PULL_REQUEST}" != "false" || "${TRAVIS_REPO_SLUG}" != "SysBioChalmers/yeast-GEM" ]]; then
    echo "Untracked build."
    memote run --ignore-git
    echo "Skip deploy."
    exit 0
else
    # Always need the deployment branch available locally for storing results.
    git checkout "${deployment}"
    git checkout "${TRAVIS_BRANCH}"
    echo "Tracked build."
    memote run --skip-unchanged
    echo "Start deploy to ${deployment}..."
fi

# Generate the history report on the deployment branch.
output="history_report.html"
echo "Generating updated history report '${output}'."
memote report history --filename="/tmp/${output}"
git checkout "${deployment}"
mv "/tmp/${output}" ./

# Add, commit and push the files.
git add "${output}"
git commit -m "Travis report #${TRAVIS_BUILD_NUMBER}"
git push --quiet "https://${GITHUB_TOKEN}@github.com/${TRAVIS_REPO_SLUG}.git" "${deployment}" > /dev/null

echo "Your new report will be available at http://sysbiochalmers.github.io/yeast-GEM/ in a moment."
