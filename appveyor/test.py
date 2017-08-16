#!/usr/bin/env python

import argparse
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', 'vim')
SOURCES_DIR = os.path.join(ROOT_DIR, 'src')
TESTS_DIR = os.path.join(SOURCES_DIR, 'testdir')

MSVC_BIN_DIR = os.path.join('..', '..', 'VC', 'bin')


def get_msvc_dir(args):
    if args.msvc == 11:
        return os.path.join(os.environ['VS110COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 12:
        return os.path.join(os.environ['VS120COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 14:
        return os.path.join(os.environ['VS140COMNTOOLS'], MSVC_BIN_DIR)
    raise RuntimeError('msvc parameter should be 11, 12, or 14.')


def test_vim(args):
    os.chdir(TESTS_DIR)

    msvc_dir = get_msvc_dir(args)

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.exists(nmake):
        raise RuntimeError('nmake tool not found.')

    gvim_path = os.path.join(SOURCES_DIR, 'gvim')

    # Register gvim in silent mode to avoid a dialog window when running the
    # tests. Otherwise, this will stuck runs on CI services.
    subprocess.check_call([gvim_path, '-silent', '-register'])

    test_cmd = [nmake, '-f',
                'Make_dos.mak',
                'VIMPROG={0}'.format(gvim_path)]
    if args.tests:
        for test in args.tests:
            root, _ = os.path.splitext(test)
            test_cmd.append(root + '.res')
        test_cmd.append('report')
    try:
        subprocess.check_call(test_cmd)
    finally:
        subprocess.check_call([nmake, '-f',
                               'Make_dos.mak',
                               'clean'])


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type=int, choices=[11, 12, 14],
                        default=14, help='choose the Microsoft Visual '
                        'Studio version (default: %(default)s).')
    parser.add_argument('tests', nargs='*', help='list of tests')

    return parser.parse_args()


def main():
    args = parse_arguments()
    test_vim(args)


if __name__ == '__main__':
    main()
