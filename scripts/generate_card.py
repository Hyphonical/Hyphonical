#!/usr/bin/env python3
"""generate_card.py — Renders the profile SVG with live GitHub data."""

import os
import requests
from datetime import datetime, timezone

GITHUB_USER = "Hyphonical"
TEMPLATE = "Template.svg"
OUTPUT = "Header.svg"

def time_ago(iso_timestamp: str) -> str:
	"""Convert an ISO timestamp to a human-readable 'X ago' string."""
	dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
	delta = datetime.now(timezone.utc) - dt
	seconds = int(delta.total_seconds())

	if seconds < 60:
		return f"{seconds}s ago"
	minutes = seconds // 60
	if minutes < 60:
		return f"{minutes}m ago"
	hours = minutes // 60
	if hours < 24:
		return f"{hours}h ago"
	days = hours // 24
	if days < 30:
		return f"{days}d ago"
	months = days // 30
	return f"{months}mo ago"


def fetch_repos(user: str, limit: int = 3) -> list[dict]:
	"""Fetch the most recently pushed-to repos for a user."""
	token = os.environ.get("GITHUB_TOKEN", "")
	headers = {"Accept": "application/vnd.github+json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"

	resp = requests.get(
		f"https://api.github.com/users/{user}/repos",
		headers=headers,
		params={
			"sort": "pushed",
			"direction": "desc",
			"per_page": limit,
			"type": "owner",
		},
	)
	resp.raise_for_status()
	repos = resp.json()

	results = []
	for repo in repos[:limit]:
		# Pad/truncate name to align columns nicely
		name = repo["full_name"]
		visibility = "Public" if not repo["private"] else "Private"
		ago = time_ago(repo["pushed_at"])
		results.append({"name": name, "visibility": visibility, "ago": ago})
	return results


def pad(text: str, width: int) -> str:
	"""Pad text with spaces to a fixed width for terminal alignment."""
	return text + " " * max(0, width - len(text))


def main():
	repos = fetch_repos(GITHUB_USER, limit=3)

	with open(TEMPLATE, "r", encoding="utf-8") as f:
		svg = f.read()

	for i, repo in enumerate(repos, start=1):
		svg = svg.replace(f"{{{{REPO_{i}_NAME}}}}", pad(repo["name"], 28))
		svg = svg.replace(f"{{{{REPO_{i}_VIS}}}}", pad(repo["visibility"], 10))
		svg = svg.replace(f"{{{{REPO_{i}_AGO}}}}", repo["ago"])

	with open(OUTPUT, "w", encoding="utf-8") as f:
		f.write(svg)

	print(f"✅ Generated {OUTPUT} with {len(repos)} repos")


if __name__ == "__main__":
	main()