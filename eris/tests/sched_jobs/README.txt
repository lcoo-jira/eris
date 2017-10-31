For running jobs at specified intervals or time triggers eris uses a
scheduler. This scheduler is necessary because the linux/unix "at" may
or may not be installed with certain distributions as it is considered
a security risk. The scheduler lives and dies with the test case and
polls for jobs in this directory. This is where the jobs for failure
injection and monitoring are scheduled.
