#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod phishable {

    use super::*;

    #[liquid(storage)]
    struct Phishable {
        owner: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl Phishable {
        // constructor
        pub fn new(&mut self, _owner: Address) {
            self.owner.set(_owner);
        }

        pub fn withdrawAll(&mut self, _recipient: Address) {
            // <yes> <report> ACCESS_CONTROL
            if self.owner.eq(&self.env().get_tx_origin()) {
                // _recipient.transfer(balance);
            }
        }
    }
}
