#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod missing {

    use super::*;

    #[liquid(storage)]
    struct Missing {
        owner: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl Missing {
        pub fn new(&mut self) {}

        // modifer semantic
        pub fn onlyowner(&mut self, address: Address) -> bool {
            if self.owner == address {
                true
            } else {
                false
            }
        }

        // The name of the constructor should be Missing
        // Anyone can call the IamMissing once the contract is deployed
        // <yes> <report> ACCESS_CONTROL
        pub fn IamMissing(&mut self) {
            self.owner.set(self.env().get_caller());
        }

        pub fn withdraw(&mut self) {
            if self.onlyowner(self.env().get_caller()) {
                // transfer all assets to the owner
            }
        }

        // omission
    }
}
