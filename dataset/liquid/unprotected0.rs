#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod unprotected {

    use super::*;

    #[liquid(storage)]
    struct Unprotected {
        owner: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl Unprotected {
        // constructor
        pub fn new(&mut self) {
            self.owner.set(self.env().get_caller());
        }

        // modifer semantic
        pub fn onlyowner(&mut self, address: Address) -> bool {
            if self.env().get_caller() == address {
                true
            } else {
                false
            }
        }

        // This function should be protected
        // <yes> <report> ACCESS_CONTROL
        pub fn changeOwner(&mut self, _newOwner: Address) {
            self.owner.set(_newOwner);
        }

        // omission
    }
}
