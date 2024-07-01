import os
import shutil
import uuid
from .docker_manager import DockerManager
from .languages.cpp import CppLanguage
from .languages.python import PythonLanguage


def get_language_instance(language, container, time_limit, memory_limit):
    """
    Returns an instance of the language-specific class based on the provided language.

    Parameters:
    - language (str): The programming language ('cpp', 'java', 'python').
    - container : The Docker container.
    - time_limit: Time limit in seconds.
    - memory_limit: Memory limit in mbs.

    Returns:
    - BaseLanguage: An instance of the language-specific class.
    """

    if language == 'cpp':
        return CppLanguage(container, time_limit, memory_limit)
    elif language == "py":
        return PythonLanguage(container, time_limit, memory_limit)
    else:
        raise ValueError("Unsupported language")


def run_judger(language, time_limit, memory_limit,
               judger_vol_path, src_code=None, std_in=None, expected_out=None,
               src_code_path=None, std_in_path=None, expected_out_path=None):
    """
    Orchestrates the compilation and execution of the provided source code within a Docker container.

    Parameters:
    - language (str): The programming language ('cpp', 'java', 'py').
    - time_limit (int): Time limit in seconds.
    - memory_limit (int): Memory limit in mbs.
    - judger_vol_path (path): Path of the directory to be mounted as container volume.
    - src_code (str): Source code to be executed
    - std_in (str): Std input passed to program
    - expected_out (str): Expected output of the program
    - source_code_path (path): Source code file path.
    - expected_out_path (path): Expected output file path.
    - std_in_path (str, optional): Input testcase file path.

    Returns:
    - status (str): Status of the task.
    """

    # Get the container instance
    dm = DockerManager(time_limit=time_limit, memory_limit=memory_limit, judger_vol_path=judger_vol_path)
    container = dm.get_container()

    # Get the specific language instance
    language_instance = get_language_instance(language, container, time_limit, memory_limit)

    # Create unique submission id for each submission
    submission_id = str(uuid.uuid4())

    try:

        submission_dir = f'{judger_vol_path}/{submission_id}'
        os.makedirs(submission_dir)

        # copy source code to container
        if src_code_path:
            shutil.copy(src_code_path, os.path.join(submission_dir, f"UserProgram.{language}"))
        elif src_code:
            with open(os.path.join(submission_dir, f"UserProgram.{language}"), "w") as file:
                file.write(src_code)
        else:
            raise ValueError("Source code not provided")

        # copy input to container
        if std_in_path:
            shutil.copy(std_in_path, os.path.join(submission_dir, "ip.txt"))
        elif std_in:
            with open(os.path.join(submission_dir, f"ip.txt"), "w") as file:
                file.write(std_in)
        else:
            raise ValueError("Input testcase not provided")

        # copy expected output to container
        if expected_out_path:
            shutil.copy(expected_out_path, os.path.join(submission_dir, "expected_op.txt"))
        elif expected_out:
            with open(os.path.join(submission_dir, f"expected_op.txt"), "w") as file:
                file.write(expected_out)
        else:
            raise ValueError("Expected output not provided")

        # Compile the code
        if language in ["cpp", "java"]:
            compile_exit_code, compile_output = language_instance.compile(submission_id=submission_id)
            if compile_exit_code == 1:
                return "CE"

        # Run the code
        run_exit_code, run_output = language_instance.run(submission_id=submission_id)

        # If no errors then check for WA or AC
        if run_exit_code == 0:
            with open(f"{submission_dir}/expected_op.txt", "r") as f:
                expected_op_data = f.read()
            with open(f"{submission_dir}/actual_op.txt", "r") as f:
                actual_op_data = f.read()
            if actual_op_data.strip() == expected_op_data.strip():
                return "AC"
            else:
                return "WA"

        # Return the status if run_exit_code is non zero
        if run_exit_code == 1:
            return "RE"
        elif run_exit_code == 143:
            return "TLE"
        elif run_exit_code == 137:
            return "MLE"
        else:
            return "UNKNOWN"

    except Exception as e:

        print(f"EXCEPTION OCCURED : {e}")

    finally:

        # Cleanup the mounted volume
        language_instance.cleanup(submission_id=submission_id)


def custom_run(language, time_limit, memory_limit,
               judger_vol_path, src_code=None, std_in=None, src_code_path=None):
    """
    Function to run custom test case with given output.

    Parameters:
    - language (str): The programming language ('cpp', 'java', 'py').
    - time_limit (int): Time limit in seconds.
    - memory_limit (int): Memory limit in mbs.
    - judger_vol_path (path): Path of the directory to be mounted as container volume.
    - src_code (str): Source code to be executed
    - std_in (str): Std input passed to program
    - source_code_path (path): Source code file path.
    - std_in_path (str, optional): Input testcase file path.

    Returns:
    - status (str): Status of the task.
    """

    # Get the container instance
    dm = DockerManager(time_limit=time_limit, memory_limit=memory_limit, judger_vol_path=judger_vol_path)
    container = dm.get_container()

    # Get the specific language instance
    language_instance = get_language_instance(language, container, time_limit, memory_limit)

    # Create unique submission id for each submission
    submission_id = str(uuid.uuid4())

    try:

        submission_dir = f'{judger_vol_path}/{submission_id}'
        os.makedirs(submission_dir)

        # Create empty input file
        open(f"{submission_dir}/ip.txt", "x")

        # copy source code to container
        if src_code_path:
            shutil.copy(src_code_path, os.path.join(submission_dir, f"UserProgram.{language}"))
        elif src_code:
            with open(os.path.join(submission_dir, f"UserProgram.{language}"), "w") as file:
                file.write(src_code)
        else:
            raise ValueError("Source code not provided")

        # copy input to container
        if std_in:
            with open(os.path.join(submission_dir, f"ip.txt"), "w") as file:
                file.write(std_in)
        else:
            raise ValueError("Input testcase not provided")

        # Compile the code
        if language in ["cpp", "java"]:
            compile_exit_code, compile_output = language_instance.compile(submission_id=submission_id)
            if compile_exit_code == 1:
                return "CE"

        # Run the code
        run_exit_code, run_output = language_instance.run(submission_id=submission_id)

        with open(os.path.join(submission_dir, f"actual_op.txt"), "r") as file:
            run_output = file.read()

        # If no errors then check for WA or AC
        if run_exit_code == 0:
            return "AC", run_output

        # Return the status if run_exit_code is non zero
        if run_exit_code == 1:
            return "RE"
        elif run_exit_code == 143:
            return "TLE"
        elif run_exit_code == 137:
            return "MLE"
        else:
            return "UNKNOWN"

    except Exception as e:

        print(f"EXCEPTION OCCURED : {e}")

    finally:

        # Cleanup the mounted volume
        language_instance.cleanup(submission_id=submission_id)