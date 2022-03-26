#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod wallet {

    use super::*;

    #[liquid(storage)]
    struct Wallet {
        creator: storage::Value<Address>,
        balances: storage::Mapping<Address, u64>,
    }

    #[liquid(methods)]
    impl Wallet {
        // constructor
        pub fn new(&mut self) {}

        // <yes> <report> ACCESS_CONTROL
        pub fn initWallet(&mut self) {
            self.creator.set(self.env().get_caller());
        }

        // omission
    }
}
