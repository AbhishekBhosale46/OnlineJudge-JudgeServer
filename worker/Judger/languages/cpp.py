from .base import BaseLanguage


class CppLanguage(BaseLanguage):

    """
    CppLanguage handles compilation and execution of C++ programs within a Docker container.
    """

    def __init__(self, container, time_limit, memory_limit):
        """
        Initializes CppLanguage with the Docker container.

        Parameters:
        - container: The Docker container.
        - time_limit: Time limit in seconds.
        - memory_limit: Memory limit in mbs.
        """

        self.container = container
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    def compile(self, submission_id):
        """
        Compile the cpp code

        Returns:
        - exit_code - exit code of the executed compile command
        - compile_output - output of the compiliation
        """

        compile_cmd = f"/bin/sh -c 'g++ -o {submission_id}/UserProgram {submission_id}/UserProgram.cpp' "
        exit_code, compile_output = self.container.exec_run(compile_cmd)
        return exit_code, compile_output.decode('utf-8')

    def run(self, submission_id):
        """
        Run the cpp code with the input file and redirect the output to the file

        Returns:
        - exit_code - exit code of the executed run command
        - run_output - output of the user program
        """

        run_cmd = f"/bin/sh -c 'timeout {self.time_limit} {submission_id}/UserProgram < {submission_id}/ip.txt > {submission_id}/actual_op.txt' "
        exit_code, run_output = self.container.exec_run(run_cmd, stderr=True, stdout=True, stdin=True)
        return exit_code, run_output.decode('utf-8')
