---
link-citations: true
---

Andrew's Behaviour Box
=======================

TODO:
-----

Making some major revisions to run the bbox without a digitizer. I'm going to change the way that the bbox outputs to be more inline with what is in the `TODO.md` file. 

It is going to take a single argument of the form:
`{stimulus}{light_stim}{light_resp}`
where each value is a boolean that is three bits, so it should be fast.

The bbox will then continuously output lick times as integers. Because we implement a forced delay between the rising and the falling of the lick time, we can insert the communication in this period. The thing is, I'm not sure I can guarantee transmission....

This will make the serial control much lighter, to the point that I won't need much of the existing overheads....