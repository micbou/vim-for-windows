#!/usr/bin/env python

import argparse
import os
import subprocess
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', 'vim')
SOURCES_DIR = os.path.join(ROOT_DIR, 'src')
TESTS_DIR = os.path.join(SOURCES_DIR, 'testdir')

MSVC_BIN_DIR = os.path.join('..', '..', 'VC')


def get_msvc_dir(args):
    if args.msvc == 11:
        return os.path.join(os.environ['VS110COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 12:
        return os.path.join(os.environ['VS120COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 14:
        return os.path.join(os.environ['VS140COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 15:
        return get_msvc15_dir()
    raise RuntimeError('msvc parameter should be 11, 12, 14, or 15.')


def get_msvc15_dir():
    vswhere = os.path.join(os.environ['ProgramFiles(x86)'],
                           'Microsoft Visual Studio',
                           'Installer',
                           'vswhere.exe')
    if not os.path.exists(vswhere):
        raise RuntimeError('cannot find vswhere. '
                           'VS 2017 version 15.2 or later is required.')

    installation_path = subprocess.check_output(
        [vswhere, '-latest', '-property', 'installationPath']
    ).strip().decode('utf8')
    return os.path.join(installation_path, 'VC', 'Auxiliary', 'Build')


def get_vc_mod(arch):
    if arch == 64:
        return 'x86_amd64'
    return 'x86'


def get_nmake_cmd(args):
    msvc_dir = get_msvc_dir(args)
    vc_vars_script_path = os.path.join(msvc_dir, 'vcvarsall.bat')
    return [vc_vars_script_path, get_vc_mod(args.arch), '&', 'nmake.exe']


def test_vim(args):
    os.chdir(TESTS_DIR)

    gvim_path = os.path.join(SOURCES_DIR, 'gvim')

    # Register gvim in silent mode to avoid a dialog window when running the
    # tests. Otherwise, this will stuck runs on CI services.
    subprocess.check_call([gvim_path, '-silent', '-register'])

    nmake_cmd = get_nmake_cmd(args)

    test_cmd = nmake_cmd + ['-f', 'Make_dos.mak',
                            'VIMPROG={0}'.format(gvim_path)]
    if args.tests:
        for test in args.tests:
            root, _ = os.path.splitext(test)
            test_cmd.append(root + '.res')
        test_cmd.append('report')
    try:
        subprocess.check_call(test_cmd)
    finally:
        subprocess.check_call(nmake_cmd + ['-f', 'Make_dos.mak', 'clean'])


def get_arch_from_python_interpreter():
    if platform.architecture()[0] == '64bit':
        return 64
    return 32


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type=int, choices=[11, 12, 14, 15],
                        default=15, help='choose the Microsoft Visual '
                        'Studio version (default: %(default)s).')
    parser.add_argument('--arch', type=int, choices=[32, 64],
                        help='force architecture to 32 or 64 bits on '
                        'Windows (default: python interpreter architecture).')
    parser.add_argument('tests', nargs='*', help='list of tests')

    args = parser.parse_args()
    if not args.arch:
        args.arch = get_arch_from_python_interpreter()

    return args


def main():
    args = parse_arguments()
    test_vim(args)


if __name__ == '__main__':
    main()
