#!/usr/bin/env python3
"""
Configure or build in the directory specified.

-j# is specified by int(arg0)
"""

import argparse
import os.path
import platform
import subprocess
import sys

import lib


class ParseError(Exception):
    def __init__(self, msg, context):
        Exception.__init__(self, msg)
        self.context = context

# Find ccache.
try:
    CCachePath = subprocess.check_output(['which', 'ccache']).decode('UTF-8').strip()
except FileNotFoundError:
    # This is windows, where we're not using the path.
    CCachePath = ''
except subprocess.CalledProcessError:
    CCachePath = ''

class ConfigParser:
    MultiCharShortcuts = {
        'nightly': "!warnings-as-errors+elf-hack+release+js-shell'--enable-update-channel=;'--with-google-api-keyfile=/builds/gapi.data;",
        'tbpl': "+signmar+stdcxx-compat!shared-js+trace-malloc",
        'tsan_pie': "+thread-sanitizer!jemalloc!crashreporter!elf-hack+debug-symbols!install-strip^MOZ_DEBUG_SYMBOLS=1;^CFLAGS=-fsanitize=thread -fPIC -pie;^CXXFLAGS=-fsanitize=thread -fPIC -pie;^LDFLAGS=-fsanitize=thread -fPIC -pie;",
        'tsan': "+thread-sanitizer!jemalloc!crashreporter!elf-hack+debug-symbols!install-strip^MOZ_DEBUG_SYMBOLS=1;^CFLAGS=-fsanitize=thread;^CXXFLAGS=-fsanitize=thread;^LDFLAGS=-fsanitize=thread;",
        'rust': "+rust",
        'shell': '+readline',
        'dbg': '+debug-symbols+valgrind+gczeal',
        'def': '.dbg.shell', # .dbg.shell
        'perf': '+strip', # forces stripping
        'fuzz': '.dbg+more-deterministic+methodjit+type-inference+profiling',
        # Use system installed libraries.
        'sysicu': '=system-icu',
        'sysnspr': '=system-nspr',
        'syslibs': ".sysicu.sysnspr",
        # Enable optional libraries.
        'crashreporter': "+crashreporter",
        'prof': "+profiling",
        # Disable optional libraries.
        'noicu': "?intl-api",
        'noctypes': "!ctypes",
        'nogstreamer': "!gstreamer",
        'noext': ".noicu.noctypes",
        # Compiler wrappers.
        'distcc': "'--with-compiler-wrapper=distcc;",
    }
    if CCachePath:
        MultiCharShortcuts['ccache'] = '^CCACHE_CPP2=1;^CCACHE_UNIFY=1;\'--with-ccache=' + CCachePath + ';'

    Compilers = {
        'c': {
                'name': 'Clang',
                'flags': '^CC=clang;^CXX=clang++;^CXXFLAGS=-fcolor-diagnostics;',
                'architectures': {
                    'd': '',
                    '4': '^AR=ar;^CC=-arch i386;^CXX=-arch i386;\'--target=i686-linux-gnu;',
                }
             },
        'g': {
                'name': 'GCC',
                'flags': '^CC=gcc;^CXX=g++;^CXXFLAGS=-fdiagnostics-color -Wunused;',
                'architectures': {
                    'd': '',
                    '4': '^AR=ar;^CC=-m32;^CXX=-m32;\'--target=i686-linux-gnu;',
                    '8': '^CC=-m64;^CXX=-m64;',
                    'X': '^CC=-mx32;^CXX=-mx32;',
                    'a': '^CC=-m32;^CXX=-m32;\'--target=arm-linux-gnuabi;',
                    'A': '^AR=ar;^CC=-m32;^CXX=-m32;\'--target=i686-linux-gnu;!ctypes+arm-simulator',
                }
             },
        'd': {
                'name': 'Default',
                'flags': '^CC=clang;^CXX=clang++;^CCACHE_CC=clang;^CXXFLAGS=-fcolor-diagnostics;',
                'architectures': {
                    'd': '',
                }
             },
        'v': {
            'name': 'MicrosoftVisualC++',
            'flags': '',
            'architectures': {'d': ''}
        }
    }

    Optimizations = {
        'o': '+optimize!debug',
        'd': '!optimize+debug',
        'D': '+optimize+debug',
        'T': "!debug'--enable-optimize=-O2 -gline-tables-only;",
        't': "!debug'--enable-optimize=-O2 -g;",
    }

    FlagChars = set(('^', '+', '=', '!', '?', '\'', '.', '@')) # '*' is available

    def __init__(self, target):
        self.target = target.strip().strip(os.path.sep)
        assert '/' not in target
        assert '\\' not in target
        self.have_parsed = False
        self.environment = {}
        self.arguments = []

    def parse_environment(self, t):
        assert t[0] == '^'
        last = t.find(';')
        if last == -1:
            raise ParseError('Environment updates must be terminated with ";"', t)
        env, t = t[1:last], t[last+1:]
        if env:
            k, _, v = env.partition('=')
            k = k.strip()
            v = v.strip()
            if k not in self.environment:
                self.environment[k] = v
            else:
                self.environment[k] = self.environment[k] + ' ' + v
        return t

    def consume_to_next_flag(self, t):
        assert t[0] in self.FlagChars
        t = t[1:]
        offset = 0
        while offset < len(t) and t[offset] not in self.FlagChars:
            offset += 1
        return t[:offset], t[offset:]

    def parse_multichars(self, t):
        assert t[0] == '.'
        name, t = self.consume_to_next_flag(t)
        if name not in self.MultiCharShortcuts:
            raise ParseError('Unrecognized multi char shortcut: "%s"' % name, name + t)
        self.parse_flags(self.MultiCharShortcuts[name])
        return t

    def parse_enable(self, t):
        assert t[0] == '+'
        arg, t = self.consume_to_next_flag(t)
        self.arguments.append('--enable-' + arg)
        return t

    def parse_with(self, t):
        assert t[0] == '='
        arg, t = self.consume_to_next_flag(t)
        self.arguments.append('--with-' + arg)
        return t

    def parse_disable(self, t):
        assert t[0] == '!'
        arg, t = self.consume_to_next_flag(t)
        self.arguments.append('--disable-' + arg)
        return t

    def parse_without(self, t):
        assert t[0] == '?'
        arg, t = self.consume_to_next_flag(t)
        self.arguments.append('--without-' + arg)
        return t

    def parse_literal(self, t):
        assert t[0] == '\''
        last = t.find(';')
        if last == -1:
            raise ParseError('Literal args must be terminated with ";"', t)
        arg, t = t[1:last], t[last+1:]
        if arg:
            self.arguments.append(arg)
        return t

    def parse_flags(self, t):
        prior_len = len(t)
        while len(t) > 0:
            ty = t[0]
            if ty not in self.FlagChars:
                raise ParseError("Expected another flag at '%s'" % ty, t)
            if ty == '^': t = self.parse_environment(t)
            elif ty == '.': t = self.parse_multichars(t)
            elif ty == '+': t = self.parse_enable(t)
            elif ty == '=': t = self.parse_with(t)
            elif ty == '!': t = self.parse_disable(t)
            elif ty == '?': t = self.parse_without(t)
            elif ty == '\'': t = self.parse_literal(t)
            elif ty == '@': t = ''
            else: raise ParseError('Unrecognized flag type: %s' % ty, t)
            assert prior_len != len(t)
            prior_len = len(t)
        return ''

    def parse_compiler(self, compiler, arch, t):
        if compiler not in self.Compilers:
            raise ParseError('Unrecognized compiler: %s' % compiler, t)
        if arch not in self.Compilers[compiler]['architectures']:
            raise ParseError('Unrecognized architecture: %s' % arch, t)
        self.parse_flags(self.Compilers[compiler]['flags'])
        self.parse_flags(self.Compilers[compiler]['architectures'][arch])

    def parse_optimization(self, flag, t):
        if flag not in self.Optimizations:
            raise ParseError('Unrecognized optimization level: %s' % flag, t)
        self.parse_flags(self.Optimizations[flag])

    def parse_toplevel(self, t):
        if t[0] != '_':
            raise ParseError('String must start with \'_\'.')
        t = t[1:]
        if len(t) < 3:
            raise ParseError('String requires at least a compiler, optimization, and arch flag.', t)
        compiler, architecture, optimization = t[0], t[1], t[2]
        self.parse_compiler(compiler, architecture, t)
        self.parse_optimization(optimization, t)
        t = t[3:]
        t = self.parse_flags(t)
        assert t == ""

    def parse(self):
        if self.have_parsed:
            return
        try:
            self.parse_toplevel(self.target)
        except ParseError as e:
            print(str(e))
            if e.context in self.target:
                pos = len(t) - len(e.context)
                print("Context: %s" % self.target)
                print("         %s^" % ('-' * pos))
        finally:
            self.have_parsed = True

    def show(self):
        self.parse()
        print("Environment:")
        for k, v in self.environment.items():
            print('\t%s: %s' % (k, v))
        print("Arguments:")
        for arg in self.arguments:
            print('\t%s' % arg)

        short = ""
        for k, v in self.environment.items():
            short += '{}="{}"'.format(k, v) + " "
        short += "./configure"
        for arg in self.arguments:
            short += " " + arg
        print('\n')
        print(short)


def needs_autoconf():
    """
    Check if configure is out of date wrt configure.in.
    """
    if not os.path.exists('configure'):
        print("No configure, rerunning autoconf.")
        return True

    if os.path.getmtime('configure') < os.path.getmtime('configure.in'):
        print("configure is older than configure.in, rerunning autoconf.")
        return True

    return False


def autoconf():
    """
    Run autoconf v2.13. Try a few variants, because everyone seems to name it differently.
    """
    try:
        subprocess.call(['autoconf-2.13'])
    except FileNotFoundError:
        subprocess.call(['autoconf213'])
    except OSError:
        sh = "c:\\mozilla-build\\msys\\bin\\bash.exe"
        subprocess.call([sh, 'autoconf-2.13'])


class Builder:
    def __init__(self, builddir):
        self.builddir = builddir.strip().strip(os.path.sep).strip('/')

    def banner(self, content):
        print("+-------------------------------------------------------------------------------")
        print("+-- {} {}+".format(content, '-' * (80 - 5 - len(content))))
        print("+-------------------------------------------------------------------------------")
        sys.stdout.flush()


class SpiderMonkeyBuilder(Builder):
    def needs_configure(self):
        confstatus = os.path.join(self.builddir, 'config.status')

        if not os.path.exists(confstatus):
            print("no config.status")
            return True

        if os.path.getmtime(confstatus) < os.path.getmtime('configure'):
            print("config.status is older than configure")
            return True

        return False

    def configure(self):
        self.banner("Configuring: " + self.builddir)

        cfg = ConfigParser(self.builddir)
        cfg.parse()

        # Make the directory if it doesn't exist.
        pwd = os.getcwd()
        confdir = os.path.realpath(os.path.join(pwd, self.builddir))
        if not os.path.exists(confdir):
            os.mkdir(confdir)

        # Get a sane environment
        inherited = ('PATH', 'SHELL', 'HOME', 'TERM', 'COLORTERM', 'MOZILLABUILD')
        env = {k: os.environ[k] for k in inherited if k in os.environ}
        env.update(cfg.environment)

        configure = [os.path.realpath('configure')]
        shell = False
        if platform.system() == 'Windows':
            sh = "c:\\mozilla-build\\msys\\bin\\bash.exe"
            configure = [sh] + configure
            shell = True

            # Also, a ton more stuff is needed, so just dump the env filtering.
            env = os.environ

        subprocess.check_call(configure + cfg.arguments, env=env, cwd=confdir,
                              shell=shell)

    def which_make(self):
        if platform.system() == 'Windows':
            return 'mozmake.exe'
        return 'make'

    def build(self, is_verbose, n_jobs, extra):
        self.banner("Building: " + self.builddir)

        # Check for build-dir.
        if not os.path.isdir(self.builddir):
            raise Exception("No directory at builddir: {}".format(self.builddir))

        # Get the process count.
        extra += ['-j' + str(lib.get_jobcount(n_jobs))]

        # Default to silent build.
        if not is_verbose:
            extra += ['-s']

        # Get a sane environment
        inherited = ('PATH', 'SHELL', 'HOME', 'TERM', 'COLORTERM', 'MOZILLABUILD')
        env = {k: os.environ[k] for k in inherited if k in os.environ}
        env = os.environ.copy()

        subprocess.check_call([self.which_make()] + extra, cwd=self.builddir, env=env)

    def check_style(self):
        self.banner("check-style: " + self.builddir)
        subprocess.check_call([self.which_make(), 'check-style'], cwd=self.builddir)

    def jsapi_tests(self, debugger: bool, filter: str):
        self.banner("jsapi-tests: " + self.builddir)
        path = os.path.join(self.builddir, 'dist', 'bin', 'jsapi-tests')
        args = [path, filter] if not debugger else ['gdb', '--args', path, filter]
        subprocess.check_call(args)

    def jit_tests(self, filter: str):
        self.banner("jit-tests: " + self.builddir)
        testsuite = os.path.join('jit-test', 'jit_test.py')
        binary = os.path.join(self.builddir, 'js', 'src', 'js')
        if platform.system() == 'Windows':
            binary += '.exe'
        command = [testsuite, binary, '--tbpl', filter]
        subprocess.check_call(command, shell=True, env=os.environ)

    def js_tests(self):
        self.banner("js-tests: " + self.builddir)
        testsuite = os.path.join('tests', 'jstests.py')
        binary = os.path.join(self.builddir, 'dist', 'bin', 'js')
        subprocess.check_call([testsuite, binary, '--tbpl'])

    def mfbt_tests(self, filter: str):
        self.banner("mfbt-tests: " + self.builddir)
        bindir = os.path.join(self.builddir, 'dist/bin/')
        for filename in os.listdir(bindir):
            if filename.startswith('Test'):
                if filter and filter not in filename:
                    continue
                print("Running: {}".format(filename))
                binary = os.path.join(bindir, filename)
                subprocess.check_call([binary])


class MozConfigBuilder(Builder):
    def needs_configure(self):
        """We just want to spit out a MOZCONFIG for build, no configuration needed."""
        return False

    def build(self, is_verbose, n_jobs, extra):
        self.banner("Building: " + self.builddir)

        # Parse the configuration.
        cfg = ConfigParser(self.builddir)
        cfg.parse()

        # Make the directory if it doesn't exist.
        pwd = os.getcwd()
        confdir = os.path.realpath(os.path.join(pwd, self.builddir))
        if not os.path.exists(confdir):
            os.mkdir(confdir)

        # Write a mozconfig.
        with open(os.path.join(confdir, "moz.config"), "w") as mozconfig:
            for key, value in cfg.environment.items():
                mozconfig.write("export {}=\"{}\"\n".format(key, value))
            for arg in cfg.arguments:
                mozconfig.write("ac_add_options {}\n".format(arg))
            mozconfig.write("mk_add_options AUTOCLOBBER=1\n");
            mozconfig.write("mk_add_options MOZ_MAKE_FLAGS=\"-j{}\"\n".format(lib.get_jobcount(n_jobs)));
            mozconfig.write("mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/{}\n".format(self.builddir))


def main():
    # Process args.
    parser = argparse.ArgumentParser(description='Make a shell.')
    parser.add_argument('builddirs', metavar='CONTEXT', default='ctx', type=str, nargs='*',
                        help='The directory(s) to build.')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all build output.')
    parser.add_argument('--test', '-t', metavar='CONFIG',
                        help="Print the behavior of the given directory.")
    parser.add_argument('--jobs', '-j', metavar='count', default=0, type=int,
                        help='Number of parallel builds to run.')
    parser.add_argument('--check-style', '-S', action='store_true',
                        help='Run the check-style target.')
    parser.add_argument('--jsapi-tests', '-C', action='store_true',
                        help='Run the jsapi-tests suite.')
    parser.add_argument('--jit-tests', '-J', action='store_true',
                        help='Run the jit-tests suite.')
    parser.add_argument('--js-tests', '-T', action='store_true',
                        help='Run the js-tests suite.')
    parser.add_argument('--mfbt-tests', '-M', action='store_true',
                        help='Run the mfbt testsuite.')
    parser.add_argument('--all-tests', '-A', default=False, type=bool,
                        help='Run all tests.')
    parser.add_argument('--filter', '-f', default='', type=str,
                        help='Filter tests.')
    parser.add_argument('--debugger', '-g', action='store_true',
                        help='Run in a debugger.')
    args, extra = parser.parse_known_args()

    # Propogate all_tests to individual test routines.
    if args.all_tests:
        args.check_style = args.jsapi_tests = args.jit_tests = args.js_tests = True

    # Handle --test.
    if args.test:
        cfg = ConfigParser(args.test)
        cfg.show()
        return 0

    # Check for configure.
    if not os.path.isfile('configure.in'):
        print("No configure.in? You're not in the right place, you know.")
        return 0

    if not os.getcwd().endswith(os.path.join('js', 'src')):
        print("Using MOZCONFIG builder")
        BuilderClass = MozConfigBuilder
    else:
        print("Using SpiderMonkey builder")
        BuilderClass = SpiderMonkeyBuilder

    # Autoconf if needed.
    if needs_autoconf():
        autoconf()

    # Generate builders.
    builders = [BuilderClass(builddir) for builddir in args.builddirs]

    # Configure and build each directory in order.
    for builder in builders:
        # Configure if needed.
        if builder.needs_configure():
            builder.configure()

        # Do the build.
        builder.build(args.verbose, args.jobs, extra)

    # Run tests as requested.
    # Note: after all builds so the output is easy to find.
    for builder in builders:
        if args.jsapi_tests: builder.jsapi_tests(args.debugger, args.filter)
        if args.check_style: builder.check_style()
        if args.jit_tests:   builder.jit_tests(args.filter)
        if args.js_tests:    builder.js_tests()
        if args.mfbt_tests:  builder.mfbt_tests(args.filter)

    return 0

if __name__ == '__main__':
    sys.exit(main())
