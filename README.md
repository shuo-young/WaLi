# WaLi

A control-flow-based analyzer of Wasm smart contracts.

Supported contract type:

- [x] [Liquid smart contract](https://github.com/WeBankBlockchain/liquid)
- [ ] Other types

## CFG/CG generator

The generator is based on [Octopus](https://github.com/pventuzelo/octopus), a security analysis framework for WebAssembly module and Blockchain Smart Contract.

### Usage

1. Get the bytecode(Hex) of smart contract.
   ```shell
    $ xxd -p ./sample/access_control_withparam.wasm | tr -d $'\n' > contractdemo.bytecode
   ```
2. Replace filename in `wasm.py` and run script, output gv file will be generated in the project root directory.

Demo file: `democg.png`, `cfg.gv`, `cg.gv`

## Detector

WaLi can detect **Access Control** vulnerability currently.
The instructions of Wasm simulator are modeled according to [EVulHunter](https://github.com/EVulHunter/EVulHunter).

### Demo

#### Run demo

```shell
$ cd wasm
$ python3 vul.py -i ../sample/access_control_withparam.wasm -t 1 -o "output.log"
```

#### Output demo

```shell
indirect getCaller path: [[35, 3]]
indirect setStorage path: [[35, 26, 43, 0], [35, 26, 22, 43, 0]]
indirect getStorage path: [[35, 20, 44, 4]]

getCallerOffset: 397
setStorageOffset: 213 1315
call FBEI function index: 3
getCaller value store to memory: 1055472
===================enter the $func20===================
################keyFactor1 judge################
load getCaller memory value at 1055472
keyFactor1 True!
===================leave the $func20===================
################keyFactor2 judge################
tee_local offset: 959
keyFactor2 True!
################keyFactor3 judge################
i32.eqz offset: 961
keyFactor3 True!

######result########
No Vul1.
######result########
```

## Dataset

The dataset is converted from [SmartBugs](https://github.com/smartbugs/smartbugs/tree/master/dataset/access_control), we rewrited them while keeping the program semantic as the same as possible.
