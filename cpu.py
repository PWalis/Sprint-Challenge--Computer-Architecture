"""CPU functionality."""

import sys

ldi = 0b10000010
prn = 0b01000111
hlt = 0b00000001
mul = 0b10100010
add = 0b10100000
push = 0b01000101
pop = 0b01000110
call = 0b01010000
ret = 0b00010001
comp = 0b10100111
jmp = 0b01010100
jeq = 0b01010101
jne = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.branchtable = {ldi:self.ldi, prn:self.prn, hlt:self.hlt, mul:self.mul, push:self.push,
                            pop:self.pop, call:self.call, ret:self.ret, add:self.add, comp:self.comp,
                            jmp:self.jmp, jeq:self.jeq, jne:self.jne}
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        # Stack pointer at r7
        self.reg[7] = 0xF3
        self.sp = self.reg[7]

        self.fl = 0b00000000

    def load(self, progname):
        """Load a program into memory."""

        address = 0
        # For now, we've just hardcoded a program:
        with open(progname) as f:
            for line in f:
                line = line.strip()

                line = line.split('#')[0]
                if line == '':
                    continue

                val = int(line, 2)
                self.ram[address] = val
                address += 1

        # print(self.ram[:10])
        # print(self.reg)
    

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "cmp":
            mdr_0 = self.reg[reg_a]
            mdr_1 = self.reg[reg_b]
            if mdr_0 < mdr_1:
                self.fl = 0b00000100
            elif mdr_0 > mdr_1:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001 
        else:
            raise Exception("Unsupported ALU operation")\

    def read_ram(self, mar):
        ''' Returns item at address in ram '''
        mdr = self.ram[mar]
        return mdr

    def write_ram(self, mar, mdr):
        ''' Writes value in ram at address '''
        if self.ram[mar] != None:
            self.reg[mar] = mdr
        else:
            return f'ERROR: address[{mar}] is not a valid address'

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ldi(self):
        # print('LDI')
        self.pc += 1
        mar = self.read_ram(self.pc)
        # print(mar)
        self.pc += 1
        mdr = self.read_ram(self.pc)
        # print(mdr)
        self.write_ram(mar, mdr)
        self.pc += 1
        
    def prn(self):
        self.pc += 1
        mdr = self.read_ram(self.pc)
        print(f'{self.reg[mdr]}')
        self.pc += 1

    def hlt(self):
        # print(f'Ram: {self.ram[:30]}\nReg: {self.reg}\nStack: {self.ram[241:244]}')
        sys.exit()

    def mul(self):
        self.pc += 1
        mar_0 = self.read_ram(self.pc)
        # print(mar)
        self.pc += 1
        mar_1 = self.read_ram(self.pc)
        # print(mdr)
        self.alu('MUL', mar_0, mar_1)
        self.pc += 1

    def add(self):
        self.pc += 1
        mar_0 = self.read_ram(self.pc)
        # print(mar)
        self.pc += 1
        mar_1 = self.read_ram(self.pc)
        # print(mdr)
        self.alu('ADD', mar_0, mar_1)
        self.pc += 1

    def push(self):
        self.pc += 1
        mar = self.ram[self.pc]
        self.sp -= 1
        self.ram[self.sp] = self.reg[mar]
        self.pc += 1
        
    def pop(self):
        self.pc += 1
        mar = self.ram[self.pc]
        self.reg[mar] = self.ram[self.sp]
        self.sp += 1
        self.pc += 1

    def call(self):
        # print(f'stack pointer{self.sp}')
        self.sp -= 1
        # print(f'stack pointer after{self.sp}')
        self.ram[self.sp] = self.pc + 2
        # print(f'Call: pc{self.pc}')
        self.pc = self.reg[self.ram[self.pc + 1]]
        
    def ret(self):
        # print(f'stack pointer ret {self.sp}')
        self.pc = self.ram[self.sp]
        self.sp += 1

    def comp(self):
        # print(f'Ram: {self.ram[:40]}\nReg: {self.reg}')
        self.fl = 0b00000000
        mar_0 = self.read_ram(self.pc + 1)
        mar_1 = self.read_ram(self.pc + 2)
        self.alu('cmp', mar_0, mar_1)
        self.pc += 3

    def jmp(self):
        mar = self.read_ram(self.pc + 1)
        mdr = self.reg[mar]
        self.pc = mdr

    def jeq(self):
        if self.fl%2 != 0:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        if self.fl%2 == 0:
            self.jmp()
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        # print(f'Ram: {self.ram[:30]}\nReg: {self.reg}\nStack: {self.ram[230:241]}')
        while True:
            ir = self.read_ram(self.pc)
            # print(f'IR: {ir}  PC: {self.pc}')
            # print(f'Ram: {self.ram[:40]}\nReg: {self.reg}\n')
            
            if ir in self.branchtable:
                # print(ir)
                self.branchtable[ir]()

            else:
                print(f'Ram: {self.ram[:30]}\nReg: {self.reg}\nStack: {self.ram[241:244]}')
                print(f'Instruction not found [{ir}]\nPC: [{self.pc}]')
                sys.exit()
        



