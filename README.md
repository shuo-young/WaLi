# WaLi

Wasm Analyzer for Liquid Smart Contract

## CFG/CG generator
1. Get the bytecode(Hex) of smart contract
   ```shell
    $ xxd -p ./sample/access_control_withparam.wasm | tr -d $'\n' > contractdemo.bytecode
   ```
2. Replace filename in `ewasm.py` and run script, output gv file will be generated in the project root directory

Demo file: `democg.png`, `cfg.gv`, `cg.gv`

## Detector

WaLi can detect **Access Control** vulnerability currently

### Demo

#### Run demo
```shell
$ cd wasm
$ python3 vul.py -i ../sample/access_control_withparam.wasm -t 1 -o "log1.txt"
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