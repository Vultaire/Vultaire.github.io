#!/usr/bin/env python3

# merge_balance_csvs.py - Merges Monarch balance history files.
# Copyright (C) 2025 Paul Goins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Please refer to the text of the license on the GNU website:
# https://www.gnu.org/licenses/gpl-3.0.html

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def main():
    args = parse_args()
    merge_balances(Path(args.input_dir), Path(args.output_file))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_dir')
    ap.add_argument('output_file')
    return ap.parse_args()


def merge_balances(input_dir: Path, output_file: Path):
    # When I first did an AI-generated version of this code, it used a naive "put-everything-in-one-dict" approach.
    # While inefficient, it was good enough.
    # While this code is written from scratch, I've copied that overall approach as it is "good enough" for our
    # purposes.
    merged_data = create_merged_balance_history_dict(input_dir)
    write_merged_csv(output_file, merged_data)


def create_merged_balance_history_dict(input_dir):
    merged_data = defaultdict(dict)   # Intended format: merged_data[dict][record_key] = balance
    for input_csv in input_dir.iterdir():
        with input_csv.open() as infile:
            # Header line for these files is: Date,Balance,Account
            reader = csv.DictReader(infile)
            for row in reader:
                # Let's compute our keys.
                # Assumption: only one row per date and account key.  But just in case, we will check for dupes.
                date = row['Date'].strip()
                # The "account key" is a combination of the input CSV's Path object and the 'Account' field.
                # At present there should only be a single unique 'Account' per CSV file.
                # But that may change in the future, *and* it may be possible to have a name collision between this and accounts in other CSV files.
                # This key avoids such accidental collisions.
                account_key = (input_csv, row['Account'].strip())

                if account_key in merged_data[date]:
                    print("WARNING: Reassigning balance for already-existing date and account key:", (date, account_key), file=sys.stderr)
                merged_data[date][account_key] = row['Balance'].strip()
    return merged_data


def write_merged_csv(output_file: Path, merged_data: dict):
    # Timestamps are in YYYY-MM-DD format, which can be lexicographically sorted.
    # Let's assume that remains true and just leverage that.
    #
    # We don't know how many columns we need, nor the names of the columns, until we walk the CSV files.  Let's do that first.
    # We'll also need to create a mapping of account keys to *unique* account names for when we walk through to write the combined file.

    # Pull all the account key objects.
    # To be more in line with what the Monarch UI shows, we'll want to sort in the order that the files were downloaded.
    account_key_set = set(account_key for date in merged_data for account_key in merged_data[date])
    account_keys = list(account_key_set)
    account_keys.sort(key=lambda key: key[0].stat().st_mtime)

    # Get the field names for the output CSV.
    fields = ["Date"]
    account_key_to_name = {}
    for account_key in account_keys:
        if account_key not in account_key_to_name:
            account_name = get_unique_account_name(account_key, fields)
            fields.append(account_name)
            account_key_to_name[account_key] = account_name

    # Now, walk and generate the CSV.
    with output_file.open(mode="w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fields)
        writer.writeheader()
        for date in sorted(merged_data):
            record = {"Date": date}
            for account_key, balance in merged_data[date].items():
                account_name = account_key_to_name[account_key]
                record[account_name] = balance
            writer.writerow(record)


def get_unique_account_name(account_key, fields):
    _, account_name_from_key = account_key
    account_name = account_name_from_key
    suffix_int = 1
    while account_name in fields:
        suffix_int += 1
        account_name = f'{account_name_from_key}_{suffix_int}'
    return account_name


if __name__ == "__main__":
    main()
