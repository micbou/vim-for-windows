#!/usr/bin/env python

import argparse
import os
import subprocess
import platform
import re
from distutils.spawn import find_executable

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', 'vim')
SOURCES_DIR = os.path.join(ROOT_DIR, 'src')
RUNTIME_DIR = os.path.join(ROOT_DIR, 'runtime')
TRANSLATIONS_DIR = os.path.join(SOURCES_DIR, 'po')

MAKE_PATH = os.path.join(SOURCES_DIR, 'Make_mvc.mak')
APPVEYOR_MAKE_PATH = os.path.join(SOURCES_DIR, 'Make_mvc_appveyor.mak')

MSVC_BIN_DIR = os.path.join('..', '..', 'VC', 'bin')
VC_VARS_SCRIPT = os.path.join('..', '..', 'VC', 'vcvarsall.bat')

SDK_INCLUDE_DIR = (r'C:\Program Files (x86)\Microsoft SDKs\Windows'
                   r'\v7.1A\Include')

VERSION_REGEX = re.compile('([0-9]+).([0-9]+)(.([0-9]+)){0,2}')


def get_major_minor_version(version):
    matches = VERSION_REGEX.match(version)
    if not matches:
        raise RuntimeError('Wrong version format: {0}'.format(version))
    return matches.group(1) + '.' + matches.group(2)


def get_minimal_version(version):
    matches = VERSION_REGEX.match(version)
    if not matches:
        raise RuntimeError('Wrong version format: {0}'.format(version))
    return matches.group(1) + matches.group(2)


def get_arch_build_args(args):
    if args.arch == 64:
        return 'CPU=AMD64'
    return 'CPU=i386'


def get_lua_build_args(args):
    if not args.lua_version:
        return []

    lua_version = get_minimal_version(args.lua_version)

    return ['LUA={0}'.format(args.lua_path),
            'LUA_VER={0}'.format(lua_version),
            'DYNAMIC_LUA=yes']


def get_perl_path(args):
    if args.perl_path:
        return args.perl_path

    if args.arch == 64:
        return r'C:\Perl64'
    return r'C:\Perl'


def get_perl_build_args(args):
    if not args.perl_version:
        return []

    perl_path = get_perl_path(args)
    perl_version = get_minimal_version(args.perl_version)

    return ['PERL={0}'.format(perl_path),
            'PERL_VER={0}'.format(perl_version),
            'DYNAMIC_PERL=yes']


def get_python2_path(args):
    if args.python2_path:
        return args.python2_path

    python2_version = get_minimal_version(args.python2_version)

    if args.arch == 64:
        return r'C:\Python{0}-x64'.format(python2_version)
    return r'C:\Python{0}'.format(python2_version)


def get_python3_path(args):
    if args.python3_path:
        return args.python3_path

    python3_version = get_minimal_version(args.python3_version)

    if args.arch == 64:
        return r'C:\Python{0}-x64'.format(python3_version)
    return r'C:\Python{0}'.format(python3_version)


def get_pythons_build_args(args):
    pythons_args = []

    if args.python2_version:
        python2_path = get_python2_path(args)
        python2_version = get_minimal_version(args.python2_version)
        pythons_args.extend(['PYTHON_VER={0}'.format(python2_version),
                             'DYNAMIC_PYTHON=yes',
                             'PYTHON={0}'.format(python2_path)])

    if args.python3_version:
        python3_path = get_python3_path(args)
        python3_version = get_minimal_version(args.python3_version)
        pythons_args.extend(['PYTHON3_VER={0}'.format(python3_version),
                             'DYNAMIC_PYTHON3=yes',
                             'PYTHON3={0}'.format(python3_path)])

    return pythons_args


def get_racket_build_args(args):
    if not args.racket_library_version:
        return []

    return ['MZSCHEME={0}'.format(args.racket_path),
            'MZSCHEME_VER={0}'.format(args.racket_library_version),
            'DYNAMIC_MZSCHEME=yes']


def get_ruby_path(args):
    if args.ruby_path:
        return args.ruby_path

    ruby_version = get_minimal_version(args.ruby_version)

    if args.arch == 64:
        return r'C:\Ruby{0}-x64'.format(ruby_version)
    return r'C:\Ruby{0}'.format(ruby_version)


def get_ruby_build_args(args):
    if not args.ruby_version:
        return []

    ruby_path = get_ruby_path(args)
    ruby_api_ver_long = args.ruby_version
    ruby_ver = get_minimal_version(args.ruby_version)

    return ['RUBY={0}'.format(ruby_path),
            'RUBY_API_VER_LONG={0}'.format(ruby_api_ver_long),
            'RUBY_VER={0}'.format(ruby_ver),
            'DYNAMIC_RUBY=yes',
            'RUBY_MSVCRT_NAME=msvcrt']


def get_tcl_build_args(args):
    if not args.tcl_version:
        return []

    tcl_ver_long = get_major_minor_version(args.tcl_version)
    tcl_ver = get_minimal_version(args.tcl_version)

    return ['TCL={0}'.format(args.tcl_path),
            'TCL_VER_LONG={0}'.format(tcl_ver_long),
            'TCL_VER={0}'.format(tcl_ver),
            'DYNAMIC_TCL=yes']


def get_msvc_dir(args):
    if args.msvc == 11:
        return os.path.join(os.environ['VS110COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 12:
        return os.path.join(os.environ['VS120COMNTOOLS'], MSVC_BIN_DIR)
    if args.msvc == 14:
        return os.path.join(os.environ['VS140COMNTOOLS'], MSVC_BIN_DIR)
    raise RuntimeError('msvc parameter should be 11, 12, or 14.')


def get_vc_mod(arch):
    if arch == 64:
        return 'x86_amd64'
    return 'x86'


def get_build_args(args, gui=True):
    build_args = [get_arch_build_args(args)]

    if gui:
        build_args.extend(['GUI=yes',
                           'OLE=yes',
                           'GIME=yes',
                           'DIRECTX=yes'])
        # MSVC 14 will fail to build gvim with XPM image support enabled.
        # See https://groups.google.com/forum/#!topic/vim_dev/6DfnCX9TjYI
        # TODO: find a way to fix this.
        if args.msvc == 14:
            build_args.append('XPM=no')

    build_args.extend(['FEATURES=HUGE',
                       'IME=yes',
                       'MBYTE=yes',
                       'ICONV=yes',
                       'DEBUG=no'])

    if args.credit:
        build_args.extend(['USERNAME={0}'.format(args.credit),
                           'USERDOMAIN='])

    build_args.extend(get_lua_build_args(args))
    build_args.extend(get_perl_build_args(args))
    build_args.extend(get_pythons_build_args(args))
    build_args.extend(get_racket_build_args(args))
    build_args.extend(get_ruby_build_args(args))
    build_args.extend(get_tcl_build_args(args))

    return build_args


def build_vim(args, gui=True):
    os.chdir(SOURCES_DIR)

    new_env = os.environ.copy()

    if not os.path.exists(SDK_INCLUDE_DIR):
        raise RuntimeError('SDK include folder does not exist.')

    new_env['SDK_INCLUDE_DIR'] = SDK_INCLUDE_DIR

    msvc_dir = get_msvc_dir(args)

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.exists(nmake):
        raise RuntimeError('nmake tool not found.')

    build_args = get_build_args(args, gui)

    vc_vars_script_path = os.path.join(msvc_dir, VC_VARS_SCRIPT)
    vc_vars_cmd = [vc_vars_script_path, get_vc_mod(args.arch)]

    clean_cmd = vc_vars_cmd
    clean_cmd.extend(['&', nmake, '/f', APPVEYOR_MAKE_PATH, 'clean'])
    clean_cmd.extend(build_args)

    subprocess.check_call(clean_cmd, env=new_env)

    build_cmd = vc_vars_cmd
    build_cmd.extend(['&', nmake, '/f', APPVEYOR_MAKE_PATH])
    build_cmd.extend(build_args)

    subprocess.check_call(build_cmd, env=new_env)


def get_arch_from_python_interpreter():
    if platform.architecture()[0] == '64bit':
        return 64
    return 32


def remove_progress_bars():
    # Progress bars from the build are messing up the logs on AppVeyor.
    # Create a new make file that remove them.
    with open(MAKE_PATH, "r") as make_file:
        lines = make_file.readlines()
    with open(APPVEYOR_MAKE_PATH, "w") as appveyor_make_file:
        for line in lines:
            appveyor_make_file.write(re.sub(r'\$\(LINKARGS2\)',
                                            r'$(LINKARGS2) | '
                                            r"sed -e 's#.*\\r.*##'",
                                            line))


def build_translations(args):
    msvc_dir = get_msvc_dir(args)

    nmake = os.path.join(msvc_dir, 'nmake.exe')
    if not os.path.isfile(nmake):
        raise RuntimeError('nmake tool not found.')

    gettext_path = find_executable('xgettext')
    if not gettext_path:
        raise RuntimeError('gettext tool not found')

    cmd = [nmake,
           '/f',
           'Make_mvc.mak',
           'GETTEXT_PATH={0}'.format(os.path.dirname(gettext_path)),
           'VIMRUNTIME={0}'.format(RUNTIME_DIR),
           'install-all']

    subprocess.check_call(cmd, cwd=TRANSLATIONS_DIR)


def clean_up():
    if os.path.isfile(APPVEYOR_MAKE_PATH):
        os.remove(APPVEYOR_MAKE_PATH)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msvc', type=int, choices=[11, 12, 14],
                        default=12, help='choose the Microsoft Visual '
                        'Studio version (default: %(default)s).')
    parser.add_argument('--arch', type=int, choices=[32, 64],
                        help='force architecture to 32 or 64 bits on '
                        'Windows (default: python interpreter architecture).')
    parser.add_argument('--lua-path', type=str, default='C:\Lua',
                        help='set Lua folder (default: C:\Lua)')
    parser.add_argument('--lua-version', type=str,
                        help='set Lua version')
    parser.add_argument('--perl-path', type=str,
                        help='set Perl folder (default: C:\Perl '
                        'or C:\Perl64 depending on architecture)')
    parser.add_argument('--perl-version', type=str,
                        help='set Perl version')
    parser.add_argument('--python2-path', type=str,
                        help='set Python2 folder (default: C:\Python{ver} '
                        'or C:\Python{ver}-x64 depending on architecture)')
    parser.add_argument('--python2-version', type=str,
                        help='set Python2 version')
    parser.add_argument('--python3-path', type=str,
                        help='set Python3 folder (default: C:\Python{ver} '
                        'or C:\Python{ver}-x64 depending on architecture)')
    parser.add_argument('--python3-version', type=str,
                        help='set Python3 version')
    parser.add_argument('--racket-path', type=str, default='C:\Racket',
                        help='set Racket folder (default: C:\Racket)')
    parser.add_argument('--racket-library-version', type=str,
                        help='set Racket library version')
    parser.add_argument('--ruby-path', type=str,
                        help='set Ruby folder (default: C:\Ruby{ver})')
    parser.add_argument('--ruby-version', type=str,
                        help='set Ruby version')
    parser.add_argument('--tcl-path', type=str, default='C:\Tcl',
                        help='set Tcl folder (default: C:\Tcl)')
    parser.add_argument('--tcl-version', type=str,
                        help='set Tcl version')
    parser.add_argument('--credit', type=str,
                        help='replace username@userdomain by a custom '
                             'string in compilation credit.')

    args = parser.parse_args()
    if not args.arch:
        args.arch = get_arch_from_python_interpreter()

    return args


def main():
    args = parse_arguments()
    remove_progress_bars()
    build_vim(args, gui=False)
    build_vim(args)
    build_translations(args)
    clean_up()


if __name__ == '__main__':
    main()
