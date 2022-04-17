#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod wallet {

    use super::*;

    #[liquid(storage)]
    struct Wallet {
        bonusCodes: storage::Value<Vec<u256>>,
        owner: storage::Value<Address>,
    }

    #[liquid(methods)]
    impl Wallet {
        pub fn new(&mut self) {
            self.bonusCodes.set(Vec::new());
            self.owner.set(self.env().get_caller());
        }

        pub fn PopBonusCode(&mut self) {
            // <yes> <report> ACCESS_CONTROL
            if self.bonusCodes.len() >= 0 as usize {
                self.bonusCodes.len() - 1;
            }
        }

        // omission
    }
}
