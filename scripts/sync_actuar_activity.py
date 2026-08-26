import os, sys, subprocess, json, urllib.request

def main():
    actuar_token = os.environ.get("ACTUAR_TOKEN")
    if not actuar_token:
        print("ERROR: ACTUAR_TOKEN environment variable not set.")
        sys.exit(1)

    query = """
    query {
      user(login: "Matheus-Allvz-Actuar") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={"Authorization": f"Bearer {actuar_token}", "User-Agent": "Python"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            total = cal["totalContributions"]
            print(f"Total Actuar Contributions: {total}")
            
            active_days = []
            for week in cal["weeks"]:
                for day in week["contributionDays"]:
                    count = day["contributionCount"]
                    if count > 0:
                        active_days.append((day["date"], count))
            
            print(f"Syncing {len(active_days)} active days...")
            
            subprocess.run(["git", "config", "user.name", "Matheus-Allvz"], check=True)
            subprocess.run(["git", "config", "user.email", "workingaccount.matheus@gmail.com"], check=True)
            
            sync_file = "actuar-activity-sync.txt"
            
            for date_str, count in active_days:
                commit_date = f"{date_str}T12:00:00"
                env = os.environ.copy()
                env["GIT_AUTHOR_DATE"] = commit_date
                env["GIT_COMMITTER_DATE"] = commit_date
                
                with open(sync_file, "a", encoding="utf-8") as f:
                    f.write(f"Synced {count} contributions on {date_str}\n")
                
                subprocess.run(["git", "add", sync_file], check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"chore(sync): Actuar activity on {date_str}"],
                    env=env,
                    check=False
                )
                
            print("SUCCESS: Actuar contributions synced to local Git history!")
            
    except Exception as e:
        print("Error syncing activity:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
