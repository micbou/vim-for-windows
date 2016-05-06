#!/usr/bin/env python

import argparse
import requests
import os
import time

BINTRAY_BASE_URL = 'https://api.bintray.com/'
BINTRAY_UPLOAD_URL = (BINTRAY_BASE_URL +
                      'content/'
                      '{subject}/'
                      '{repo}/'
                      '{package}/'
                      '{version}/'
                      '{file_path}')
BINTRAY_PUBLISH_URL = (BINTRAY_BASE_URL +
                       'content/'
                       '{subject}/'
                       '{repo}/'
                       '{package}/'
                       '{version}/'
                       'publish')
BINTRAY_DOWNLOAD_LIST_URL = (BINTRAY_BASE_URL +
                             'file_metadata/'
                             '{subject}/'
                             '{repo}/'
                             '{file_path}')
BINTRAY_VERSION_URL = (BINTRAY_BASE_URL +
                       'packages/'
                       '{subject}/'
                       '{repo}/'
                       '{package}/'
                       'versions/'
                       '{version}')

# Interval between two retries (in seconds).
RETRY_INTERVAL = 10


def bintray_upload(args):
    args.filepath = (args.filepath if args.filepath else
                     os.path.basename(args.file_input))

    params = {
        'publish': 1 if args.publish else 0,
        'override': 1 if args.override else 0,
        'explode': 1 if args.explode else 0
    }

    url = BINTRAY_UPLOAD_URL.format(subject=args.subject,
                                    repo=args.repo,
                                    package=args.package,
                                    version=args.version,
                                    file_path=args.filepath)

    with open(args.file_input, 'rb') as f:
        response = requests.put(url,
                                data=f,
                                params=params,
                                auth=(args.username,
                                      args.api_key))

    if response.status_code != 201:
        raise RuntimeError('Bintray upload failed with message: {0}'
                           .format(response.text))


def bintray_publish(args):
    json = {
        'discard': True if args.discard else False,
        'publish_wait_for_secs': -1
    }

    url = BINTRAY_PUBLISH_URL.format(subject=args.subject,
                                     repo=args.repo,
                                     package=args.package,
                                     version=args.version)

    response = requests.post(url,
                             json=json,
                             auth=(args.username,
                                   args.api_key))

    if response.status_code != 200:
        raise RuntimeError('Publish failed with status code: {0}'
                           .format(response.status_code))


def bintray_file_in_download_list(args):
    json = {
        'list_in_downloads': True if args.action == 'add' else False
    }

    url = BINTRAY_DOWNLOAD_LIST_URL.format(subject=args.subject,
                                           repo=args.repo,
                                           file_path=args.filepath)

    response = requests.put(url,
                            json=json,
                            auth=(args.username,
                                  args.api_key))

    if response.status_code != 200:
        action = 'Adding' if args.action == 'add' else 'Removing'
        raise RuntimeError('{0} file in download list failed with status '
                           'code: {1}'.format(action, response.status_code))


def delete_version(args):
    url = BINTRAY_VERSION_URL.format(subject=args.subject,
                                     repo=args.repo,
                                     package=args.package,
                                     version=args.version)

    response = requests.delete(url,
                               auth=(args.username,
                                     args.api_key))

    if response.status_code != 200:
        raise RuntimeError('Deleting version failed with status code: {0}'
                           .format(response.status_code))


def update_version(args):
    json = {
        'desc': args.desc,
    }

    if args.github_release_notes_file:
        json['github_release_notes_file'] = args.github_release_notes_file
    if args.github_use_tag_release_notes:
        json['github_use_tag_release_notes'] = (
            args.github_use_tag_release_notes)
    if args.vcs_tag:
        json['vcs_tag'] = args.vcs_tag
    if args.released:
        json['released'] = args.released

    url = BINTRAY_VERSION_URL.format(subject=args.subject,
                                     repo=args.repo,
                                     package=args.package,
                                     version=args.version)

    response = requests.patch(url,
                              json=json,
                              auth=(args.username,
                                    args.api_key))

    if response.status_code != 200:
        raise RuntimeError('Updating version failed with status code: {0}'
                           .format(response.status_code))


def retries(function, args):
    max_retries = args.retries
    nb_retries = 0
    while True:
        try:
            function(args)
        except RuntimeError as error:
            nb_retries = nb_retries + 1
            print('ERROR: {0}. Retry {1}.'.format(error, nb_retries))
            if nb_retries > max_retries:
                raise RuntimeError('Number of retries exceeded ({0}). '
                                   'Aborting.'.format(max_retries))
            time.sleep(RETRY_INTERVAL)
        else:
            return True


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str,
                        help='bintray username (default: value from '
                             '"bintray_username" environment variable.')
    parser.add_argument('--api-key', type=str,
                        help='bintray API key (default: value from '
                             '"bintray_api_key" environment variable.')
    parser.add_argument('--retries', type=int, default=3,
                        help='number of retries before bailing out '
                             '(default: 3).')

    subparsers = parser.add_subparsers(
        title='subcommands',
        help='list of subcommands')

    # Bintray upload
    parser_upload = subparsers.add_parser(
        'upload',
        help='upload to bintray'
    )
    parser_upload.add_argument('repo', type=str,
                               help='bintray repository.')
    parser_upload.add_argument('package', type=str,
                               help='bintray package.')
    parser_upload.add_argument('version', type=str,
                               help='bintray version.')
    parser_upload.add_argument('file_input', type=str,
                               help='file to upload.')
    parser_upload.add_argument('--subject', type=str,
                               help='bintray account (default: username).')
    parser_upload.add_argument('--filepath', type=str,
                               help='bintray file path (default: file input '
                                    'basename).')
    parser_upload.add_argument('--publish', action='store_true',
                               help='publish the uploaded artifact as part '
                                    'of uploading.')
    parser_upload.add_argument('--override', action='store_true',
                               help='overwrite already published artifact.')
    parser_upload.add_argument('--explode', action='store_true',
                               help='unknown behavior.')
    parser_upload.set_defaults(func=bintray_upload)

    # Publish content
    parser_publish = subparsers.add_parser(
        'publish',
        help='publish uploaded content'
    )
    parser_publish.add_argument('repo', type=str,
                                help='bintray repository.')
    parser_publish.add_argument('package', type=str,
                                help='bintray package.')
    parser_publish.add_argument('version', type=str,
                                help='bintray version.')
    parser_publish.add_argument('--subject', type=str,
                                help='bintray account (default: username).')
    parser_publish.add_argument('--discard', action='store_true',
                                help='discard uploaded content instead of '
                                     'publishing it.')
    parser_publish.set_defaults(func=bintray_publish)

    # Add or remove a file in download list
    parser_download_list = subparsers.add_parser(
        'download-list',
        help='add or remove a file in download list'
    )
    parser_download_list.add_argument('repo', type=str,
                                      help='bintray repository.')
    parser_download_list.add_argument('filepath', type=str,
                                      help='bintray file path.')
    parser_download_list.add_argument('action', type=str,
                                      choices=['add', 'remove'],
                                      default='add',
                                      help='add or remove file '
                                           '(default: add).')
    parser_download_list.add_argument('--subject', type=str,
                                      help='bintray account '
                                           '(default: username).')
    parser_download_list.set_defaults(func=bintray_file_in_download_list)

    # Delete version
    parser_delete_version = subparsers.add_parser(
        'delete-version',
        help='delete the specified version.'
    )
    parser_delete_version.add_argument('repo', type=str,
                                       help='bintray repository.')
    parser_delete_version.add_argument('package', type=str,
                                       help='bintray package.')
    parser_delete_version.add_argument('version', type=str,
                                       help='bintray version.')
    parser_delete_version.add_argument('--subject', type=str,
                                       help='bintray account '
                                            '(default: username).')
    parser_delete_version.set_defaults(func=delete_version)

    # Update version
    parser_update_version = subparsers.add_parser(
        'update-version',
        help='update the information of the specified version.'
    )
    parser_update_version.add_argument('repo', type=str,
                                       help='bintray repository.')
    parser_update_version.add_argument('package', type=str,
                                       help='bintray package.')
    parser_update_version.add_argument('version', type=str,
                                       help='bintray version.')
    parser_update_version.add_argument('desc', type=str,
                                       help='version description.')
    parser_update_version.add_argument('--subject', type=str,
                                       help='bintray account '
                                            '(default: username).')
    parser_update_version.add_argument('--github-release-notes-file',
                                       type=str,
                                       help='GitHub release notes file.')
    parser_update_version.add_argument('--github-use-tag-release-notes',
                                       type=str,
                                       help='GitHub use tag release notes.')
    parser_update_version.add_argument('--vcs-tag', type=str,
                                       help='VCS tag.')
    parser_update_version.add_argument('--released', type=str,
                                       help='release date.')
    parser_update_version.set_defaults(func=update_version)

    args = parser.parse_args()

    if not args.username:
        if 'bintray_username' not in os.environ:
            raise RuntimeError('"bintray_username" environment '
                               'variable not set')
        args.username = os.environ['bintray_username']
    if not args.api_key:
        if 'bintray_api_key' not in os.environ:
            raise RuntimeError('"bintray_api_key" environment '
                               'variable not set')
        args.api_key = os.environ['bintray_api_key']

    if not args.subject:
        args.subject = args.username

    return args


def main():
    args = parse_arguments()
    retries(args.func, args)


if __name__ == '__main__':
    main()
