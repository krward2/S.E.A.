# SEA
A Scanning and Enumeration Automation Tool meant for CCDC DAC at White Sands Missile Range.

## Backup Procedure
Backups will be done through an automated Python script every 12 hours (twice a day).

If a backup is done but the most recent ZIP archive matches the current ZIP archive, no backup will be done.
If a backup is done and the most recent ZIP archive differs from the current ZIP archive, a backup will be done.

Every backup will be stored in a ZIP archive.
