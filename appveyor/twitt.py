#!/usr/bin/env python

import argparse
import os
from twitter import *  # noqa


def set_twitter_argument(args, name):
    if not args.__dict__[name]:
        env_name = 'twitter_' + name
        if env_name not in os.environ:
            raise RuntimeError('{0} environment variable not '
                               'set'.format(env_name))
        args.__dict__[name] = os.environ[env_name]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--consumer-key', type=str,
                        help='Consumer Key')
    parser.add_argument('--consumer-secret', type=str,
                        help='Consumer Secret')
    parser.add_argument('--access-token', type=str,
                        help='Access Token')
    parser.add_argument('--access-token-secret', type=str,
                        help='Access Token Secret')
    parser.add_argument('status', type=str,
                        help='Tweet message')

    args = parser.parse_args()

    set_twitter_argument(args, 'consumer_key')
    set_twitter_argument(args, 'consumer_secret')
    set_twitter_argument(args, 'access_token')
    set_twitter_argument(args, 'access_token_secret')

    return args


def main():
    args = parse_arguments()
    twitter = Twitter(auth=OAuth(args.access_token,
                                 args.access_token_secret,
                                 args.consumer_key,
                                 args.consumer_secret))
    twitter.statuses.update(status=args.status)


if __name__ == '__main__':
    main()
