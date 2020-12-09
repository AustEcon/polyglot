#!/usr/bin/env python3

import argparse
import getpass
import sys
import bitsv
import polyglot


def set_network(args):
    if args.testnet:
        network = 'test'
    elif args.scalingtestnet:
        network = 'stn'
    else:
        network = 'main'
    return network


def get_wif_securely():
    wif = ""
    while wif == "":
        wif = getpass.getpass("Enter private key in wif format:")
        if not wif:
            print("Was expecting a wif format private key but got an empty string. Try again.")
    return wif


def main():
    parser = argparse.ArgumentParser(description='Load files with Bitcoin SV.')
    parser.add_argument('file', help='filename')
    parser.add_argument('--download', action='store', dest='url', default=None,
                       help='Download from a url')
    parser.add_argument("--testnet", action="store_true", dest="testnet", default=False,
                       help="Use Testnet")
    parser.add_argument("--scaling-testnet", action="store_true", dest="scalingtestnet",
                       default=False, help="Use Scaling Testnet")
    args = parser.parse_args()
    if args.url:
        downloader = polyglot.Download(network=set_network(args))
        fields = downloader.download_url(args.url, args.file)
        for key, value in fields.items():
            if key == 'data':
                continue
            print(key, value)
    else:
        wif = get_wif_securely()
    
        try:
            bitsv.format.wif_checksum_check(wif)
            bitsv.format.wif_to_bytes(wif)
        except ValueError as e:
            print(f"'{wif}' is not a valid WIF format private key")
            sys.exit(1)
    
        uploader = polyglot.Upload(wif, network=set_network(args))
        txid = uploader.upload_easy(args.file)
        print('txid', txid)
