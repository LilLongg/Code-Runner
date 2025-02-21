def main():
    import argparse
    import os
    import textwrap
    import subprocess
    import sys
    import shlex

    arg_parser = argparse.ArgumentParser(
        description="Run a file with specified arguments.",
        add_help=True,
        allow_abbrev=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
                               Supported languages:
                               - C (.c)
                               - C++ (.cpp, .cxx, .c++, .cc)
                               - Python (.py, .py3)
        """),
    )
    arg_parser._actions[0].help = "Show this help message and exit."
    arg_parser.add_argument(
        "FILENAMES",
        help="Path to the files to be executed.",
        type=str,
        nargs="+",
    )
    arg_parser.add_argument(
        "-a", "--arguments", help=r"Execution file's arguments.", type=str
    )
    arg_parser.add_argument(
        "-e", "--execargs", help=r"Execution language's arguments.", type=str
    )
    args = arg_parser.parse_args(args=None if sys.argv[1:] else ["-h"])
    FULL_FILENAMES: list[str] = args.FILENAMES
    NAMED_FILE = FULL_FILENAMES[0]
    file_name, file_extension = os.path.splitext(NAMED_FILE)
    file_args: list[str] = shlex.split(args.arguments) if args.arguments else []
    exec_args: list[str] = shlex.split(args.execargs) if args.execargs else []

    C_EXTENSION = {".c"}
    CPP_EXTENSION = {".cc", ".cpp", ".c++", ".cxx"}
    PYTHON_EXTENSION = {".py", ".py3"}

    if file_extension in C_EXTENSION:
        output_file = file_name
        for idx, arg in enumerate(exec_args):
            if arg == "-o":
                output_file = exec_args[idx + 1]
                break
        else:
            exec_args += ["-o", output_file]
        subprocess.run(["gcc", *FULL_FILENAMES, *exec_args], check=True)

        if not os.path.isabs(output_file):
            output_file = f"./{output_file}"

        if os.access(output_file, os.X_OK):
            subprocess.run([output_file, *file_args], check=True)

    if file_extension in CPP_EXTENSION:
        output_file = file_name
        for idx, arg in enumerate(exec_args):
            if arg == "-o":
                output_file = exec_args[idx + 1]
                break
        else:
            exec_args += ["-o", output_file]
        subprocess.run(["g++", *FULL_FILENAMES, "-std=c++23", *exec_args], check=True)

        if not os.path.isabs(output_file):
            output_file = f"./{output_file}"

        if os.access(output_file, os.X_OK):
            subprocess.run([output_file, *file_args], check=True)

    if file_extension in PYTHON_EXTENSION:
        subprocess.run(["python", *exec_args, *FULL_FILENAMES, *file_args], check=True)
