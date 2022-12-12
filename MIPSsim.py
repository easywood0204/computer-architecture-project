from function import MipsSimulator
import argparse


def mips_spliter(raw_string: str):
    strip_string = raw_string.rstrip(' \t\n')
    return strip_string


def mips_file_reader(file_path: str):
    file_line_list = []
    with open(file_path) as f:
        while True:
            line = f.readline()
            if not line:
                break
            else:
                file_line_list.append(mips_spliter(line))
        f.close()
    return file_line_list


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help="input file path")
    return parser.parse_args()


if __name__ == "__main__":
    args = args_parser()
    instructions_list = mips_file_reader(file_path=args.file_path)
    simulator = MipsSimulator()
    simulator.disassemble(instructions_list)
    # simulator.execution_simulate()
    simulator.pipelined_simulate()
