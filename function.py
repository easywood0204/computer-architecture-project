import copy
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
                    w = [command[0:1], " ",
                         command[1:5 + 1], " ",
                         command[6: 10 + 1], " ",
                         command[11: 15 + 1], " ",
                         command[16: 20 + 1], " ",
                         command[21: 25 + 1], " ",
                         command[26:31 + 1], "\t",
                         str(now), "\t"]
                else:
                    w = [command, "\t",
                         str(now), "\t"]
                for i in range(len(self.memory[str(now)])):
                    w.append(str(self.memory[str(now)][i]))
                    if i == 0 and i != len(self.memory[str(now)]) - 1:
                        w.append("\t")
                    elif i != len(self.memory[str(now)]) - 1:
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
            counter = (counter + 1) % 8
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

    def execute_command(self, command, program_counter=0):
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
            self.register_list[rd_reg_idx] = self.execute_shift(rt_value=self.register_list[rt_reg_idx], imm=imm,
                                                                order=order)
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

    def outprint(self, command, parentheses=True):
        if command is None:
            return ''
        if parentheses is False:
            if len(command) == 1:
                p = '{}'.format(command[0])
            elif len(command) == 2:
                p = '{}\t{}'.format(command[0], command[1])
            elif len(command) == 3:
                p = '{}\t{}, {}'.format(command[0], command[1], command[2])
            else:
                print(command)
                p = '{}\t{}, {}, {}'.format(command[0], command[1], command[2], command[3])
            return p

        if len(command) == 1:
            p = '{}'.format(command[0])
        elif len(command) == 2:
            p = '{}\t{}'.format(command[0], command[1])
        elif len(command) == 3:
            p = '[{}\t{}, {}]'.format(command[0], command[1], command[2])
        else:
            p = '[{}\t{}, {}, {}]'.format(command[0], command[1], command[2], command[3])
        return p

    def print(self, out, Cycle):
        result_description = '--------------------\n'
        result_description += 'Cycle:{}\n\nIF Unit:\n'.format(Cycle)
        result_description += '\tWaiting Instruction: {}\n'.format(self.outprint(out['Waiting_Instruction'], False))
        result_description += '\tExecuted_Instruction: {}\n'.format(self.outprint(out['Executed_Instruction'], False))
        result_description += 'Pre-Issue Buffer:\n'
        result_description += '\tEntry 0:{}\n'.format(self.outprint(out['PreIssue_Buffer'][0]))
        result_description += '\tEntry 1:{}\n'.format(self.outprint(out['PreIssue_Buffer'][1]))
        result_description += '\tEntry 2:{}\n'.format(self.outprint(out['PreIssue_Buffer'][2]))
        result_description += '\tEntry 3:{}\n'.format(self.outprint(out['PreIssue_Buffer'][3]))
        result_description += 'Pre-ALU Queue:\n'
        result_description += '\tEntry 0:{}\n'.format(self.outprint(out['PreALU_Queue'][0]))
        result_description += '\tEntry 1:{}\n'.format(self.outprint(out['PreALU_Queue'][1]))
        result_description += 'Post-ALU Buffer:{}\n'.format(self.outprint(out['PostALU_Buffer']))
        result_description += 'Pre-ALUB Queue:\n'
        result_description += '\tEntry 0:{}\n'.format(self.outprint(out['PreALUB_Queue'][0]))
        result_description += '\tEntry 1:{}\n'.format(self.outprint(out['PreALUB_Queue'][1]))
        result_description += 'Post-ALUB Buffer:{}\n'.format(self.outprint(out['PostALUB_Buffer']))
        result_description += 'Pre-MEM Queue:\n'
        result_description += '\tEntry 0:{}\n'.format(self.outprint(out['PreMEM_Queue'][0]))
        result_description += '\tEntry 1:{}\n'.format(self.outprint(out['PreMEM_Queue'][1]))
        result_description += 'Post-MEM Buffer:{}\n\n'.format(self.outprint(out['PostMEM_Buffer']))
        result_description += 'Register\n'
        result_description += 'R00:\t{0}\n'.format('\t'.join(str(reg_value) for reg_value in self.register_list[0:8]))
        result_description += 'R08:\t{0}\n'.format('\t'.join(str(reg_value) for reg_value in self.register_list[8:16]))
        result_description += 'R16:\t{0}\n'.format('\t'.join(str(reg_value) for reg_value in self.register_list[16:24]))
        result_description += 'R24:\t{0}\n'.format('\t'.join(str(reg_value) for reg_value in self.register_list[24:32]))
        result_description += "\nData"
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
            counter = (counter + 1) % 8
        result_description += '\n'
        if not os.path.exists(os.path.dirname(self.simulation_file_path)):
            os.mkdir(os.path.dirname(self.simulation_file_path))
        with open(self.simulation_file_path, 'a') as f:
            f.write(result_description)

    def pipelined_simulate(self):
        if os.path.exists(self.simulation_file_path):
            os.remove(self.simulation_file_path)
        output_list = {'Waiting_Instruction': None,
                       'Executed_Instruction': None,
                       'PreIssue_Buffer': [None, None, None, None],
                       'PreALU_Queue': [None, None],
                       'PostALU_Buffer': None,
                       'PreALUB_Queue': [None, None],
                       'PostALUB_Buffer': None,
                       'PreMEM_Queue': [None, None],
                       'PostMEM_Buffer': None}
        ALUB_epoch = [-1, -1]
        function_state = []
        register_state = [None for _ in range(32)]
        PC = self.start_address
        Cycle = 1
        self.end = False
        while not self.end:
            new_output_list = copy.deepcopy(output_list)
            new_function_state = copy.deepcopy(function_state)
            new_register_state = copy.deepcopy(register_state)
            # IF
            if output_list['Executed_Instruction'] is not None:
                command = output_list['Executed_Instruction']
                PC = self.execute_command(command, PC)
                new_output_list['Executed_Instruction'] = None

            if output_list['Waiting_Instruction'] is None:
                empty_num = 0
                for i in range(4):
                    if new_output_list['PreIssue_Buffer'][i] is None:
                        empty_num += 1
                for _ in range(min(2, empty_num)):
                    command = self.memory[str(PC)]
                    if command[0] == 'J' or command[0] == 'JR' or command[0] == 'BEQ' or command[0] == 'BLTZ' or command[0] == 'BGTZ':
                        need = []
                        for p in range(1, len(command)):
                            if command[p][0] == 'R':
                                need.append(int(command[1].lstrip("R")))
                            elif len(command[p].split('(')) > 1:
                                mem_addr = re.split("[()]", command[p])
                                need.append(int(mem_addr[1].lstrip('R')))
                        f = True
                        for k in range(len(need)):
                            if register_state[need[k]] is not None:
                                f = False
                        if f is True:
                            new_output_list['Executed_Instruction'] = command
                        else:
                            new_output_list['Waiting_Instruction'] = command
                        break
                    elif command[0] == 'BREAK':
                        new_output_list['Executed_Instruction'] = command
                        self.end = True
                        break
                    for i in range(4):
                        if new_output_list['PreIssue_Buffer'][i] is None:
                            PC += 4
                            new_output_list['PreIssue_Buffer'][i] = command
                            order = command[0]
                            if order == 'SW' or order == 'LW':
                                D = int(command[1].lstrip("R"))
                                state = {'finish': False, 'Qi': None, 'Ri': True, 'OP': command, 'Fi': command[1], 'Fj': command[2], 'Fk': None,
                                         'Qj': None, 'Qk': None, 'Rj': True, 'Rk': True}
                                mem_addr = re.split("[()]", command[2])
                                if new_register_state[D] is not None:
                                    state['Qi'] = new_register_state[D]
                                    state['Ri'] = False
                                elif order == 'LW':
                                    new_register_state[D] = command

                                state['Qj'] = new_register_state[int(mem_addr[1].lstrip('R'))]
                                if state['Qj'] is not None:
                                    state['Rj'] = False

                                new_function_state.append(copy.deepcopy(state))
                            elif order == 'SLL' or order == 'SRL' or order == 'SRA' or order == 'MUL':
                                D = int(command[1].lstrip("R"))
                                state = {'finish': False, 'Qi': None, 'Ri': True, 'OP': command, 'Fi': command[1], 'Fj': command[2],
                                         'Fk': command[3], 'Qj': None, 'Qk': None, 'Rj': True, 'Rk': True}
                                if command[2][0] == 'R':
                                    state['Qj'] = new_register_state[int(command[2].lstrip("R"))]
                                    if state['Qj'] is not None:
                                        state['Rj'] = False
                                if command[3][0] == 'R':
                                    state['Qk'] = new_register_state[int(command[3].lstrip("R"))]
                                    if state['Qk'] is not None:
                                        state['Rk'] = False
                                if new_register_state[D] is not None:
                                    state['Qi'] = new_register_state[D]
                                    state['Ri'] = False
                                else:
                                    new_register_state[D] = command
                                new_function_state.append(copy.deepcopy(state))
                            else:
                                D = int(command[1].lstrip("R"))

                                state = {'finish': False, 'Qi': None, 'Ri': True, 'OP': command, 'Fi': command[1], 'Fj': command[2], 'Fk': command[3],
                                         'Qj': None, 'Qk': None, 'Rj': True, 'Rk': True}
                                if command[2][0] == 'R':
                                    state['Qj'] = new_register_state[int(command[2].lstrip("R"))]
                                    if state['Qj'] is not None:
                                        state['Rj'] = False
                                if command[3][0] == 'R':
                                    state['Qk'] = new_register_state[int(command[3].lstrip("R"))]
                                    if state['Qk'] is not None:
                                        state['Rk'] = False
                                if new_register_state[D] is not None:
                                    state['Qi'] = new_register_state[D]
                                    state['Ri'] = False
                                else:
                                    new_register_state[D] = command
                                new_function_state.append(copy.deepcopy(state))
                            break
            else:
                need = []
                command = output_list['Waiting_Instruction']
                for p in range(1, len(command)):
                    if command[p][0] == 'R':
                        need.append(int(command[1].lstrip("R")))
                    elif len(command[p].split('(')) > 1:
                        mem_addr = re.split("[()]", command[p])
                        need.append(int(mem_addr[1].lstrip('R')))
                f = True
                for k in range(len(need)):
                    if register_state[need[k]] is not None:
                        f = False
                if f is True:
                    new_output_list['Executed_Instruction'] = copy.deepcopy(new_output_list['Waiting_Instruction'])
                    new_output_list['Waiting_Instruction'] = None
            # Issue
            for i in range(4):
                if output_list['PreIssue_Buffer'][i] is not None:
                    command = output_list['PreIssue_Buffer'][i]
                    for k in range(len(function_state)):
                        if new_function_state[k]['finish'] is True:
                            continue
                        if function_state[k]['OP'] == command:
                            if function_state[k]['Rj'] is True and function_state[k]['Rk'] is True and function_state[k]['Ri'] is True:
                                order = command[0]
                                if order == 'SW' or order == 'LW':
                                    if new_output_list['PreMEM_Queue'][0] is None:
                                        location = 0
                                    elif new_output_list['PreMEM_Queue'][1] is None:
                                        location = 1
                                    else:
                                        break
                                    new_output_list['PreMEM_Queue'][location] = command
                                    new_output_list['PreIssue_Buffer'][i] = None
                                elif order == 'SLL' or order == 'SRL' or order == 'SRA' or order == 'MUL':
                                    if new_output_list['PreALUB_Queue'][0] is None:
                                        location = 0
                                    elif new_output_list['PreALUB_Queue'][1] is None:
                                        location = 1
                                    else:
                                        break
                                    new_output_list['PreALUB_Queue'][location] = command
                                    ALUB_epoch[location] = 1
                                    new_output_list['PreIssue_Buffer'][i] = None
                                else:
                                    if new_output_list['PreALU_Queue'][0] is None:
                                        location = 0
                                    elif new_output_list['PreALU_Queue'][1] is None:
                                        location = 1
                                    else:
                                        break
                                    new_output_list['PreALU_Queue'][location] = command
                                    new_output_list['PreIssue_Buffer'][i] = None
            for i in range(4):
                if new_output_list['PreIssue_Buffer'][i] is None:
                    for j in range(i + 1, 4):
                        if new_output_list['PreIssue_Buffer'][j] is not None:
                            new_output_list['PreIssue_Buffer'][i] = new_output_list['PreIssue_Buffer'][j]
                            new_output_list['PreIssue_Buffer'][j] = None
                            break
            # MEM
            flag_MEM = False
            flag_SW = False
            if output_list['PreMEM_Queue'][0] is not None:
                command = output_list['PreMEM_Queue'][0]
                if command[0] == 'SW':
                    for k in range(len(new_function_state)):
                        if new_function_state[k]['OP'] == command and new_function_state[k]['finish'] is False:
                            new_function_state[k]['finish'] = True
                            break
                    self.execute_command(command)

                    flag_SW = True
                else:
                    new_output_list['PostMEM_Buffer'] = output_list['PreMEM_Queue'][0]
                    flag_MEM = True
                new_output_list['PreMEM_Queue'][0] = new_output_list['PreMEM_Queue'][1]
                new_output_list['PreMEM_Queue'][1] = None
            # ALUB
            flag_ALUB = False
            if output_list['PreALUB_Queue'][0] is not None:
                if ALUB_epoch[0] == 0:
                    new_output_list['PostALUB_Buffer'] = output_list['PreALUB_Queue'][0]
                    flag_ALUB = True
                    new_output_list['PreALUB_Queue'][0] = new_output_list['PreALUB_Queue'][1]
                    new_output_list['PreALUB_Queue'][1] = None
                    ALUB_epoch[0] = ALUB_epoch[1]
                else:
                    ALUB_epoch[0] -= 1

            # ALU
            flag_ALU = False
            if output_list['PreALU_Queue'][0] is not None:
                new_output_list['PostALU_Buffer'] = output_list['PreALU_Queue'][0]
                flag_ALU = True
                new_output_list['PreALU_Queue'][0] = new_output_list['PreALU_Queue'][1]
                new_output_list['PreALU_Queue'][1] = None

            for i in range(3):
                if i == 0:
                    command = output_list['PostALU_Buffer']
                elif i == 1:
                    command = output_list['PostMEM_Buffer']
                else:
                    command = output_list['PostALUB_Buffer']
                if command is not None:
                    D = int(command[1].lstrip("R"))
                    new_register_state[D] = None
                    for k in range(len(new_function_state)):
                        if new_function_state[k]['OP'] == command and new_function_state[k]['finish'] is False:
                            new_function_state[k]['finish'] = True
                            break
                    for k in range(len(new_function_state)):
                        if new_function_state[k]['finish'] is True:
                            continue
                        if new_function_state[k]['Qj'] == command:
                            new_function_state[k]['Qj'] = None
                            new_function_state[k]['Rj'] = True
                        if new_function_state[k]['Qk'] == command:
                            new_function_state[k]['Qk'] = None
                            new_function_state[k]['Rk'] = True
                    for k in range(len(new_function_state)):
                        if new_function_state[k]['finish'] is True:
                            continue
                        if new_function_state[k]['Qi'] == command:
                            new_function_state[k]['Qi'] = None
                            new_function_state[k]['Ri'] = True
                            if function_state[k]['OP'][0] == 'SW':
                                continue
                            new_register_state[D] = function_state[k]['OP']
                            for p in range(k + 1, len(new_function_state)):
                                if function_state[p]['Qi'] == command:
                                    new_function_state[p]['Qi'] = new_register_state[D]
                            break
                    if not flag_ALU and i == 0:
                        new_output_list['PostALU_Buffer'] = None
                    if not flag_MEM and i == 1:
                        new_output_list['PostMEM_Buffer'] = None
                    if not flag_ALUB and i == 2:
                        new_output_list['PostALUB_Buffer'] = None
                    if flag_SW is False or i != 1:
                        self.execute_command(command)
            # update
            output_list = new_output_list
            register_state = new_register_state
            function_state = new_function_state
            # print
            self.print(output_list, Cycle)
            Cycle += 1
