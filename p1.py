import sys

"""
GROUP PROJECT

Matthew Salemi
Steven Li
Escher Campie
Joseph Om

12/12/18
Computer Organization
Fall 2018

The purpose of this program is to simulate and show a pipeline for
a given set of MIPS commands. It shows each command followed by which
stage it is in for the pipeline. The simulation offers the ability
to run the pipeline with or without fowarding and branch prediction.
If one of these causes a hazard, the pipeline will insert a nop
command and bubbles until the needed information is availible.
"""


"""
Compares two different registers/values under a branching
command and returns 1 if the branch is taken and 0 if it
is not taken.

command: The branch command being used (beq/bne)
print_l_d: The dependencies of each printed line
regs: A dictionary of values corresponding to each register

returns: 1 if branch is taken and 0 if it is not
"""
def compare(command, print_l_d, regs):

    first, second, x = print_l_d

    if first == "$zero":
        first = 0

    elif first[0] == '$':
        first = regs[first]

    else: 
        first = int(first)

    if second == "$zero":
        second = 0

    elif second[0] == '$':
        second = regs[second]

    else:
        second = int(second)


    if command == "beq":
        if second == first:
            return 1
        return 0

    else:
        if second != first:
            return 1
        return 0


"""
Takes in a command and two read registers or a read register
and an immediate value and calculates the value that should
be stored in the save register of the command

oper: The type of operation being run on the inputs
deps: The dependencies for a given line (read registers)
regs: A dictionary of values corresponding to each register

returns: The value to be stored in the save register
"""
def processWB(oper, deps, regs):

    """ 
    Ex)  
        oper ->       "add"
                      "addi"
                      "or"
                      "ori" 
                      "and"
                      "andi"
                      "slt"
                      "slti"
                      "beq"
                      "bne"

        deps ->        ('$t0', '$s0', 5)

        reg ->         Dictionary of all current registers 
                       ["$s0":0,: "$s1":0, "$s2":0 ..... "$t9": 0]
    """

    arg1 = deps[1]
    arg2 = deps[2]

    if arg1 == "$zero":
        arg1 = '0'
    if arg2 == "$zero":
        arg2 = '0'

    if arg1[0] == '$':
        arg1 = regs[arg1]
    else:
        arg1 = int(arg1)

    if arg2[0] == '$':
        arg2 = regs[arg2]
    else:
        arg2 = int(arg2)

    # AND/ANDi Operation
    if oper == "and" or oper == "andi":
        return arg1 & arg2

    # OR/ORi Operation
    elif oper == "or" or oper == "ori":
        return arg1 | arg2 

    # ADD/ADDi Operation 
    elif oper == "add" or oper == "addi":
        return arg1 + arg2 

    # SLT/SLTi Operation
    elif oper == "slt" or oper == "slti":
        if arg1 < arg2:
            return 1
        else:
            return 0

    return "ERROR"


"""
Prints the "board" which consists of the cycle labels, instructions
being executed, the current pipeline and the values of all save
and temporary registers.

lines: A list of all of the instructions that have been executed
regs: A dictionary of values corresponding to each register
pipe: A two dimensional array of the current and past stages for each line
stages: A list of the different stages an instruction can be in

returns: void
"""
def print_board(lines, regs, pipe, stages):
    print('-' * 82)
    print("CPU Cycles ===>     1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16")

    #Print current stages of the pipeline

    for i in range(len(pipe)):
        print("{0: <20}".format(lines[i]), end='')
        for j in range(15):
            print("{0: <4}".format(stages[pipe[i][j]]), end='')
        print(stages[pipe[i][15]])
    print()

    #Print the value of all registers

    for i in range(8):
        if (i + 1) % 4 != 0:
            print("{0: <20}".format("$s" + str(i) + " = " + str(regs["$s" + str(i)])), end='')
        else:
            print("$s" + str(i) + " = " + str(regs["$s" + str(i)]))

    for i in range(9):
        if (i + 1) % 4 != 0:
            print("{0: <20}".format("$t" + str(i) + " = " + str(regs["$t" + str(i)])), end='')
        else:
            print("$t" + str(i) + " = " + str(regs["$t" + str(i)]))
    print("$t" + str(9) + " = " + str(regs["$t" + str(9)]))

    return 0


"""
Finds the dependencies for each instruction

lines: A list of all of the instructions to be executed

returns: A list of tuples with the depencies of each line
"""
def dependencies(lines):
    dependencies = []

    for x in lines:
        x = x.strip()

        if x[-1] == ":":    #if the line is invalid, it will add a -1
                            #(in a tuple) to the dependencies array
            dependencies.append((-1))

        else:
            y = x.split(" ")
            registers = y[1].split(",")
            #creating the tuple of the result registers, and the 2 registers/values it depends on 
            t = (registers[0], registers[1], registers[2]) 
            dependencies.append(t)

    return dependencies

"""
Prints the "board" which consists of the cycle labels, instructions
being executed, the current pipeline and the values of all save
and temporary registers.

lines: A list of all of the instructions that have been executed
print_l_d: The dependencies of each printed line
print_lines: A list of the instructions that have been printed
regs: A dictionary of values corresponding to each register
pipe: A two dimensional array of the current and past stages for each line
cycle_num: The current cycle number that the simulation has reached
curr_line: The current line of input that the simulation is adding
deps: The dependencies for all lines in the input
print_l_d: The dependencies of each printed line
stalls: A list of which printed lines have buffers remaining
fowarding: Whether or not forwarding is used in the current simulation

returns: A tuple containing if the simulation is over and the line number just added
"""
def update_cycle(lines, print_l, print_lines, regs, pipe, cycle_num, curr_line, deps, 
                 print_l_d, stalls, forwarding):
    if curr_line < len(lines):
        print_lines.append(print_l)
        print_l_d.append(deps[curr_line])

    if cycle_num == 0:
        pipe[0][0] = 1
        stalls.append(0)
        return (False, curr_line)

    if len(print_lines) > len(pipe):
        pipe.append([0] * 16)
        stalls.append(0)

    i = 0
    
    while i < len(pipe):

        if pipe[i][cycle_num - 1] == 2 and forwarding == 'N':
            nops = 0

            if i > 0 and type(print_l_d[i - 1]) != int and (print_l_d[i-1][0] == \
                              print_l_d[i][1] or print_l_d[i-1][0] == print_l_d[i][2]):
                nops = 2
            elif i > 1 and type(print_l_d[i - 2]) != int and (print_l_d[i-2][0] == \
                                print_l_d[i][1] or print_l_d[i-2][0] == print_l_d[i][2]):
                nops = 1

            if nops > 0:
                #add first nop
                print_lines.insert(i, "nop")
                pipe.insert(i, pipe[i].copy())
                pipe[i][cycle_num] = 7
                print_l_d.insert(i, -2)
                stalls.insert(i, 0)
                i += 1

                for j in range(i, len(pipe)):
                    stalls[j] += 1

                if nops > 1:
                    print_lines.insert(i, "nop")
                    pipe.insert(i, pipe[i].copy())
                    pipe[i][cycle_num] = 7
                    print_l_d.insert(i, -2)
                    stalls.insert(i, 0)
                    i += 1

                    for j in range(i, len(pipe)):
                        stalls[j] += 1

        if pipe[i][cycle_num - 1] == 4:
            if print_lines[i].split(" ")[0] == "beq" or print_lines[i].split(" ")[0] == "bne":
                if compare(print_lines[i].split(" ")[0], print_l_d[i], regs):
                    l = i
                    k = i + 1
                    for j in range(k, len(pipe)):
                        pipe[j][cycle_num] = 8
                        i += 1
                    label = print_l_d[l][-1]

                    k = 0

                    for j in range(len(lines)):
                        if label + ':' == lines[j]:
                            k = j
                            break

                    print_lines.append(lines[k + 1])
                    print_l_d.append(deps[k + 1])
                    pipe.append([0] * 16)
                    stalls.append(0)

                    pipe[l][cycle_num] = 5
                    pipe[-1][cycle_num] = 1

                    return (False, k + 1)

            else:
                regs[print_l_d[i][0]] = processWB(print_lines[i].split(" ")[0],\
                                                  print_l_d[i], regs)

        if pipe[i][cycle_num - 1] < 6:

            if (stalls[i] > 0):
                pipe[i][cycle_num] = pipe[i][cycle_num - 1]
                stalls[i] -= 1
            else:
                pipe[i][cycle_num] = pipe[i][cycle_num - 1] + 1

            if print_l == lines[-1] and pipe[-1][cycle_num] == 5:
                return (True, 0)

        else:
            if pipe[i][cycle_num - 1] == 8:
                nonzero = 0
                for j in range(0, 16):
                    if pipe[i][j] != 0:
                        nonzero += 1
                if nonzero == 5:
                    pipe[i][cycle_num] = 6
                else:
                    pipe[i][cycle_num] = 8
            elif pipe[i][cycle_num - 1] == 7:
                if pipe[i - 1][cycle_num - 1] == 6:
                    pipe[i][cycle_num] = 6
                    if pipe[i + 1][cycle_num - 1] == 7:
                        pipe[i + 1][cycle_num] = 6
                        i += 1
                else:
                    pipe[i][cycle_num] = pipe[i][cycle_num - 1]
            else:
                pipe[i][cycle_num] = pipe[i][cycle_num - 1]
        i += 1

    return (False, curr_line)


"""
Runs through all of the inputed instructions up to 16 cycles in the
simulation and prints the "board" after each cycle is updated.

lines: A list of all of the instructions that have been executed
regs: A dictionary of values corresponding to each register
pipe: A two dimensional array of the current and past stages for each line
fowardining: Whether or not forwarding is used in the current simulation
deps: The dependencies for all lines in the input

returns: void
"""
def execute(lines, regs, pipe, forwarding, deps):
    # Stages for the pipeline
    stages = [".", "IF", "ID", "EX", "MEM", "WB", ".", "*", "*"]

    cycle_num = 0

    curr_line = 0
    print_lines = []
    print_l_d = []

    stalls = []

    print("START OF SIMULATION (", end = '')

    if forwarding == "F":
        print("forwarding)")

    elif forwarding == "N":
        print("no forwarding)")

    while (cycle_num != 16):

        if curr_line < len(lines):

            while (lines[curr_line][-1] == ':'):
                curr_line += 1

            print_l = lines[curr_line]

        finished = False

        finished, curr_line = update_cycle(lines, print_l, print_lines, regs, pipe, \
                                           cycle_num, curr_line, deps, print_l_d,\
                                           stalls, forwarding)
        print_board(print_lines, regs, pipe, stages)

        if finished == True:
            break

        if curr_line < len(lines):
            curr_line += 1

        cycle_num += 1
    print('-' * 82)
    print("END OF SIMULATION")


def main():

    #Error checking for read in
    if len(sys.argv) < 3:
        print("Invalid number of arguments!")
        return 1

    forwarding = sys.argv[1]

    # Make sure there is validing forwarding condition
    if forwarding != 'N' and forwarding != 'F':
        print("Invalid forwarding mode!")
        return 1

    in_file = sys.argv[2]

    # Open file and read in lines
    in_file = open(in_file, 'r')
    lines = in_file.read().splitlines()
    deps = dependencies(lines)

    # Creating the dictionary for all of the registers
    regs = dict()
    reg_type = "$s"
    num_reg = 0
    for i in range(18):
    	if i == 8:
    		reg_type = "$t"
    		num_reg = 0
    	regs[reg_type + str(num_reg)] = 0
    	num_reg += 1

    # Creating a pipe structure of 16 zeroes
    pipe = []
    pipe.append([0] * 16)

    execute(lines, regs, pipe, forwarding, deps)

    in_file.close()

    return 0;


if __name__ == '__main__':
    main()