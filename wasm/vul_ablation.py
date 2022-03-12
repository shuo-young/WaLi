import getopt
import sys
from analyzer.tools import get_call_offsets, get_call_paths
from analyzer.wasmvm import WasmVM
from analyzer.tools import gen_funcs_call_graph
from analyzer.tools import gen_f_param
from octopus.platforms.ETH.cfg import EthereumCFG

from analyzer.tools import gen_func_graph_params

def usage():
    print(
        '''
        usage: python3 vul.py -i|--input <FILEPATH> -t|--type <VUL_TYPE> -o|--output <OUTPUT_FILENAME>

        VUL_TYPE:
        1.   No Access Control

        OUTPUT FILE PATH:
        ./log/OUTPUT_FILENAME
        '''
    )

def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:t:ho:', ['input', 'type', 'help', 'output'])
    except getopt.GetoptError:
        usage()
        sys.exit()

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit()
        elif opt in ['-i', '--input']:
            file_name = arg
        elif opt in ['-t', '--type']:
            vul_type = arg
        elif opt in ['-o', '--output']:
            output_file = arg
        else:
            print("Error: invalid parameters")
            usage()
            sys.exit()

    print("Detector start!")
    print(file_name, vul_type)
    print("")
    Vuldetect(file_name, vul_type, output_file)
    print("")

def Vuldetect(file_name, vul_type, output_file):
    with open(file_name, 'rb') as f:
        raw = f.read()
    cfg = EthereumCFG(raw, arch='wasm')

    func_proto = cfg.analyzer.get_func_prototypes_ordered()
    func_map = list()
    for f_idx in func_proto:
        func_map.append(f_idx)
    # print(func_map)
    N_FUNCS = len(func_map)

    # indexs
    get_caller_idx = None
    set_storage_idx = None
    get_storage_idx = None

    for f in func_map:
        if f[0] == "getCaller":
            get_caller_idx = func_map.index(f)
        if f[0] == "setStorage":
            set_storage_idx = func_map.index(f)
        if f[0] == "getStorage":
            get_storage_idx = func_map.index(f)
    # print("the index of set_storage is ", set_storage_idx)

    # get main function blocks and edges
    func_main_blocks, func_main_edges = gen_f_param(cfg, "main")

    # get funcs call graph
    graph_funcs = gen_funcs_call_graph(cfg, N_FUNCS)

    # get all paths in the above graph, where the start is main and the terminal is indirect call target
    main_idx = list(f[0] for f in func_map).index("main")
    # print(main_idx)

    # =================================================Vul1=========================================================
    if vul_type == "1":
        vul_access_control = True

        # indirect to getCaller
        paths_indirect_call = graph_funcs.depth_first_search_path(main_idx, get_caller_idx)
        print("indirect getCaller path:", paths_indirect_call)  # blocks name

        # indirect to setStorage
        paths_indirect_set_storage = graph_funcs.depth_first_search_path(main_idx, set_storage_idx)
        print("indirect setStorage path:", paths_indirect_set_storage)  # blocks name

        paths_indirect_get_storage = graph_funcs.depth_first_search_path(main_idx, get_storage_idx)
        print("indirect getStorage path:", paths_indirect_get_storage)  # blocks name

        # opcode simple logic
        # !getCaller | getCaller & setStorage & !getStorage => vul!
        if (len(paths_indirect_call[0]) == 0) or (len(paths_indirect_call[0]) != 0 and len(paths_indirect_set_storage[0]) != 0 and len(paths_indirect_get_storage[0]) == 0):
            print("")
            print("######result########")
            print("Vul1! No Access Control!")
            f = open("log/" + output_file, "a")
            f.write(file_name + "        " + "Vul1! No Access Control!\n")
            f.close()
            print("######result########")
            return
        # get the focused f(s)
        focus_funcs_get_caller = []
        for p in paths_indirect_call:
            focus_funcs_get_caller.append(p[1])
        focus_funcs_get_caller = list(set(focus_funcs_get_caller))
        # print("focused getCaller : " + str(focus_funcs_get_caller))

        focus_funcs_storage = []
        for p in paths_indirect_set_storage:
            focus_funcs_storage.append(p[1])
        focus_funcs_storage = list(set(focus_funcs_storage))
        # print("focused setStorage : " + str(focus_funcs_storage))

        focus_funcs_get_storage = []
        for p in paths_indirect_get_storage:
            focus_funcs_get_storage.append(p[1])
        focus_funcs_get_storage = list(set(focus_funcs_get_storage))
        # print("focused getStorage : " + str(focus_funcs_get_storage))


        focuc_funcs = []
        focuc_funcs.append(focus_funcs_get_caller[0])
        focuc_funcs.append(focus_funcs_get_storage[0])

        break_out_flag = False

        for bb in [func_main_blocks]:
            # wasmvm
            wasmvm = WasmVM(cfg, func_map)
            for b in bb:
                wasmvm.trace_blocks([b], {}, focuc_funcs)
                if wasmvm.keyFactor3 == True:
                    # print("break")
                    break_out_flag = True
                    vul_access_control = False
                    break
            if break_out_flag == True:
                break

        print("")
        print("######result########")
        if vul_access_control:
            print("Vul1! No Access Control!")
            f = open("log/" + output_file, "a")
            f.write(file_name + "        " + "Vul1! No Access Control!\n")
        else:
            print("No Vul1.")
            f = open("log/" + output_file, "a")
            f.write(file_name + "        " + "No Vul1.\n")

        f.close()
        print("######result########")




if __name__ == '__main__':
    Vuldetect("/Users/shall/Paper/wasmAnalyzer/sample/access_control_withparam.wasm","1","log.txt")
    # main(sys.argv)