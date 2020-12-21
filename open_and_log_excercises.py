import argparse
import pathlib
import platform
import subprocess
import sys

if __name__ == '__main__':

    system = platform.system()
    if system == "Windows":
        browser = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    elif system == "Linux":
        browser = "google-chrome"
    else:
        sys.stderr.write("OS not supported.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', type=str, required=True)

    args = parser.parse_args()

    input_file = pathlib.Path(args.inputfile)
    output_file = input_file.with_name("{}_completed.txt".format(input_file.stem))

    with input_file.open() as fp:
        input_lines = fp.readlines()

    while len(input_lines) > 0:
        current_line = input_lines.pop(0)
        with output_file.open("a") as fp:
            fp.write(current_line)

        with input_file.open('w') as fp:
            fp.writelines(input_lines)

        url = current_line.split(';')[1].strip()
        p = subprocess.Popen((browser, "--new-window", url))
        input()

        with output_file.open("a") as fp:
            fp.write(current_line)
