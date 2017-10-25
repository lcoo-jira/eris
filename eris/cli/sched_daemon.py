#! /usr/bin/env python

import json
import subprocess
import os
import uuid
import time
import argparse

# TODO: This whole file needs a whole bunch of logging
# without logging we are blind to what's happening in there
# Add robust logging.
# TODO: See if https://github.com/dbader/schedule is a better alternative
class Job(object):
    """
    The main job object. Currently, the only type of
    jobs supported at this time are those that need
    to run at a specific time. There is no dependency
    graph. The class runs ansible commands. The input
    is an inventory file, a module with arguments and
    time variables when to run the job and on which host.
    """

    ONETIME = 1
    RECURRING = 2

    def __init__(self,
                 outdir,
                 cmd,
                 run_at=None,
                 repeat=None,
                 until=None):
        """
        Create a one-time or a repetitive job

        :param logger: The logger to be used
        :param outdir: The output directory for the job
        :param cmd: The job command line
        :param run_at: Run run_at + now()  seconds
        :param repeat: Run every repeat seconds
        :param until: Run until now + until seconds \
                Only valid when repeat is there.
        :type logger: logging.Logger
        :type outdir: str
        :type cmd: list
        :type run_at: int
        :type repeat: int
        :type until: int
        :returns: None
        :raises ValueError: if repeat or until is specified \
                without the other. If logger is None this is \
                thrown as well.
        """
        
        current_time = time.time()

        if ((repeat is None and until is not None) or
                (repeat is not None and until is None)):
            raise ValueError('both repeat and until need to be specified')

        if repeat is None:
            self.jtype = Job.ONETIME
        else:
            self.jtype = Job.RECURRING
        
        self.cmd = cmd
        self.run_at = current_time + run_at
        self.repeat = repeat
        self.until = current_time + until

        self.id = uuid.uuid4()
        self.outfile = os.path.join(outdir, str(self.id))
        self.popen = None

    def __eq__(self, another_job):
        return self.id == another_job.id if another_job is not None else False

    def __ne__(self, another_job):
        return self.id != another_job.id if another_job is not None else True

    def __hash__(self):
        return hash(self.id)

    def recurring(self):
        """
        Is the job onetime or recurring.

        :returns: True if recurring False if onetime
        :rtype: boolean
        """

        return self.jtype == Job.RECURRING

    def expired(self):
        """
        Has the recurring job expired? 
        Or has the one time job been run?

        :returns: True if expired
        :rtype: boolean
        """
        
        # A recurring job is expired when 
        # the current time is past its until time
        # A onetime job is expired after it is run
        current_time = time.time()
        if self.recurring():
            return current_time >= self.until
        else:
            return self.started() and self.finished()

    def set_next_run(self):
        """
        Update the run_at value for
        recurring jobs to be now + repeat
        Can be called on onetime jobs without any effect
        """

        if self.recurring():
            self.run_at = time.time() + self.repeat

    def ready(self):
        """
        Is the job ready to be executed

        :returns: True or false on whether the job can be run
        :rtype: boolean
        """

        # Ready to run if the current time is >= the run_at time
        current_time = time.time()
        if self.jtype == Job.ONETIME:
            return current_time >= self.run_at
        elif self.jtype == Job.RECURRING:
            return current_time >= self.run_at and current_time < self.until
        else:
            # Really - it shouldn't get here at all
            # But if we do by some bad luck - this is something
            # we don't know about.
            # So, always return false
            return False

    def started(self):
        """
        Has the job been started. This is when run_job is called
        This is provided as a courtesy method. It needs to be called
        before checking for finished.

        :returns: If the job has been started
        :rtype: boolean
        """

        return self.popen is not None

    def finished(self):
        """
        Lets the caller know if the job is finished
        Called started to see if the job has aready been started

        :returns: If the job has been completed
        :rtype: boolean
        """

        return self.popen.poll() is not None

    def returncode(self):
        """
        Gets the return code of the job
        Ensure that the job is finished before requesting the return code

        :returns: The returncode of the process
        :rtype: int
        """

        return self.popen.returncode

    def stop(self):
        """
        Stops the process. Call with care
        This will terminate a process when it is executing

        :returns: None
        """

        if self.started() and not self.finished():
            self.popen.kill()

    def run_job(self):
        """
        Run the job as a subprocess

        :returns: A Pipe to the subprocess Popen command
        :rtype: subprocess.Popen
        """

        # NOTE: The with context for the output actually works here
        # You should notice that in the context of unix subprocess
        # the file descriptor should be closed in the parent but
        # open in the child. That is exactly what the context does
        # It closes fid in the parent but the child process still has
        # it open and will close when complete.
        with open(self.outfile, 'w+') as fid:
            current_time = time.time()
            header_string = '\n\n' + str(self.id) + ':' + str(current_time) + '\n'
            fid.write(header_string)
            self.popen = subprocess.Popen(self.cmd, stdout=fid, stderr=fid)

        return self.popen


class Scheduler(object):
    """
    The main scheduler class. 
    1. It maintains a list of jobs
    2. It looks to see which jobs are ready and starts them
    3. It removes finished jobs to conserve memory
    4. It recreates recurring jobs back in the job list
    5. It listens to HTTP JSON requests, created new jobs \
            and can provide simple status on existing jobs

    The scheduler is very simple - it reads off a directory
    specified in the constructor for jobs. There is no job 
    control - once in the scheduler a job cannot be deleted.
    """
    # TODO: Add better mechanism to manage jobs. Options are
    # using a named pipe, unix socket, 127.0.0.1:<port>, etc.
    # Custom protocol or using http.

    def __init__(self, job_dir, poll_interval=5):
        """
        Create a scheduler

        :param job_dir: The job directory
        :param poll_interval: How often to check the job directory
        :type job_dir: str
        :type poll_interval: int
        :returns: None
        :raises IOError: if the job dir does not exist and \
                can't be created.
        :raises ValueError: if the poll_interval < 5 and > 60
        """

        self.job_dir = job_dir
        self.poll_interval = poll_interval
        self.pending_jobs = set()
        self.running_jobs = set()
    
    def loop_forever(self):
        """
        Main loop job. Will exist when the stop
        command is added into the job directory

        There are two types of commands that can be
        added to the queue. 
        {"type": "JOB", <...job payload...>}
        {"type": "CMD", "value": "STOP"}
        """

        stop = False
        while not stop:
            file_list = os.listdir(self.job_dir)
            for x in file_list:
                if x.endswith('.json') is False:
                    continue
                file_value = None 
                complete_path = os.path.join(self.job_dir, x)
                if os.path.isfile(complete_path) is False:
                    continue
                with open(complete_path, 'r') as fid:
                    try:
                        file_value = json.load(fid)
                    except:
                        # Don't care if it fails.
                        # Ignore
                        pass
               
                # We have the JSON/dict - now get rid of the file
                os.remove(complete_path)
                if file_value is None:
                    continue

                if file_value.get('type','something') == 'JOB':
                    j = Job(file_value.get('outdir'),
                            file_value.get('cmd'),
                            file_value.get('run_at', None),
                            file_value.get('repeat', None),
                            file_value.get('until', None))
                    self.pending_jobs.add(j)
                elif file_value.get('type','something') == 'CMD':
                    stop = True
                    break
                else:
                    # Some junk - ignore
                    pass
            if not stop:
                self.run_jobs()

                # Wait for the poll interval
                time.sleep(self.poll_interval)
        
        # Ok - got a stop and we're out of the loop here
        # Stop all the jobs
        self.stop()

    def run_jobs(self):
        """
        Main task that selects and runs jobs

        This is currently a super simple algorithm
        1. Remove all the completed jobs and pick the ready jobs
        2. Check is any of the ready jobs are running - for RECURRING
           2.1 Remove those
        3. Take the rest of the jobs, map them into a process pool of 10
        """
        
        # Step 1: Get all the finished jobs
        finished_jobs = set(filter(lambda j: j.started() and j.finished(), self.running_jobs))

        # Step 2: Get all the recurring jobs that are finished
        recurring_jobs = set(filter(lambda j: j.recurring() and not j.expired(), finished_jobs))
        
        # Step 3: Remove the finished jobs from the running jobs
        self.running_jobs.difference_update(finished_jobs)

        # Step 4: Add the recurring jobs back to the pending jobs
        self.pending_jobs.update(recurring_jobs)
        
        # Step 5: Get all the jobs that are ready to run
        jobs_to_run = set(filter(lambda j: j.ready(), self.pending_jobs))

        # Step 6: Remove the jobs ready to run from the pending jobs
        self.pending_jobs.difference_update(jobs_to_run)

        # Step 7: Start all jobs ready to run
        map(lambda j: j.run_job(), jobs_to_run)

        # Step 8: Update the next run time. No effect for onetime jobs
        map(lambda j: j.set_next_run(), jobs_to_run)

        # Step 9: Add the running jobs to the list of running jobs
        self.running_jobs.update(jobs_to_run)


    def stop(self):
        """
        Stop all running jobs. This is the last thing to run
        """

        map(lambda j: j.stop(), self.running_jobs)

def main():
    """
    The main function to start the scheduler. 

    :param argv: The argument vector which is sys.argv
    :type argv: list
    :returns: None
    """

    parser = argparse.ArgumentParser(description='Schedule one time or recurring jobs based in the short term')
    parser.add_argument('--jobdir',
                        action='store',
                        dest='jobdir',
                        default='/tmp',
                        help='The directory where jobs are picked up')
    parser.add_argument('--poll-interval',
                        action='store',
                        dest='poll_interval',
                        type=int,
                        default=5,
                        help='The poll interval for picking and scheduling jobs')
    
    args = parser.parse_args()
    scheduler = Scheduler(args.jobdir, args.poll_interval)
    scheduler.loop_forever()
    

if __name__ == '__main__':
    main()


