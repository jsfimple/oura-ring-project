import argparse
import json
from datetime import date

import auth
import oura_client
import poster


def cmd_auth(args):
    auth.run_oauth_setup()


def cmd_run(args):
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    access_token = oura_client.ensure_valid_access_token()
    bundle = oura_client.fetch_all(access_token, target_date)

    if args.dry_run:
        print(json.dumps(bundle, indent=2))
        return

    resp = poster.post_bundle(bundle)
    print(f"Posted bundle for {target_date}: routine responded {resp.status_code}")


def main():
    parser = argparse.ArgumentParser(description="Oura Ring morning report automation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("auth", help="Run one-time OAuth2 authorization setup")
    auth_parser.set_defaults(func=cmd_auth)

    run_parser = subparsers.add_parser("run", help="Refresh token, pull data, post to routine")
    run_parser.add_argument("--date", help="Target date (YYYY-MM-DD), defaults to today")
    run_parser.add_argument("--dry-run", action="store_true", help="Print bundle instead of posting it")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
