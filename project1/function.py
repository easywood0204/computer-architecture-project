import math
import os
import re


class MipsSimulator:
    def __init__(self):
        self.register_list = [0 for _ in range(32)]
        self.memory = dict()
        self.data_start = None
        self.data_end = None
        self.start_address = 64
        self.end = False
        self.disassembly_path = "output/disassembly.txt"
        self.simulation_file_path = "output/simulation.txt"

    def Category_1_R_TYPE(self, command):
        Rs = int(command[6:10 + 1], 2)
        Rt = int(command[11:15 + 1], 2)
        Rd = int(command[16:20 + 1], 2)
        if command[26:31 + 1] == "001000":  # JR
            return ["JR", "R" + str(Rs)]
        elif command[26:31 + 1] == "001101":  # BREAK
            self.end = True
            return ["BREAK"]
        elif command[26:31 + 1] == "000000":  # SLL
            sa = int(command[21:25 + 1], 2)
            return ["SLL", "R" + str(Rd), "R" + str(Rt), "#" + str(sa)]
        elif command[26:31 + 1] == "000010":  # SRL
            sa = int(command[21:25 + 1], 2)
            return ["SRL", "R" + str(Rd), "R" + str(Rt), "#" + str(sa)]
        elif command[26:31 + 1] == "000011":  # SRA
            sa = int(command[21:25 + 1], 2)
            return ["SRA", "R" + str(Rd), "R" + str(Rt), "#" + str(sa)]
        return None

    def Category_1_J_TYPE(self, command):
        if command[0:5 + 1] == "000010":  # J
            num = int(command[6:31 + 1] + "00", 2)
            return ["J", "#" + str(num)]
        return None

    def Category_1_I_TYPE(self, command):
        Rs = int(command[6:10 + 1], 2)
        Rt = int(command[11:15 + 1], 2)
        if command[0:5 + 1] == "000100":  # BEQ
            offset = int(command[16:31 + 1] + "00", 2)
            return ["BEQ", "R" + str(Rs), "R" + str(Rt), "#" + str(offset)]
        elif command[0:5 + 1] == "000111":  # BGTZ
            offset = int(command[16:31 + 1] + "00", 2)
            return ["BGTZ", "R" + str(Rs), "#" + str(offset)]
        elif command[0:5 + 1] == "101011":  # SW
            offset = int(command[16:31 + 1], 2)
            return ["SW", "R" + str(Rt), str(offset) + "(R" + str(Rs) + ")"]
        elif command[0:5 + 1] == "100011":  # LW
            offset = int(command[16:31 + 1], 2)
            return ["LW", "R" + str(Rt), str(offset) + "(R" + str(Rs) + ")"]
        return None

    def Category_1_REGIMM(self, command):
        if command[11:15 + 1] == "00000":  # BLTZ
            Rs = int(command[6:10 + 1], 2)
            offset = int(command[16:31 + 1] + "00", 2)
            return ["BLTZ", "R" + str(Rs), "#" + str(offset)]
        return None

    def Category_2_IMM_0(self, command):
        Rs = int(command[6:10 + 1], 2)
        Rt = int(command[11:15 + 1], 2)
        Rd = int(command[16:20 + 1], 2)
        comm = None
        if command[26: 31 + 1] == "100000":  # ADD
            comm = "ADD"
        elif command[26: 31 + 1] == "100010":  # SUB
            comm = "SUB"
        elif command[26: 31 + 1] == "000010":  # MUL
            comm = "MUL"
        elif command[26: 31 + 1] == "100100":  # AND
            comm = "AND"
        elif command[26: 31 + 1] == "100111":  # NOR
            comm = "NOR"
        elif command[26: 31 + 1] == "101010":  # SLT
            comm = "SLT"
        if comm is None:
            return None
        else:
            return [comm, "R" + str(Rd), "R" + str(Rs), "R" + str(Rt)]

    def Category_2_IMM_1(self, command):
        Rs = int(command[6:10 + 1], 2)
        Rt = int(command[11:15 + 1], 2)
        num = int(command[16:31 + 1], 2)
        comm = None
        if command[1: 5 + 1] == "10000":  # ADD
            comm = "ADD"
        elif command[1: 5 + 1] == "10001":  # SUB
            comm = "SUB"
        elif command[1: 5 + 1] == "00001":  # MUL
            comm = "MUL"
        elif command[1: 5 + 1] == "10010":  # AND
            comm = "AND"
        elif command[1: 5 + 1] == "10011":  # NOR
            comm = "NOR"
        elif command[1: 5 + 1] == "10101":  # SLT
            comm = "SLT"
        if comm is None:
            return None
        else:
            return [comm, "R" + str(Rt), "R" + str(Rs), "#" + str(num)]

    def disassemble(self, instructions: list[str]) -> None:
        NOP_CODE = "00000000000000000000000000000000"

        R_TYPE_opcode = ["000000"]
        J_TYPE_opcode = ["000010"]
        I_TYPE_opcode = ["000100", "000111", "101011", "100011"]
        REGIMM_opcode = ["000001"]

        now = self.start_address
        for command in instructions:
            new_command = None
            if self.end is False:
                if command == NOP_CODE:
                    new_command = "NOP"
                if new_command is None and command[0:5 + 1] in R_TYPE_opcode:
                    new_command = self.Category_1_R_TYPE(command)
                if new_command is None and command[0:5 + 1] in J_TYPE_opcode:
                    new_command = self.Category_1_J_TYPE(command)
                if new_command is None and command[0:5 + 1] in I_TYPE_opcode:
                    new_command = self.Category_1_I_TYPE(command)
                if new_command is None and command[0:5 + 1] in REGIMM_opcode:
                    new_command = self.Category_1_REGIMM(command)
                if new_command is None and command[0] == "0":
                    new_command = self.Category_2_IMM_0(command)
                if new_command is None and command[0] == "1":
                    new_command = self.Category_2_IMM_1(command)
            else:
                if self.data_start is None:
                    self.data_start = now
                new_command = [int(int(command[1:], 2) - int(command[0], 2) * math.pow(2, 31))]
            self.memory[str(now)] = new_command
            now += 4
        self.data_end = now - 4

        now = self.start_address
        if not os.path.exists(os.path.dirname(self.disassembly_path)):
            os.mkdir(os.path.dirname(self.disassembly_path))
        with open(self.disassembly_path, "w") as f:
            for command in instructions:
                if now < self.data_start:
                    w = [command[0:5 + 1], " ",
                         command[6: 10 + 1],  " ",
                         command[11: 15 + 1],  " ",
                         command[16: 20 + 1], " ",
                         command[21: 25 + 1], " ",
                         command[26:31 + 1], "\t",
                         str(now), "\t"]
                else:
                    w = [command, "\t",
                         str(now), " "]
                for i in range(len(self.memory[str(now)])):
                    w.append(str(self.memory[str(now)][i]))
                    if i == 0 and i != len(self.memory[str(now)])-1:
                        w.append(" ")
                    elif i != len(self.memory[str(now)])-1:
                        w.append(", ")
                    else:
                        w.append("\n")
                f.writelines(w)
                now += 4

    def print_simulation(self, command, cycle, program_counter):
        result_description = "--------------------\n"
        result_description += "Cycle:{0}\t{1}\t{2} {3}\n".format(
            cycle, program_counter, command[0], ", ".join(command[1:])
        )
        result_description += '\n'
        result_description += "Registers\n"
        result_description += "R00:\t{0}\n".format("\t".join(str(reg_value) for reg_value in self.register_list[0:16]))
        result_description += "R16:\t{0}\n".format("\t".join(str(reg_value) for reg_value in self.register_list[16:32]))
        result_description += '\n'
        result_description += "Data"
        counter = 0
        for addr, data in self.memory.items():
            if int(addr) < self.data_start:
                continue
            if int(addr) > self.data_end:
                break
            if counter == 0:
                result_description += '\n'
                result_description += "{0}:".format(addr)
            result_description += "\t{0}".format(data[0])
            counter = (counter+1) % 8
        result_description += '\n\n'

        if not os.path.exists(os.path.dirname(self.simulation_file_path)):
            os.mkdir(os.path.dirname(self.simulation_file_path))
        with open(self.simulation_file_path, 'a') as f:
            f.write(result_description)

    def execute_op(self, Rs, Rt, order):
        if order == "ADD":
            return Rs + Rt
        elif order == "SUB":
            return Rs - Rt
        elif order == "MUL":
            return Rs * Rt
        elif order == "AND":
            return Rs & Rt
        elif order == "NOR":
            return ~(Rs | Rt)
        elif order == "SLT":
            return Rs < Rt
        else:
            return None

    def execute_sl(self, mem_addr, reg_idx, order):
        if order == "SW":
            self.memory[str(mem_addr)][0] = self.register_list[reg_idx]
        elif order == "LW":
            self.register_list[reg_idx] = self.memory[str(mem_addr)][0]

    def execute_shift(self, rt_value, imm, order):
        if order == "SLL":
            return rt_value << imm
        elif order == "SRL":
            return rt_value >> imm
        elif order == "SRA":
            return (rt_value & 0xffffffff) >> imm
        else:
            return None

    def execute_command(self, command, program_counter):
        order = command[0]
        if order == "ADD" or order == "SUB" or order == "MUL" or \
                order == "AND" or order == "NOR" or order == "SLT":
            rs_reg_idx = int(command[1].lstrip("R"))
            rt_reg_idx = int(command[2].lstrip("R"))
            if command[3].startswith('R'):
                rd_reg_idx = int(command[3].lstrip("R"))
                rt_value = self.register_list[rt_reg_idx]
                rd_value = self.register_list[rd_reg_idx]
                self.register_list[rs_reg_idx] = self.execute_op(rt_value, rd_value, order)
            elif command[3].startswith('#'):
                imm = int(command[3].lstrip("#"))
                rt_value = self.register_list[rt_reg_idx]
                self.register_list[rs_reg_idx] = self.execute_op(rt_value, imm, order)
        elif order == "SW" or order == "LW":
            reg_idx = int(command[1].lstrip('R'))
            mem_addr = re.split("[()]", command[2])
            offset = int(mem_addr[0])
            base_idx = int(mem_addr[1].lstrip('R'))
            base = self.register_list[base_idx]
            self.execute_sl(mem_addr=base + offset, reg_idx=reg_idx, order=order)
        elif order == "SLL" or order == "SRL" or order == "SRA":
            rd_reg_idx = int(command[1].lstrip("R"))
            rt_reg_idx = int(command[2].lstrip("R"))
            imm = int(command[3].lstrip("#"))
            self.register_list[rd_reg_idx] = self.execute_shift(rt_value=self.register_list[rt_reg_idx], imm=imm, order=order)
        elif order == "BREAK":
            return None
        elif order == "NOP":
            pass
        elif order == "J":
            return int(command[1].lstrip("#"))
        elif order == "JR":
            reg_idx = int(command[1].lstrip("R"))
            return self.register_list[reg_idx]
        elif order == "BEQ":
            rs_reg_idx = int(command[1].lstrip("R"))
            rt_reg_idx = int(command[2].lstrip("R"))
            offset = int(command[3].lstrip("#"))
            rs_value = self.register_list[rs_reg_idx]
            rt_value = self.register_list[rt_reg_idx]
            if rs_value == rt_value:
                program_counter = program_counter + offset
        elif order == "BLTZ":
            rs_reg_idx = int(command[1].lstrip("R"))
            offset = int(command[2].lstrip("#"))
            rs_value = self.register_list[rs_reg_idx]
            if rs_value < 0:
                program_counter = program_counter + offset
        elif order == "BGTZ":
            rs_reg_idx = int(command[1].lstrip("R"))
            offset = int(command[2].lstrip("#"))
            rs_value = self.register_list[rs_reg_idx]
            if rs_value > 0:
                program_counter = program_counter + offset

        return program_counter + 4

    def execution_simulate(self):
        if os.path.exists(self.simulation_file_path):
            os.remove(self.simulation_file_path)
        PC = self.start_address
        Cycle = 1
        while PC:
            command = self.memory[str(PC)]
            new_program_counter = self.execute_command(command, PC)
            self.print_simulation(command, Cycle, PC)
            PC = new_program_counter
            Cycle += 1
