import asyncio
import tempfile
import os
from ..shared import adjust_command, eprint, debug_print
import subprocess
import time

class ExecutorLogger:
    def __init__(self):
        self._data = []

    def log(self, cmd, stdout_name, stderr_name, returncode):
        self._data.append((cmd, stdout_name, stderr_name, returncode))
        #print("stdout_name, stderr_name", stdout_name, stderr_name)

    def flush(self):
        stdout_fd, stdout_name = tempfile.mkstemp(prefix='pyfind-exec-complete-', suffix='.stdout')
        stderr_fd, stderr_name = tempfile.mkstemp(prefix='pyfind-exec-complete-', suffix='.stderr')

        def write(fd, cmd_, data):
            os.write(fd, cmd_)
            os.write(fd, data)
            os.write(fd, b"\n")

        for item in self._data:
            cmd, input_stdout_name, input_stderr_name, returncode = item
            cmd_ = (" ".join(cmd) + "\n").encode('utf-8')
            with open(input_stdout_name, 'rb') as f:
                write(stdout_fd, cmd_, f.read())
            with open(input_stderr_name, 'rb') as f:
                write(stderr_fd, cmd_, f.read())
        os.close(stdout_fd)
        os.close(stderr_fd)

        eprint("stdout data saved to {}".format(stdout_name))
        eprint("stderr data saved to {}".format(stderr_name))

class Executor:
    def exec(self, cmd):
        pass
    async def wait(self):
        pass

class SyncExecutor(Executor):
    def exec(self, cmd):
        cmd_ = adjust_command(cmd)
        debug_print("SyncExecutor.run", cmd_)
        subprocess.run(cmd_)

class XargsExecutor(Executor):
    def __init__(self, cmd):
        super().__init__()
        self._paths = []
        self._cmd = cmd
    
    def append(self, path):
        self._paths.append(path)

    async def wait(self):
        cmd_ = adjust_command(self._cmd + self._paths)
        subprocess.run(cmd_)

async def executor_worker(name, queue: asyncio.Queue, logger: ExecutorLogger):
    t0 = time.time()
    while True:
        debug_print(name, "waiting for new task")
        cmd = await queue.get()
        t1 = time.time()
        debug_print(name, "got task")
        
        stdout_fd, stdout_name = tempfile.mkstemp(prefix='pyfind-exec-', suffix='.stdout')
        stderr_fd, stderr_name = tempfile.mkstemp(prefix='pyfind-exec-', suffix='.stderr')

        cmd_ = adjust_command(cmd)

        debug_print(name, "running", cmd)
        proc = await asyncio.subprocess.create_subprocess_exec(*cmd_, stdout=stdout_fd, stderr=stderr_fd)
        
        debug_print(name, "wait process to complete")
        await proc.wait()

        os.close(stdout_fd)
        os.close(stderr_fd)

        logger.log(cmd, stdout_name, stderr_name, proc.returncode)

        t2 = time.time()

        debug_print(name, "process completed, returncode", proc.returncode, "time", (t1 - t0), (t2 - t0))
        queue.task_done()

class AsyncExecutor(Executor):

    def __init__(self, n = None):
        super().__init__()
        queue = asyncio.Queue()
        if n is None:
            n = os.cpu_count()
        debug_print("create {} workers".format(n))
        workers = []
        logger = ExecutorLogger()
        for i in range(n):
            task = asyncio.create_task(executor_worker("worker {}".format(i), queue, logger))
            workers.append(task)
        self._queue = queue
        self._workers = workers
        self._n = n
        self._logger = logger
    
    def exec(self, cmd):
        self._queue.put_nowait(cmd)

    async def wait(self):
        queue = self._queue

        debug_print("join queue")
        await queue.join()
        debug_print("queue joined")

        debug_print("terminating workers")
        workers = self._workers
        for task in workers:
            task.cancel()
        asyncio.gather(*workers, return_exceptions=True)
        debug_print("workers terminated")

        self._logger.flush()
