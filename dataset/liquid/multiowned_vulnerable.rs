#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod multiownable {

    use super::*;

    #[liquid(storage)]
    struct MultiOwnable {
        root: storage::Value<Address>,
        owners: storage::Mapping<Address, Address>,
    }

    #[liquid(methods)]
    impl MultiOwnable {
        // constructor
        pub fn new(&mut self) {
            self.root.set(self.env().get_caller());
            self.owners[&self.root] = self.env().get_caller();
        }

        // modifer semantic
        pub fn onlyowner(&mut self, address: Address) -> bool {
            if self.owners[&address] != Address::default() {
                true
            } else {
                false
            }
        }

        /**
         * @dev Adding new owners
         * Note that the "onlyOwner" modifier is missing here.
         */
        // <yes> <report> ACCESS_CONTROL
        pub fn newOwner(&mut self, _owner: Address) -> bool {
            if _owner != Address::default() {
                self.owners[&_owner] = self.env().get_caller();
                true
            } else {
                false
            }
        }

        // omission
    }
}
