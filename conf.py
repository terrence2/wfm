#!/usr/bin/python3
import argparse
import os
import os.path
import subprocess
import sys

SingleCharShortcuts = {
    # \'--cache-file=/home/terrence/moz/config.cache; -- Seems to cache too much, like the CC/CXX environment vars!?!
    'C': '^CCACHE_CPP2=1;^CCACHE_UNIFY=1;\'--with-ccache=/usr/bin/ccache;',
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
    'R': '+readline',
    'c': '+ctypes',
    't': '+threadsafe',
    'N': '=system-nspr',
    'T': '+trace-malloc',
}

MultiCharShortcuts = {
    'shell': '*RX', # We almost always want these.
    'dbg': '*dvz', # Add debugability enhancements.
    'def': '*dvzRX!intl-api', # .dbg.shell
    'ra': '!optimize+debug!threadsafe*rzv', # Root analysis build (replaces def).
    'perf': '*s', # forces stripping
    'fuzz': '*dO',
    'ggc': '*nx',
    'tbpl': '+signmar+stdcxx-compat!shared-js*tcTNC',
    'tbpl4': '+signmar+stdcxx-compat!shared-js*tTC\'--with-nspr-prefix=/usr/i686-linux-gnu;\'--with-nspr-exec-prefix=/usr/i686-linux-gnu;',
}

Compilers = {
    'c': '^CC=clang;^CXX=clang++;^CCACHE_CC=clang;^CXXFLAGS=-fcolor-diagnostics;',
    'g': '^CC=gcc;^CXX=g++;',
    'P': ''
}

Optimizations = {
    'o': '+optimize!debug',
    'd': '!optimize+debug',
    'D': '+optimize+debug',
}

Architectures = {
    '4': '^CC=-m32;^CXX=-m32;\'--target=i686-linux-gnu;',
    '8': '^CC=-m64;^CXX=-m64;',
    'X': '^CC=-mx32;^CXX=-mx32;',
    'D': '',
}

FlagChars = set(('^', '+', '=', '!', '\'', '*', '.'))

def show(env, args):
    print("Environment:")
    for k, v in env.items():
        print('\t%s: %s' % (k, v))
    print("Arguments:")
    for arg in args:
        print('\t%s' % arg)

    short = ""
    for k, v in env.items():
        short += '{}="{}"'.format(k, v) + " "
    short += "./configure"
    for arg in args:
        short += " " + arg
    print('\n')
    print(short)

def to_string(env, args):
    envs = ' '.join(["%s=%s" % (k, v) for k, v in env.items()])
    return "%s %s" % (envs, ' '.join(args))

def help_syntax():
    print("Showing help for wfm-conf:")
    print("\t-s/--show      Show selected configure env/args.")
    print("\t-t/--test=DIR  Test the given dirname.")
    print("")

    print("Compilers:")
    for k in sorted(Compilers.keys()):
        parse_flags(Compilers[k])
        print("\t%s: %s" % (k, to_string(Environment, Arguments)))
        reset()
    print("")

    print("Optimizations:")
    for k in sorted(Optimizations.keys()):
        parse_flags(Optimizations[k])
        print("\t%s: %s" % (k, to_string(Environment, Arguments)))
        reset()
    print("")

    print("Architectures:")
    for k in sorted(Architectures.keys()):
        parse_flags(Architectures[k])
        print("\t%s: %s" % (k, to_string(Environment, Arguments)))
        reset()
    print("")

    print("Multi Char Shortcuts (.)")
    for k in sorted(MultiCharShortcuts.keys()):
        parse_flags(MultiCharShortcuts[k])
        print("\t%s: %s" % (k, to_string(Environment, Arguments)))
        reset()
    print("")

    print("Single Char Shortcuts (*)")
    for k in sorted(SingleCharShortcuts.keys()):
        parse_flags(SingleCharShortcuts[k])
        print("\t%s: %s" % (k, to_string(Environment, Arguments)))
        reset()
    print("")

    print("""
Grammar = Compiler & OptimizationLevel & Architecture & Flag*

  Flags:
    Enable argument with --enable-$TEXT:
       +TEXT
    Enable argument with --with-$TEXT:
       =TEXT
    Disable argument with --disable-$TEXT:
       !TEXT
    Send literal argument $TEXT:
       'TEXT;
    Environment Variable:
       ^FLAG=foo;
    Expand all single char shortcuts with --enable-$REP:
       *abcd
    Expand all multi char shortcuts recursively:
       .name
""")

Environment = {}
Arguments = []
def reset():
    global Environment
    global Arguments
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
        k = k.strip()
        v = v.strip()
        if k not in Environment:
            Environment[k] = v
        else:
            Environment[k] = Environment[k] + ' ' + v
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
    parse_flags(Compilers[flag])
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

def parse_toplevel(t):
    if len(t) < 3:
        raise ParseError('String requires at least a compiler, optimization, and arch flag.', t)
    t = parse_compiler(t)
    t = parse_optimization(t)
    t = parse_architecture(t)
    t = parse_flags(t)
    res = Environment, Arguments
    reset()
    return res

def parse(t):
    try:
        return parse_toplevel(t)
    except ParseError as e:
        print(str(e))
        if e.context in t:
            pos = len(t) - len(e.context)
            print("Context: %s" % t)
            print("         %s^" % ('-' * pos))

def create(target):
    res = parse(target)
    if not res:
        return 1
    environment = res[0]
    confargs = res[1]

    # Make the directory if it doesn't exist.
    pwd = os.getcwd()
    confdir = os.path.realpath(os.path.join(pwd, target))
    if not os.path.exists(confdir):
        os.mkdir(confdir)

    # Create the context link, if there is not already one.
    if not os.path.islink('ctx'):
        os.symlink(confdir, 'ctx')

    # If configure exists in the current directly, run autoconf to make sure it
    # is up to date before we configure.
    if os.path.isfile('configure.in'):
        subprocess.call(['autoconf-2.13'])

    # Run configure.
    inherited = ('PATH', 'SHELL', 'TERM', 'COLORTERM', 'MOZILLABUILD')
    env = {k: os.environ[k] for k in inherited if k in os.environ}
    conf = subprocess.Popen(['../configure'] + confargs, env=env, cwd=confdir)
    conf.wait()

def main():
    parser = argparse.ArgumentParser(description='Configure SpiderMonkey.')
    parser.add_argument('-s', '--show', action='store_true',
                        help="Print the behavior of the current ctx.")
    parser.add_argument('-t', '--test', metavar='CONFIG',
                        help="Print the behavior of the given directory.")
    parser.add_argument('--syntax', action="store_true",
                        help="Help with the syntax.")
    parser.add_argument('builddir', metavar='CONTEXT', default='ctx', type=str,
                        nargs='?', help='The configuration to use.')
    args, extra = parser.parse_known_args()

    if args.syntax:
        help_syntax()
        return 0

    if args.show:
        args.test = os.path.basename(os.readlink('ctx'))

    if args.test:
        # Show the result of parsing the passed string.
        res = parse(args.test)
        if not res:
            return 1
        show(res[0], res[1])
        return 0

    if args.builddir == 'ctx':
        args.builddir = os.path.basename(os.readlink('ctx'))
    create(args.builddir)

    return 0

if __name__ == '__main__':
    sys.exit(main())

