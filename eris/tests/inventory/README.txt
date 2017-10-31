This one is a bit of a hack (well, even more so than the rest of the
process here (smile)). Sometimes when your inventory is derived out of
either an http(s) or an ssh connection it can get time consuming to do
inventory every time. So, this is where the inventory json is
pre-generated and stored for use. You really shouldn't need this if
you are using a file based inventory (described later).
