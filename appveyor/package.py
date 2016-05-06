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
GVIM_NSIS_PATH = os.path.join(NSIS_DIR, 'gvim.nsi')
GVIM_PACKAGE_PATH = os.path.join(NSIS_DIR, 'gvim-package.exe')


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


def generate_package(args):
    generate_uganda_file()

    shutil.copy(os.path.join(ROOT_DIR, 'vimtutor.bat'),
                os.path.join(ROOT_DIR, 'runtime'))

    shutil.copy(os.path.join(ROOT_DIR, 'README.txt'),
                os.path.join(ROOT_DIR, 'runtime'))

    shutil.copy(os.path.join(SOURCES_DIR, 'install.exe'),
                os.path.join(SOURCES_DIR, 'installw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'uninstal.exe'),
                os.path.join(SOURCES_DIR, 'uninstalw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'gvim.exe'),
                os.path.join(SOURCES_DIR, 'gvim_ole.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'xxd', 'xxd.exe'),
                os.path.join(SOURCES_DIR, 'xxdw32.exe'))

    shutil.copy(os.path.join(SOURCES_DIR, 'vim.exe'),
                os.path.join(SOURCES_DIR, 'vimw32.exe'))

    shutil.copy(os.path.join(GVIM_EXT_DIR, 'gvimext.dll'),
                os.path.join(GVIM_EXT_DIR, 'gvimext64.dll'))

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
    parser.add_argument('package', type=str,
                        help='Vim package name.')

    return parser.parse_args()


def main():
    args = parse_arguments()
    generate_package(args)
    clean_up()


if __name__ == '__main__':
    main()
