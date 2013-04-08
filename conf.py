#!/usr/bin/python2

import getopt
import os
import os.path
import sys

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
    'c': '^CC=clang;^CPP=clang++;',
    'g': '^CC=gcc;^CPP=g++;',
    'D': ''
}

Optimizations = {
    'o': '+optimize!debug',
    'd': '!optimize+debug',
    'D': '+optimize+debug',
}

Architectures = {
    '4': '^CC=-m32;^CPP=-m32;',
    '8': '^CC=-m64;^CPP=-m64;',
    'X': '^CC=-mx32;^CPP=-mx32;',
    'D': '',
}

FlagChars = set(('^', '+', '=', '!', '\'', '*', '.'))

def show(env, args):
    print "Environment:"
    for k, v in env.items():
        print '\t%s: %s' % (k, v)
    print "Arguments:"
    for arg in args:
        print '\t%s' % arg

def to_string(env, args):
    envs = ' '.join(["%s=%s" % (k, v) for k, v in env.items()])
    return "%s %s" % (envs, ' '.join(args))

def help():
    print "Showing help for wfm-conf:"
    print "\t-s/--show      Show selected configure env/args."
    print "\t-t/--test=DIR  Test the given dirname."
    print ""

    print "Compilers:"
    for k in sorted(Compilers.keys()):
        parse_flags(Compilers[k])
        print "\t%s: %s" % (k, to_string(Environment, Arguments))
        reset()
    print ""

    print "Optimizations:"
    for k in sorted(Optimizations.keys()):
        parse_flags(Optimizations[k])
        print "\t%s: %s" % (k, to_string(Environment, Arguments))
        reset()
    print ""

    print "Architectures:"
    for k in sorted(Architectures.keys()):
        parse_flags(Architectures[k])
        print "\t%s: %s" % (k, to_string(Environment, Arguments))
        reset()
    print ""

    print "Multi Char Shortcuts (.)"
    for k in sorted(MultiCharShortcuts.keys()):
        parse_flags(MultiCharShortcuts[k])
        print "\t%s: %s" % (k, to_string(Environment, Arguments))
        reset()
    print ""

    print "Single Char Shortcuts (*)"
    for k in sorted(SingleCharShortcuts.keys()):
        parse_flags(SingleCharShortcuts[k])
        print "\t%s: %s" % (k, to_string(Environment, Arguments))
        reset()
    print ""

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

def parse(t):
    if len(t) < 3:
        raise ParseError('String requires at least a compiler, optimization, and arch flag.', t)
    t = parse_compiler(t)
    t = parse_optimization(t)
    t = parse_architecture(t)
    t = parse_flags(t)
    res = Environment, Arguments
    reset()
    return res

def get_opt(short, long, opts):
    for opt, optarg in opts:
        if (opt == long or opt == short) and optarg:
            return optarg
    return None

def main():
    optlist, extra = getopt.gnu_getopt(sys.argv, 'hst:', ['help', 'show', 'test='])

    cwd = os.getcwd()
    directory = os.path.basename(cwd)
    parent = os.path.dirname(cwd)
    configure = os.path.join(parent, 'configure')

    t = get_opt('-t', '--test', optlist)
    if t is not None:
        optlist.append(('--show', ''))
        directory = t
    elif ('--help', '') in optlist or ('-h', '') in optlist:
        help()
        return 0
    elif not os.path.exists(configure):
        print "No 'configure' in parent directory!"
        return 1

    try:
        env, args = parse(directory)
    except ParseError, e:
        print str(e)
        if e.context in directory:
            pos = len(directory) - len(e.context)
            print "Context: %s" % directory
            print "         %s^" % ('-' * pos)
            return 1

    if ('--show', '') in optlist or ('-s', '') in optlist:
        show(env, args)

    else:
        os.execve(configure, [configure] + args, env)

    return 0

if __name__ == '__main__':
    sys.exit(main())

