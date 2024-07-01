from .base import BaseLanguage


class PythonLanguage(BaseLanguage):

    """
    PythonLanguage handles execution of Python programs within a Docker container.
    """

    def __init__(self, container, time_limit, memory_limit):
        """
        Initializes PythonLanguage with the Docker container.

        Parameters:
        - container: The Docker container.
        - time_limit: Time limit in seconds.
        - memory_limit: Memory limit in mbs.
        """
        self.container = container
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    def run(self, submission_id):
        """
        Run the python code

        Returns:
        - exit_code - exit code of the executed run command
        - run_output - output of the user program
        """

        run_cmd = f"/bin/sh -c 'timeout {self.time_limit} python {submission_id}/UserProgram.py < {submission_id}/ip.txt > {submission_id}/actual_op.txt' "
        exit_code, run_output = self.container.exec_run(run_cmd, stderr=True, stdout=True, stdin=True)
        return exit_code, run_output.decode('utf-8')

    def compile(self):
        return 0, "No compilation needed for Python"
