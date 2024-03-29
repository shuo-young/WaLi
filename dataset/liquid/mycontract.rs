#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod mycontract {

    use super::*;

    #[liquid(storage)]
    struct MyContract {
        owner: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl MyContract {
        // constructor
        pub fn new(&mut self) {
            self.owner.set(self.env().get_caller());
        }

        pub fn sendTo(&mut self, to: Address, value: u128) {
            // <yes> <report> ACCESS_CONTROL
            if self.owner.eq(&self.env().get_tx_origin()) {
                // transfer to receiver
                // let ret = self.transfer(self.env().get_address(), to, value);
            }
        }
    }
}
