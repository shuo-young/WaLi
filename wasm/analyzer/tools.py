from .graph import *

def get_common_edges(a = list(), b = list()):
    common = list()
    if len(a) and len(b):
        for ai in a:
            for bi in b:
                if ai == bi:
                    common.append(ai)
    return common


def enum_func_call_edges(functions, len_imports):
    # return a list of tuple with
    #   (index_func_node_from, index_func_node_to)

    call_edges = list()
    N_FUNCS = len_imports + len(functions)
    # iterate over functions
    for index, func in enumerate(functions):
        node_from = len_imports + index
        # iterates over instruction
        for inst in func.instructions:
            # detect if inst is a call instructions
            if inst.name == "call":  # is_call:
                # print(inst.operand_interpretation)
                # if inst.name == "call":
                # only get the import_id

                import_id = inst.operand_interpretation.split(' ')[1]
                if import_id.startswith('0x'):
                    import_id = int(import_id, 16)
                else:
                    import_id = int(import_id)
                node_to = int(import_id)
                call_edges.append((node_from, node_to))
            # The `call_indirect` operator takes a list of function arguments and as the last operand the index into the table.
            elif inst.name == "call_indirect":
                # the last operand is the index on the table
                # print(inst.operand_interpretation)
                # print(type(inst.insn_byte[1]))
                # print(func.name)
                node_to = int(inst.operand_interpretation.split(',')[-1].split(' ')[
                                  -1])  # node_to is the table of functions to index into.(http://fitzgeraldnick.com/2018/04/26/how-does-dynamic-dispatch-work-in-wasm.html)
                call_edges.append((node_from, N_FUNCS))

    return call_edges

def gen_f_param(cfg, f_name):
    f_blocks = list(b for f in cfg.functions for b in f.basicblocks if f.name == f_name)  # entire block
    f_edges = list(e for e in cfg.edges if e.node_from in list(b.name for b in f_blocks))  # entire
    return f_blocks, f_edges

def gen_g_param(f_blocks, f_edges):
    g_nodes = list(b.name for b in f_blocks)
    g_edges = []
    for e in f_edges:
        g_edges.append((e.node_from, e.node_to))
    return g_nodes, g_edges

def gen_func_graph_params(cfg, f_name):
    f_blocks, f_edges = gen_f_param(cfg, f_name)
    g_nodes, g_edges = gen_g_param(f_blocks, f_edges)
    return f_blocks, f_edges, g_nodes, g_edges


def get_call_offsets(func_edges, func_blocks, get_caller_idx, set_storage_idx):
    getCallerOffset = []
    setStorageOffset = []
    # print(str(get_caller_idx))
    # print(str(set_storage_idx))
    for bb in func_blocks:
        instrs = bb.instructions
        for i in instrs:
            if str(i) == "call " + str(get_caller_idx[0]):
                getCallerOffset.append(i.offset)
            if str(i) == "call " + str(set_storage_idx[0]):
                setStorageOffset.append(i.offset)
    return getCallerOffset, setStorageOffset


def get_call_paths(cfg, func_main_blocks, getCallerOffset, setStorageOffset):
    caller_bb = []
    storage_bb = []
    for offset in getCallerOffset:
        for bb in func_main_blocks:
            if offset > bb.end_offset:
                continue
            else:
                caller_bb.append(bb.name)
                break

    for offset in setStorageOffset:
        for bb in func_main_blocks:
            if offset > bb.end_offset:
                continue
            else:
                storage_bb.append(bb.name)
                break
    # not use func_edges
    func_blocks, func_edges, graph_nodes, graph_edges = gen_func_graph_params(cfg, "main")
    path_all = []
    graph = Graph(graph_nodes, graph_edges)
    for el in caller_bb:
        for sel in storage_bb:
            paths = graph.depth_first_search_path(el, sel)
            paths_blocks = []
            for p in paths:
                p_blocks = blocks_name_to_blocks(p, func_blocks)
                paths_blocks.append(p_blocks)
            path_all.append(paths_blocks)

    return path_all

def get_paths_to_target(paths, func_blocks, focus_funcs):
    # return the paths_foucs in paths which will lead to indirectly call func in focus funcs
    paths_focus = []
    block_focus = []
    for p in paths:
        for b_name in p:
            block = list(b for b in func_blocks if b.name == b_name)[0]
            for i in block.instructions:
                if i.name == "call" and int(i.operand_interpretation.split(" ")[-1]) in focus_funcs:
                    paths_focus.append(p)
                    block_focus.append(block)
                    break
    return paths_focus, block_focus


def get_indirect_targets(wasmvm, paths_focus, func_blocks, func_args, focus_funcs):
    # TODO: refine the paths
    for p_paths_focus in paths_focus:
        path_blocks = []
        for b_name in p_paths_focus:
            block = list(b for b in func_blocks if b.name == b_name)[0]
            path_blocks.append(block)
        wasmvm.trace_func(path_blocks, func_args, focus_funcs)
        # print(wasmvm.indirect_targets)

def blocks_name_to_blocks(blocks_name = list(), func_blocks = list()):
    blocks = []
    for b_name in blocks_name:
        block = list(b for b in func_blocks if b.name == b_name)[0]
        blocks.append(block)
    return blocks


def get_func_paths(cfg, f_name):
    func_blocks, func_edges, graph_nodes, graph_edges = gen_func_graph_params(cfg, f_name)
    graph = Graph(graph_nodes, graph_edges)

    # get all possible paths in the above graph
    # TODO:get all the possible end node
    paths = graph.depth_first_search_path(graph_nodes[0], graph_nodes[-1])
    paths_blocks = []
    for p in paths:
        p_blocks = blocks_name_to_blocks(p, func_blocks)
        paths_blocks.append(p_blocks)
    return paths_blocks

def gen_funcs_call_graph(cfg, N_FUNCS):
    call_edges = enum_func_call_edges(cfg.functions, len(cfg.analyzer.imports_func))
    funcs_idx = list(range(0, N_FUNCS + 1))  # N_FUNCS is the indirect call target
    funcs_edges = []
    for e in call_edges:
        funcs_edges.append((e[0], e[1]))
    return Graph(funcs_idx, funcs_edges)









