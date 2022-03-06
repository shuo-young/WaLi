from struct import *
import logging
from .graph import *
from .tools import *
import collections

CALLER_SYSMBOL = 5
class StackItem:
    def __init__(self, _value = 0):
         self.value = _value
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, StackItem):
            return self.value == other.value
        else:
            return self.value == other
    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        return not self.__eq__(other)
    def __str__(self):
        return str(self.value)
    def __int__(self):
        return self.value

class Stack(collections.MutableSequence):

    def __init__(self, *args):
        self.list = list()
        self.extend(list(args))

    def __len__(self): return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i): del self.list[i]

    def __setitem__(self, i, v):
        print("setitem")
        self.list[i].value = v

    def insert(self, i, v):
        if isinstance(v, StackItem):
            self.list.insert(i, v)
        else:
            item = StackItem()
            item.value = v
            self.list.insert(i, item)

    def __str__(self):
        strStack = list(i.value for i in self.list)
        return str(strStack)

class WasmVM(object):

    def __init__(self, cfg, func_map):
        self.mem_tb = {}
        self.globals = {}
        self.size_stack = 0
        self.stack = Stack()
        self.cfg = cfg
        self.func_map = func_map

        self.caller_memory = []
        self.flag = 0
        self.judge = False
        self.focus = False

        # load caller_memory
        self.keyFactor1 = False
        self.offset1 = 0
        self.leave_focus = False
        self.leave_iter = False
        # tee and eqz after call focusfunc[1](get_storage)
        self.keyFactor2 = False
        self.offset2 = 0
        self.keyFactor3 = False
        self.offset3 = 0

        self.indirect_targets = []

        self.globals['$G0'] = 0

        self.memAddr = 0

    def trace_func(self, path_blocks, args = list(), focus_funcs=list()):

        locals = {}  # keep local variables
        for i in range(0, len(args)):
            locals["$L" + str(i)] = args[i]

        self.trace_blocks(path_blocks, locals, focus_funcs)


    def trace_blocks(self, blocks, locals = dict(), focus_funcs = list(), recursion = True):
        logging.debug(list(b.name for b in blocks))
        logging.debug(self.mem_tb)

        path_instrs = []
        for b in blocks:
            path_instrs.extend(b.instructions)

        for i in path_instrs:
            logging.debug(str(self.size_stack)  + str(self.stack) + str(i) )
            # record the size_stack
            if i.name != "call":
                self.size_stack -= i.pops
                self.size_stack += i.pushes

            if i.name in ["unreachable", "nop", "block", "loop", "else", "end", "br"]:
                pass
            elif i.name == "if":
                self.stack.pop()
            elif i.name == "br_if":
                self.stack.pop()
            elif i.name == "br_table":
                self.stack.pop()
            elif i.name == "return":
                self.stack.pop()

            elif i.name == "drop":
                self.stack.pop()
            elif i.name == "select":
                c = self.stack.pop()
                val2 = self.stack.pop()
                val1 = self.stack.pop()
                if int(c) != 0:
                    self.stack.append(val1)
                else:
                    self.stack.append(val2)
            elif i.name == "get_local":
                if "$L" + str(i.operand_interpretation.split(" ")[-1]) in locals:
                    obj = locals["$L" + str(i.operand_interpretation.split(" ")[-1])]
                    item = StackItem()
                    if isinstance(obj, StackItem):
                        item = obj
                    else:
                        item.value = int(obj)
                elif i.operand_interpretation == "get_local 2":
                    item = StackItem()
                    item.value = 0
                    item.type = "TO"
                else:
                    # print("UNKNOWN LOCAL")
                    item = StackItem()
                    item.value = 0
                    item.type = "UNKNOWN"
                # item.type = "LOCAL"
                item.allies = "$L" + str(i.operand_interpretation.split(" ")[-1])

                # firt L0 set as 5 after getCaller
                if item.allies == "$L0":
                    if self.flag == 1:
                        item.value = CALLER_SYSMBOL
                        self.flag = 0

                self.stack.append(item)
            elif i.name == "set_local":
                locals["$L" + str(i.operand_interpretation.split(" ")[-1])] = self.stack.pop()
            elif i.name == "tee_local":
                if(self.keyFactor1 == True and self.leave_focus == True and i.offset == self.offset1+2):
                    print("################keyFactor2 judge################")
                    print("tee_local offset: "+str(i.offset))
                    self.keyFactor2 = True
                    self.offset2 = i.offset
                    print("keyFactor2 True!")
                locals["$L" + str(i.operand_interpretation.split(" ")[-1])] = self.stack[-1]

            elif i.name == "get_global":
                self.stack.append(self.globals["$G" + str(i.operand_interpretation.split(" ")[-1])])
            elif i.name == "set_global":
                self.globals["$G"+ str(i.operand_interpretation.split(" ")[-1])] = self.stack.pop()
            elif i.name == "i32.load":
                addr_operand = self.stack.pop()
                if (int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)) in self.mem_tb:
                    # if load 5(the value of getCaller), then push back to stack
                    # if focus is true, then find satisfaction of the condition of keyFactor1
                    if (int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)) in self.caller_memory:
                        print("################keyFactor1 judge################")
                        if(self.focus == True):
                            print("load getCaller memory value at", int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand))
                            self.keyFactor1 = True
                            self.leave_focus = True
                            self.leave_iter = True
                            print("keyFactor1 True!")
                        else:
                            print("keyFactor1 False!")
                            self.stack.append(CALLER_SYSMBOL)
                    else:
                        val = self.mem_tb[int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)]
                        val = unpack('i', val)[0]
                        self.stack.append(val)
                else:
                    self.stack.append(0)
            elif i.name == "i32.load8_u":
                addr_operand = self.stack.pop()
                if (int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)) in self.mem_tb:
                    val = self.mem_tb[int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)]
                    val = unpack('i', val)[0]
                    self.stack.append(val)
                else:
                    self.stack.append(0)
            elif i.name == "i64.load":

                addr_operand = self.stack.pop()
                ef_addr1 = int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)
                ef_addr2 = (4 + int(i.operand_interpretation.split(" ")[-1])) + int(addr_operand)

                item = StackItem()
                item.memAddr = ef_addr1
                if hasattr(addr_operand, "allies") and addr_operand.allies == "$L0" \
                        and i.operand_interpretation == "i64.load 3, 0":
                    item.type = "SELF"
                else:
                    item.type = "MEM_V"

                item.op = i.operand_interpretation
                if ef_addr1 in self.mem_tb:
                    val = self.mem_tb[ef_addr1]

                    if ef_addr2 in self.mem_tb:
                        val = val + self.mem_tb[ef_addr2]

                    else:
                        val = val + pack('i', 0)

                    val = unpack('q', val)[0]
                    item.value = val
                    self.stack.append(item)
                else:
                    item.value = 0
                    self.stack.append(item)
            elif i.name == "i32.store":
                val = self.stack.pop()
                addr_operand = self.stack.pop()
                # store the value of getCaller to memory
                if (val == CALLER_SYSMBOL):
                    self.caller_memory.append(int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand))
                    print("getCaller value store to memory: "+" ".join('%s' %id for id in self.caller_memory))
                val = pack('i', int(val))
                self.mem_tb[int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)] = val
            elif i.name == "i64.store":  # TODO: 64bit
                val = self.stack.pop()
                val = pack('q', int(val))
                addr_operand = self.stack.pop()
                self.mem_tb[int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand)] = val[:4]
                self.mem_tb[int(i.operand_interpretation.split(" ")[-1]) + int(addr_operand) + 4] = val[4:]

            elif i.name in ["i32.const", "i64.const"]:
                self.stack.append(int(i.operand_interpretation.split(" ")[-1]))
            elif i.name in ["i32.eqz", "i64.eqz"]:
                if(self.keyFactor2 == True and i.offset == self.offset2+2):
                    print("################keyFactor3 judge################")
                    print("i32.eqz offset: "+str(i.offset))
                    self.keyFactor3 = True
                    self.offset3 = i.offset
                    print("keyFactor3 True!")

                op = int(self.stack.pop())
                if op == "unknown":
                    self.stack.append(0)
                    continue

                if op in locals:
                    op = locals[op]

                if int(op) == 0:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            elif i.name in ["i32.eq", "i64.eq", "i32.ne", "i64.ne"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                self.stack.append(0)
            elif i.name in ["i32.lt_u", "i64.lt_u"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if int(op1) < int(op2):
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            elif i.name in ["i32.gt_u", "i64.gt_u", "i32.gt_s", "i64.gt_s"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if int(op1) > int(op2):
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            elif i.name in ["i32.le_s", "i64.le_s","i32.le_u", "i64.le_u"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if int(op1) < int(op2):
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            elif i.name in ["i32.mul", "i64.mul"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                self.stack.append(int(op1) * int(op2))
            elif i.name in ["i32.ge_u","i64.ge_u","i32.shl", "i64.shl","i32.shr_s","i64.shr_s"]:
                self.stack.pop()
            elif i.name in ["i32.add", "i64.add"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if int(op2) in locals:
                    op2 = locals[int(op2)]
                if int(op1) in locals:
                    op1 = locals[int(op1)]
                if op1 == "unknown" or op2 == "unknown":
                    self.stack.append(0)#TODO
                else:
                    self.stack.append(int(op1) + int(op2))


            elif i.name in ["i32.sub", "i64.sub"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                self.stack.append(int(op1) - int(op2))

            elif i.name in ["i32.and", "i64.and"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                if int(op2) in locals:
                    op2 = locals[int(op2)]
                if int(op1) in locals:
                    op1 = locals[int(op1)]
                self.stack.append(int(op1) & int(op2))
            elif i.name in ["i32.or", "i64.or"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                self.stack.append(int(op1) | int(op2))
            elif i.name in ["i32.xor", "i64.xor"]:
                op2 = self.stack.pop()
                op1 = self.stack.pop()
                self.stack.append(int(op1) ^ int(op2))


            elif i.name == "call":
                # function index
                f_idx = int(i.operand_interpretation.split(" ")[-1])

                # enter the key funciton part -> getStorage
                if (f_idx == focus_funcs[1]):
                    self.focus = True
                    self.offset1 = i.offset

                if self.func_map[f_idx][3] != "import":
                    # not FBEI function
                    pops_n = len(list(filter(None, self.func_map[f_idx][1].split(" "))))
                    pushs_n = len(list(filter(None, self.func_map[f_idx][2].split(" "))))

                    args_next = []

                    for n in range(0, pops_n):
                        args_next.append(self.stack.pop())
                        self.size_stack -= self.size_stack

                    if recursion:
                        f_next_name = self.func_map[f_idx][0]
                        if f_next_name == "$func20":
                            print("===================enter the " + f_next_name + "===================")
                        next_paths = get_func_paths(self.cfg, f_next_name)

                        for p in next_paths:
                            if self.leave_iter == False:
                                self.trace_func(p, args_next, focus_funcs)
                            elif self.leave_iter == True:
                                if (f_next_name == "$func" + str(focus_funcs[1])):
                                    print("===================leave the " + f_next_name + "===================")
                                break

                    else:
                        try:
                            indirect_target = unpack("i", self.mem_tb[int(args_next[0])])[0]
                            f_pts = self.cfg.analyzer.elements[0].get('elems')
                            start_idx = 1
                            for f in self.cfg.functions:
                                if f.name == self.func_map[f_pts[0]][0]:
                                    if len(f.instructions) == 2 and f.instructions[0].name == "unreachable" and f.instructions[1].name == "end":
                                        start_idx = 0
                                        break
                            if not f_pts[indirect_target - start_idx] in self.indirect_targets:
                                self.indirect_targets.append(f_pts[indirect_target - start_idx])
                        except:
                            print("try fail", f_idx)
                            pass

                    self.size_stack += pushs_n
                    for n in range(0, pushs_n):
                        self.stack.append(0)

                else:
                    if f_idx in focus_funcs:
                        print("call FBEI function index: " + str(f_idx))

                        # getCaller process
                        if f_idx == focus_funcs[0]:
                            self.flag = 1

                        logging.debug(self.stack)
                        logging.debug(self.mem_tb)
                    pops_n = len(list(filter(None, self.func_map[f_idx][1].split(" "))))
                    self.size_stack -= pops_n
                    for n in range(0, pops_n):
                        self.stack.pop()
                    pushs_n = len(list(filter(None, self.func_map[f_idx][2].split(" "))))
                    self.size_stack += pushs_n
                    for n in range(0, pushs_n):
                        self.stack.append(CALLER_SYSMBOL)
