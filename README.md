# OSRS-CLog_leaderboard
Pulls information about users from collectionlog.net API and outputs in a leaderboard format

Install Python if needed:

```https://www.python.org/downloads/```


To install the Requests module via CMD or Powershell:

```python -m pip install requests```

Update cloggers.txt with all the usernames you want to check for. eg
```
Name 1
Name 2
Name 3
```

Outputs into file 'clog_results.txt' with the following format:
```
Last updated DD/MM/YYYY

Rank 1 - NAME: 111/1111 (Status)
---
Rank 2 - NAME: 99/1111 (Status)
---
Rank 3 - NAME: 55/1111 (Status)
  etc
```
