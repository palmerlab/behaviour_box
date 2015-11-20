# args.py
import argparse

p = argparse.ArgumentParser()

# accept two lists of arguments
# like -a 1 2 3 4 -b 1 2 3
p.add_argument('-a', nargs="+")
p.add_argument('-b', nargs="+", type=int)
args = p.parse_args()

a = args.a
print a

# check if input is valid
set_a = set(args.a)
set_b = set(args.b)


# check if "a" is in proper range.
if len(set_a - set(range(1, 51))) > 0: # can use also min(a)>=1 and max(a)<=50
    raise Exception("set a not in range [1,50]")

# check if "b" is in "a"
if len(set_b - set_a) > 0:
    raise Exception("set b not entirely in set a")

# you could even skip len(...) and leave just operations on sets
# ...