#!/usr/bin/env python3
import sys

def asPairs(fp):
    out = []
    for line in fp:
        if not line or line.startswith('-'):
            continue
        before, _, after = line.partition(": ")
        out.append((before.strip(), after.strip()))
    return out

with open(sys.argv[1]) as fp:
    out0 = asPairs(fp)
with open(sys.argv[2]) as fp:
    out1 = asPairs(fp)

def red():   print("\x1b[31;2m", end='')
def green(): print("\x1b[32;2m", end='')
def reset(): print("\x1b[0m", end='')

assert len(out0) == len(out1)
for i, (k0, v0) in enumerate(out0):
    k1, v1 = out1[i]
    assert k0 == k1
    delta = (int(v1) - int(v0)) / float(v0) * 100.0
    print("{:17} | {:>6} -> {:>6} = ".format(k0, v0, v1), end='')
    if delta > 0: green()
    else: red()
    print("{:=+7.02f}%".format(delta))
    reset()
