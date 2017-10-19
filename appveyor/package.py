#!/usr/bin/env python

import argparse
import os
import re
import shutil
import subprocess
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', 'vim')
SOURCES_DIR = os.path.join(ROOT_DIR, 'src')
RUNTIME_DIR = os.path.join(ROOT_DIR, 'runtime')
NSIS_DIR = os.path.join(ROOT_DIR, 'nsis')
DOC_DIR = os.path.join(RUNTIME_DIR, 'doc')
XXD_DIR = os.path.join(SOURCES_DIR, 'xxd')
GVIM_EXT_DIR = os.path.join(SOURCES_DIR, 'GvimExt')
GVIM_EXT32_DIR = os.path.join(SOURCES_DIR, 'GvimExt32')
GVIM_EXT64_DIR = os.path.join(SOURCES_DIR, 'GvimExt64')
GVIM_EXT32_RUNTIME_DIR = os.path.join(RUNTIME_DIR, 'GvimExt32')
GVIM_EXT64_RUNTIME_DIR = os.path.join(RUNTIME_DIR, 'GvimExt64')
GVIM_NSIS_PATH = os.path.join(NSIS_DIR, 'gvim.nsi')
GVIM_PACKAGE_PATH = os.path.join(NSIS_DIR, 'gvim-package.exe')

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


def get_nmake_cmd(args, arch):
    msvc_dir = get_msvc_dir(args)
    vc_vars_script_path = os.path.join(msvc_dir, 'vcvarsall.bat')
    return [vc_vars_script_path, get_vc_mod(arch), '&', 'nmake.exe']


def generate_uganda_file():
    # Uganda manual is written in Vim doc so we need to apply some formatting
    # to it for the package.
    uganda_path = os.path.join(DOC_DIR, 'uganda.txt')
    nsis_uganda_path = os.path.join(DOC_DIR, 'uganda.nsis.txt')
    with open(uganda_path, "r") as uganda_file:
        lines = uganda_file.readlines()
    with open(nsis_uganda_path, "w") as nsis_uganda_file:
        for line in lines[:-1]:
            nsis_uganda_file.write(re.sub(r'[ \t]*\*[-a-zA-Z0-9.]*\*', '',
                                          line))


def rename_package(args):
    os.rename(GVIM_PACKAGE_PATH,
              os.path.join(NSIS_DIR, args.package))


def build_gvimext(args, arch):
    nmake_cmd = get_nmake_cmd(args, arch)

    os.chdir(GVIM_EXT_DIR)

    subprocess.check_call(nmake_cmd + ['clean', 'all'])


def generate_package(args):
    generate_uganda_file()

    shutil.copy(os.path.join(ROOT_DIR, 'vimtutor.bat'),
                os.path.join(ROOT_DIR, 'runtime'))

    shutil.copy(os.path.join(ROOT_DIR, 'README.txt'),
                os.path.join(ROOT_DIR, 'runtime'))

    shutil.copy(os.path.join(SOURCES_DIR, 'vim.exe'),
                os.path.join(SOURCES_DIR, 'vimw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'tee', 'tee.exe'),
                os.path.join(SOURCES_DIR, 'teew32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'xxd', 'xxd.exe'),
                os.path.join(SOURCES_DIR, 'xxdw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'install.exe'),
                os.path.join(SOURCES_DIR, 'installw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'uninstal.exe'),
                os.path.join(SOURCES_DIR, 'uninstalw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'gvim.exe'),
                os.path.join(SOURCES_DIR, 'gvim_ole.exe'))

    for directory in [GVIM_EXT32_DIR,
                      GVIM_EXT64_DIR,
                      GVIM_EXT32_RUNTIME_DIR,
                      GVIM_EXT64_RUNTIME_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    build_gvimext(args, 32)
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.dll'),
                os.path.join(GVIM_EXT32_DIR, 'gvimext.dll'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'README.txt'),
                os.path.join(GVIM_EXT32_DIR, 'README.txt'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.inf'),
                os.path.join(GVIM_EXT32_DIR, 'gvimext.inf'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'GvimExt.reg'),
                os.path.join(GVIM_EXT32_DIR, 'GvimExt.reg'))
    for filepath in os.listdir(GVIM_EXT32_DIR):
        shutil.copy(filepath, GVIM_EXT32_RUNTIME_DIR)

    build_gvimext(args, 64)
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.dll'),
                os.path.join(GVIM_EXT_DIR, 'gvimext64.dll'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.dll'),
                os.path.join(GVIM_EXT64_DIR, 'gvimext.dll'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'README.txt'),
                os.path.join(GVIM_EXT64_DIR, 'README.txt'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.inf'),
                os.path.join(GVIM_EXT64_DIR, 'gvimext.inf'))
    shutil.copy(os.path.join(GVIM_EXT_DIR, 'GvimExt.reg'),
                os.path.join(GVIM_EXT64_DIR, 'GvimExt.reg'))
    for filepath in os.listdir(GVIM_EXT64_DIR):
        shutil.copy(filepath, GVIM_EXT64_RUNTIME_DIR)

    upx = find_executable('upx')
    if upx is None:
        print('WARNING: Ultimate Packer eXecutables is not available.')

    makensis = find_executable('makensis')
    if makensis is None:
        raise RuntimeError('Cannot find makensis executable. '
                           'Did you install NSIS?')

    vimrt = '/DVIMRT={0}'.format(os.path.join('..', 'runtime'))
    outfile = '/XOutFile {0}'.format('gvim-package.exe')

    subprocess.check_call([makensis,
                           vimrt,
                           GVIM_NSIS_PATH,
                           outfile])

    rename_package(args)


def clean_up():
    remove_if_exists(os.path.join(ROOT_DIR, 'runtime', 'vimtutor.bat'))
    remove_if_exists(os.path.join(ROOT_DIR, 'runtime', 'README.txt'))
    remove_if_exists(os.path.join(GVIM_EXT_DIR, 'gvimext64.dll'))


def remove_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type=int, choices=[11, 12, 14, 15],
                        default=15, help='choose the Microsoft Visual '
                        'Studio version (default: %(default)s).')
    parser.add_argument('package', type=str,
                        help='Vim package name.')

    return parser.parse_args()


def main():
    args = parse_arguments()
    generate_package(args)
    clean_up()


if __name__ == '__main__':
    main()
