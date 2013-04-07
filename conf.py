#!/usr/bin/python2
"""
Usage: configure [options] [host]
Options: [defaults in brackets after descriptions]
Configuration:
  --cache-file=FILE       cache test results in FILE
  --help                  print this message
  --no-create             do not create output files
  --quiet, --silent       do not print `checking...' messages
  --version               print the version of autoconf that created configure
Directory and file names:
  --prefix=PREFIX         install architecture-independent files in PREFIX
                          [/usr/local]
  --exec-prefix=EPREFIX   install architecture-dependent files in EPREFIX
                          [same as prefix]
  --bindir=DIR            user executables in DIR [EPREFIX/bin]
  --sbindir=DIR           system admin executables in DIR [EPREFIX/sbin]
  --libexecdir=DIR        program executables in DIR [EPREFIX/libexec]
  --datadir=DIR           read-only architecture-independent data in DIR
                          [PREFIX/share]
  --sysconfdir=DIR        read-only single-machine data in DIR [PREFIX/etc]
  --sharedstatedir=DIR    modifiable architecture-independent data in DIR
                          [PREFIX/com]
  --localstatedir=DIR     modifiable single-machine data in DIR [PREFIX/var]
  --libdir=DIR            object code libraries in DIR [EPREFIX/lib]
  --includedir=DIR        C header files in DIR [PREFIX/include]
  --oldincludedir=DIR     C header files for non-gcc in DIR [/usr/include]
  --infodir=DIR           info documentation in DIR [PREFIX/info]
  --mandir=DIR            man documentation in DIR [PREFIX/man]
  --srcdir=DIR            find the sources in DIR [configure dir or ..]
  --program-prefix=PREFIX prepend PREFIX to installed program names
  --program-suffix=SUFFIX append SUFFIX to installed program names
  --program-transform-name=PROGRAM
                          run sed PROGRAM on installed program names
Host type:
  --build=BUILD           configure for building on BUILD [BUILD=HOST]
  --host=HOST             configure for HOST [guessed]
  --target=TARGET         configure for TARGET [TARGET=HOST]
Features and packages:
  --disable-FEATURE       do not include FEATURE (same as --enable-FEATURE=no)
  --enable-FEATURE[=ARG]  include FEATURE [ARG=yes]
  --with-PACKAGE[=ARG]    use PACKAGE [ARG=yes]
  --without-PACKAGE       do not use PACKAGE (same as --with-PACKAGE=no)
  --x-includes=DIR        X include files are in DIR
  --x-libraries=DIR       X library files are in DIR
--enable and --with options recognized:
  --with-dist-dir=DIR     Use DIR as 'dist' staging area.  DIR may be
                          relative to the top of SpiderMonkey build tree,
                          or absolute.
  --disable-compile-environment
                          Disable compiler/library checks.
  --disable-shared-js
                          Do not create a shared library.
  --with-gonk=DIR
               location of gonk dir
  --with-gonk-toolchain-prefix=DIR
                          prefix to gonk toolchain commands
  --with-android-ndk=DIR
                          location where the Android NDK can be found
  --with-android-toolchain=DIR
                          location of the android toolchain
  --with-android-gnu-compiler-version=VER
                          gnu compiler version to use
  --enable-android-libstdcxx
                          use GNU libstdc++ instead of STLPort
  --with-android-version=VER
                          android platform version, default 5 for arm, 9 for x86/mips
  --with-android-platform=DIR
                           location of platform dir
  --enable-metro           Enable Windows Metro build targets
  --with-windows-version=WINSDK_TARGETVER
                          Windows SDK version to target. Lowest version
                          currently allowed is 601, highest is 602
  --enable-macos-target=VER (default=10.6)
                          Set the minimum MacOS version needed at runtime
  --with-macos-sdk=dir    Location of platform SDK to use (Mac OS X only)
  --with-x                use the X Window System
  --with-arch=[[type|toolchain-default]]
                           Use specific CPU features (-march=type). Resets
                           thumb, fpu, float-abi, etc. defaults when set
  --with-thumb[[=yes|no|toolchain-default]]
                          Use Thumb instruction set (-mthumb)
  --with-thumb-interwork[[=yes|no|toolchain-default]]
                           Use Thumb/ARM instuctions interwork (-mthumb-interwork)
  --with-fpu=[[type|toolchain-default]]
                           Use specific FPU type (-mfpu=type)
  --with-float-abi=[[type|toolchain-default]]
                           Use specific arm float ABI (-mfloat-abi=type)
  --with-soft-float[[=yes|no|toolchain-default]]
                           Use soft float library (-msoft-float)
  --enable-address-sanitizer       Enable Address Sanitizer (default=no)
  --enable-llvm-hacks       Enable workarounds required for several LLVM instrumentations (default=no)
  --disable-os2-high-mem  Disable high-memory support on OS/2
  --disable-ion      Disable use of the IonMonkey JIT
  --disable-methodjit           Disable method JIT support
  --disable-monoic      Disable use of MICs by JIT compiler
  --disable-polyic      Disable use of PICs by JIT compiler
  --disable-gcincremental Disable incremental GC
  --enable-methodjit-spew      Enable method JIT spew support
  --disable-icf          Disable Identical Code Folding
  --enable-cpp-rtti       Enable C++ RTTI 
  --enable-update-channel=CHANNEL
                          Select application update channel (default=default)
  --with-linux-headers=DIR
                          location where the Linux kernel headers can be found
  --with-pthreads         Force use of system pthread library with NSPR 
  --with-system-nspr      Use an NSPR that is already built and installed.
                          Use the 'nspr-config' script in the current path,
                          or look for the script in the directories given with
                          --with-nspr-exec-prefix or --with-nspr-prefix.
                          (Those flags are only checked if you specify
                          --with-system-nspr.)
  --with-nspr-cflags=FLAGS
                          Pass FLAGS to CC when building code that uses NSPR.
                          Use this when there's no accurate nspr-config
                          script available.  This is the case when building
                          SpiderMonkey as part of the Mozilla tree: the
                          top-level configure script computes NSPR flags
                          that accomodate the quirks of that environment.
  --with-nspr-libs=LIBS   Pass LIBS to LD when linking code that uses NSPR.
                          See --with-nspr-cflags for more details.
  --with-nspr-prefix=PFX  Prefix where NSPR is installed
  --with-nspr-exec-prefix=PFX
                          Exec prefix where NSPR is installed
  --with-system-zlib[=PFX]
                          Use system libz [installed at prefix PFX]
  --with-debug-label=LABELS
                          Define DEBUG_<value> for each comma-separated
                          value given.
  --with-ccache[=path/to/ccache]
                          Enable compiling with ccache
  --with-static-checking=path/to/gcc_dehydra.so
                          Enable static checking of code using GCC-dehydra
  --with-qemu-exe=path   Use path as an arm emulator on host platforms
  --with-cross-lib=dir   Use dir as the location for arm libraries
  --with-arm-kuser         Use kuser helpers (Linux/ARM only -- requires kernel 2.6.13 or later)

  --enable-system-ffi       Use system libffi (located with pkgconfig)
  --enable-ui-locale=ab-CD
                          Select the user interface locale (default: en-US)

  --disable-tests         Do not build test libraries & programs


  --enable-debug[=DBG]    Enable building with developer debug info
                           (using compiler flags DBG)
  --disable-optimize      Disable compiler optimization
  --enable-optimize=[OPT] Specify compiler optimization flags [OPT=-O]

  --enable-trace-logging   Enable trace logging
  --enable-warnings-as-errors
                          Enable treating of warnings as errors
  --enable-sm-fail-on-warnings
                          Enable warnings as errors
  --enable-trace-malloc   Enable malloc tracing
  --enable-wrap-malloc    Wrap malloc calls (gnu linker only)
  --with-wrap-malloc=DIR  Location of malloc wrapper library
  --enable-trace-jscalls  Enable JS call enter/exit callback (default=no)
  --enable-profiling      Set compile flags necessary for using sampling profilers (e.g. shark, perf)
  --enable-jprof          Enable jprof profiling tool (needs mozilla/tools/jprof). Implies --enable-profiling.
  --enable-shark          Enable shark remote profiling. Implies --enable-profiling.
  --enable-callgrind      Enable callgrind profiling. Implies --enable-profiling.
  --enable-vtune          Enable vtune profiling. Implies --enable-profiling.
  --enable-ETW            Enable ETW (Event Tracing for Windows) event reporting
  --enable-dtrace         build with dtrace support if available (default=no)
  --enable-js-diagnostics
                          Enable JS diagnostic assertions and breakpad data
  --enable-install-strip  Enable stripping of libs & executables when packaging 
  --jitreport-granularity=N
                           Default granularity at which to report JIT code
                           to external tools
                             0 - no info
                             1 - code ranges for whole functions only
                             2 - per-line information
                             3 - per-op information
"""

# Only disabled-by-default allowed in here.
SingleCharShortcuts = {
    'C': '\'--with-ccache=/usr/bin/ccache;\'--cache-file=/home/terrence/moz/config.cache;',
    's': '+strip',
    'd': '+debug-symbols',
    'D': '+dmd',
    'j': '+jemalloc',
    'n': '+gcgenerational',
    'r': '+root-analysis',
    'x': '+exact-rooting',
    'v': '+valgrind',
    'z': '+gczeal',
    'd': '+more-deterministic',
    'O': '+oom-backtrace',
    'X': '+xterm-updates',
    'r': '+readline',
    'c': '+ctypes',
    't': '+threadsafe',
    'n': '=system-nspr',
}

MultiCharShortcuts = {
    'def': '*jctrXnC', # We almost always want these.
    'dbg': '*dvz', # Add debugability enhancements.
    'perf': '*s', # forces stripping
    'fuzz': '*dO',
    'ggc': '*nrx'
}

Compilers = {
    'c': ('clang', 'clang++'),
    'g': ('gcc', 'g++'),
    'D': ('', ''),
}

Optimizations = {
    'o': '+optimize!debug',
    'd': '!optimize+debug',
    'D': '+optimize+debug',
}

Architectures = {
    '4': '^CPPFLAGS=-m32;',
    '8': '^CPPFLAGS=-m64;',
    'X': '^CPPFLAGS=-mx32;',
}

# Grammar = Compiler & OptimizationLevel & Architecture & Flag*
#
#  Flags:
#    Enable argument with --enable-$TEXT:
#       +TEXT
#    Enable argument with --with-$TEXT:
#       =TEXT
#    Disable argument with --disable-$TEXT:
#       !TEXT
#    Send literal argument $TEXT:
#       'TEXT;
#    Environment Variable:
#       ^FLAG=foo;
#    Expand all single char shortcuts with --enable-$REP:
#       *abcd
#    Expand all multi char shortcuts recursively:
#       .name

FlagChars = set(('^', '+', '=', '!', '\'', '*', '.'))

import getopt
import os
import os.path
import sys

Environment = {}
Arguments = []

class ParseError(Exception):
    def __init__(self, msg, context):
        Exception.__init__(self, msg)
        self.context = context

def parse_environment(t):
    assert t[0] == '^'
    last = t.find(';')
    if last == -1:
        raise ParseError('Environment updates must be terminated with ";"', t)
    env, t = t[1:last], t[last+1:]
    if env:
        k, _, v = env.partition('=')
        Environment[k.strip()] = v.strip()
    return t

def parse_singlechars(t):
    assert t[0] == '*'
    t = t[1:]
    while t and t[0] not in FlagChars:
        char, t = t[0], t[1:]
        if char not in SingleCharShortcuts:
            raise ParseError('Unrecognized single char shortcut: "%s"' % char, t)
        parse_flags(SingleCharShortcuts[char])
    return t

def consume_to_next_flag(t):
    assert t[0] in FlagChars
    t = t[1:]
    offset = 0
    while offset < len(t) and t[offset] not in FlagChars:
        offset += 1
    return t[:offset], t[offset:]

def parse_multichars(t):
    assert t[0] == '.'
    name, t = consume_to_next_flag(t)
    if name not in MultiCharShortcuts:
        raise ParseError('Unrecognized multi char shortcut: "%s"' % name, name + t)
    parse_flags(MultiCharShortcuts[name])
    return t

def parse_enable(t):
    assert t[0] == '+'
    arg, t = consume_to_next_flag(t)
    Arguments.append('--enable-' + arg)
    return t

def parse_with(t):
    assert t[0] == '='
    arg, t = consume_to_next_flag(t)
    Arguments.append('--with-' + arg)
    return t

def parse_disable(t):
    assert t[0] == '!'
    arg, t = consume_to_next_flag(t)
    Arguments.append('--disable-' + arg)
    return t

def parse_literal(t):
    assert t[0] == '\''
    last = t.find(';')
    if last == -1:
        raise ParseError('Literal args must be terminated with ";"', t)
    arg, t = t[1:last], t[last+1:]
    if arg:
        Arguments.append(arg)
    return t

def parse_flags(t):
    prior_len = len(t)
    while len(t) > 0:
        ty = t[0]
        if ty not in FlagChars:
            raise ParseError("Expected another flag at '%s'" % ty, t)
        if ty == '^': t = parse_environment(t)
        elif ty == '*': t = parse_singlechars(t)
        elif ty == '.': t = parse_multichars(t)
        elif ty == '+': t = parse_enable(t)
        elif ty == '=': t = parse_with(t)
        elif ty == '!': t = parse_disable(t)
        elif ty == '\'': t = parse_literal(t)
        else: raise ParseError('Unrecognized flag type: %s' % ty, t)
        assert prior_len != len(t)
        prior_len = len(t)
    return ''

def parse_compiler(t):
    flag, t = t[0], t[1:]
    if flag not in Compilers:
        raise ParseError('Unrecognized compiler: %s' % flag, t)
    cc, cpp = Compilers[flag]
    if cc: Environment['CC'] = cc
    if cpp: Environment['CPP'] = cpp
    return t

def parse_optimization(t):
    flag, t = t[0], t[1:]
    if flag not in Optimizations:
        raise ParseError('Unrecognized optimization level: %s' % flag, t)
    parse_flags(Optimizations[flag])
    return t

def parse_architecture(t):
    flag, t = t[0], t[1:]
    if flag not in Architectures:
        raise ParseError('Unrecognized architecture: %s' % flag, t)
    parse_flags(Architectures[flag])
    return t

def parse(t):
    t = parse_compiler(t)
    t = parse_optimization(t)
    t = parse_architecture(t)
    t = parse_flags(t)

def main():
    optlist, extra = getopt.gnu_getopt(sys.argv, 's', ['show'])

    cwd = os.getcwd()
    directory = os.path.basename(cwd)
    parent = os.path.dirname(cwd)
    configure = os.path.join(parent, 'configure')

    if not os.path.exists(configure):
        print "No 'configure' in parent directory!"
        return 1

    try:
        parse(directory)
    except ParseError, e:
        print str(e)
        if e.context in directory:
            pos = len(directory) - len(e.context)
            print "Context: %s" % directory
            print "         %s^" % ('-' * pos)
            return 1

    if ('--show', '') in optlist or ('-s', '') in optlist:
        print "Environment:"
        for k, v in Environment.items():
            print '\t%s: %s' % (k, v)
        print "Arguments:"
        for arg in Arguments:
            print '\t%s' % arg

    else:
        os.execve(configure, [configure] + Arguments, Environment)

if __name__ == '__main__':
    sys.exit(main())

