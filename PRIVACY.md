# Privacy Policy

This project is a personal, single-user automation script. It is not a public
service or product — it is run locally by its one author for their own use.

## What data it accesses

The script uses OAuth2 to connect to your own Oura Ring account and pull your
own daily health data (sleep, readiness, activity, heart rate, SpO2, stress,
resilience, cardiovascular age, VO2 max, workouts, sessions, and tags) from
Oura's v2 API.

## What happens to that data

- Data is pulled to your local machine only.
- It is bundled into a single JSON payload and sent directly to a private,
  self-hosted automation endpoint (a Claude Code Routine) that the author
  controls, in order to generate a personal daily health report.
- The data is not stored by this script beyond the local run, not shared with
  any third party, not sold, and not used for any purpose other than
  generating the author's own report.
- OAuth access and refresh tokens are stored locally on the author's machine
  (gitignored, never committed to source control) and are used solely to
  authenticate the author's own requests to Oura's API.

## Who can use this

This application is intended for use by its author only. It has not been
built or reviewed for use by the general public.

## Contact

Questions about this project: jsfimple1@gmail.com
