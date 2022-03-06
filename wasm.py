from octopus.platforms.ETH.cfg import EthereumCFG

# HelloWorld on Kovan Parity Network
file_name = "./contract.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex, arch='wasm')
cfg.visualize()
# visualization
# cfg.visualize_call_flow()