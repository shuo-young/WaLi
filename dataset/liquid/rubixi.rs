#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod rubixi {

    use super::*;

    #[liquid(storage)]
    struct Rubixi {
        balance: storage::Value<u32>,
        collectedFees: storage::Value<u32>,
        feePercent: storage::Value<u32>,
        pyramidMultiplier: storage::Value<u32>,
        payoutOrder: storage::Value<u32>,
        creator: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl Rubixi {
        // constructor
        pub fn new(&mut self) {
            self.balance.set(0);
            self.collectedFees.set(0);
            self.feePercent.set(10);
            self.pyramidMultiplier.set(300);
            self.payoutOrder.set(0);
        }

        //Sets creator
        // <yes> <report> ACCESS_CONTROL
        pub fn DynamicPyramid(&mut self) {
            self.creator.set(self.env().get_caller());
        }

        // modifer semantic
        pub fn onlyowner(&mut self, address: Address) -> bool {
            if self.env().get_caller() == address {
                true
            } else {
                false
            }
        }
        // omission
    }
}
