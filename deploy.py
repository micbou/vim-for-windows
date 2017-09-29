#!/usr/bin/env python

import argparse
import os
import subprocess
import re
import tempfile
import textwrap
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIM_DIR = os.path.join(SCRIPT_DIR, 'vim')

VIM_COMMIT = re.compile('patch (?P<version>.*): .* '
                        'Problem:(?:\s+)(?P<problem>.*) '
                        'Solution:(?:\s+)(?P<solution>.*)' )
COMMIT_SEPARATOR = '------'
CHANGELOG_LINE = '{version}: {problem} {solution}'


def replace_multiplespaces_by_one(string):
    return ' '.join(string.split())


def format_logs(patches):
    formatted_patches = []
    for patch in patches.split(COMMIT_SEPARATOR):
        onelined_patch = ' '.join(patch.strip().split('\n'))
        match = VIM_COMMIT.match(onelined_patch)
        if match:
            problem = replace_multiplespaces_by_one(match.group('problem'))
            solution = replace_multiplespaces_by_one(match.group('solution'))
            formatted_patch = CHANGELOG_LINE.format(
              version=match.group('version'),
              problem=problem,
              solution=solution)
            formatted_patches.append(formatted_patch)
    logs = []
    for patch in reversed(formatted_patches):
        log = textwrap.wrap(patch)
        formatted_log = ['- ' + log[0]]
        for line in log[1:]:
            formatted_log.append('  ' + line)
        logs.extend(formatted_log)
    return logs


def deploy(args):
    git = find_executable('git')
    if git is None:
        raise RuntimeError('git tool not found.')

    # Move to script folder
    os.chdir(SCRIPT_DIR)

    # Switch to master branch
    subprocess.check_call([git, 'checkout', 'master'])

    # Move to vim folder
    os.chdir(VIM_DIR)

    # Get current hash
    current_hash = subprocess.check_output(
      [git, 'rev-parse', 'HEAD']).strip().decode('utf8')

    # Pull vim changes
    subprocess.check_call(
      [git, 'pull', '--tags', '--force', 'origin', 'master'])

    # Check if upstream contains changes
    changes = subprocess.check_output([git, 'log', '--oneline',
                                       current_hash + '..HEAD'])
    if not changes:
        print('No upstream changes.')
        return

    # Format logs
    patches = subprocess.check_output(
      [git, 'log', '--pretty=format:%B{0}'.format(COMMIT_SEPARATOR),
       current_hash + '..HEAD']).strip().decode('utf8')
    logs = format_logs(patches)

    # Get the latest tag
    latest_commit = subprocess.check_output(
        [git, 'rev-list', '--tags', '--max-count=1']).strip().decode('utf8')
    latest_tag = subprocess.check_output(
        [git, 'describe', '--tags', latest_commit]).strip().decode('utf8')

    # Push to upstream if remote is not origin
    remote = subprocess.check_output(
      [git, 'rev-parse', '--abbrev-ref',
            'master@\{upstream\}']).strip().decode('utf8')
    remote, _ = remote.split('/')
    if remote != 'origin':
      subprocess.check_call(
        [git, 'push', '--force'])

    # Return to script folder
    os.chdir(SCRIPT_DIR)

    # Add changes
    subprocess.check_call([git, 'add', 'vim'])

    # Commit changes
    commit_message = ('Bump version to ' + latest_tag[1:] + '\n\n' +
                      '\n'.join(logs))

    # Get commit message from a temporary file
    with tempfile.NamedTemporaryFile(buffering=0,
                                     delete=False) as commit_message_file:
      commit_message_file.write(commit_message.encode('utf8'))
      subprocess.check_call([git, 'commit', '-F', commit_message_file.name])

    # Set latest tag to the last commit
    subprocess.check_call([git, 'tag', '-f', latest_tag])

    # Push the changes
    subprocess.check_call([git, 'push', '-f'])

    # Remove upstream tag in case it already exists
    if len(subprocess.check_output([git, 'ls-remote', 'origin', latest_tag])):
        subprocess.check_call([git, 'push', 'origin',
                               ':{0}'.format(latest_tag)])

    # Push the tag
    subprocess.check_call([git, 'push', 'origin', latest_tag])


def revert(args):
    git = find_executable('git')
    if git is None:
        raise RuntimeError('git tool not found.')

    # Switch to master branch
    subprocess.check_call([git, 'checkout', 'master'])

    # Reset to previous commit
    subprocess.check_call([git, 'reset', '--hard', 'HEAD~1'])

    # Update submodule
    subprocess.check_call([git, 'submodule', 'update'])

    # Get latest tag
    latest_commit = subprocess.check_output(
        [git, 'rev-list', '--tags', '--max-count=1']).strip().decode('utf8')
    latest_tag = subprocess.check_output(
        [git, 'describe', '--tags', latest_commit]).strip().decode('utf8')

    # Remove latest upstream tag in case it already exists
    if len(subprocess.check_output([git, 'ls-remote', 'origin', latest_tag])):
        subprocess.check_call([git, 'push', 'origin',
                               ':{0}'.format(latest_tag)])

    # Remove latest tag locally
    subprocess.check_call([git, 'tag', '-d', latest_tag])

    # Push the changes
    subprocess.check_call([git, 'push', '-f'])


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revert', action = 'store_true',
                        help = 'Revert to previous commit')
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.revert:
        revert(args)
    else:
        deploy(args)


if __name__ == '__main__':
    main()
