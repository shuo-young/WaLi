#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod contract {

    use super::*;

    #[liquid(storage)]
    struct Contract {
        allowances: storage::Mapping<Address, u64>,
        owner: storage::Value<Address>,
        receiver: storage::Value<Address>
    }

    #[liquid(asset(
            issuer = "发行者的账户地址", fungible = true,
            total = 1000000000, description = "资产描述"
        ))]
    struct SomeAsset;
    #[liquid(methods)]
    impl Contract {
        pub fn new(&mut self, owner: Address) {
            self.allowances.initialize();
            self.owner.initialize(owner);
        }
        pub fn setReceiver(&mut self) {
            // should be qualified to set receiver
            let caller = self.env().get_caller();
            self.receiver.set(caller);
        }
        pub fn transferToReceiver(&mut self) -> bool{
            false
        }
    }
}