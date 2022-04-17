#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod wallet {

    use super::*;

    #[liquid(storage)]
    struct Wallet {
        creator: storage::Value<Address>,
        balances: storage::Mapping<Address, u128>,
    }

    #[liquid(event)]
    struct TransferEvent {
        ret_code: i16,
        #[liquid(indexed)]
        from: Address,
        #[liquid(indexed)]
        to: Address,
        value: u128,
    }

    #[liquid(methods)]
    impl Wallet {
        // constructor
        pub fn new(&mut self) {
            self.balances.initialize();
            self.creator.set(self.env().get_caller());
        }

        pub fn withdraw(&mut self, amount: u128) {
            // <yes> <report> ACCESS_CONTROL
            if amount >= *self.balances.get(&self.env().get_caller()).unwrap() {
                // transfer amount to msg.sender
                let ret = self.transfer(self.env().get_address(), self.env().get_caller(), amount);
            }
        }

        // omission

        // transfer logic
        pub fn transfer(&mut self, from: Address, to: Address, value: u128) -> i16 {
            let mut ret_code: i16 = 0;
            let (ok, from_value) = self.select(from.clone());
            if ok != true.into() {
                ret_code = -1;
                self.env().emit(TransferEvent {
                    ret_code,
                    from,
                    to,
                    value,
                });
                return ret_code;
            }

            let (ret, to_value) = self.select(to.clone());
            if ret != true {
                ret_code = -2;
                self.env().emit(TransferEvent {
                    ret_code,
                    from,
                    to,
                    value,
                });
                return ret_code;
            }

            if from_value < value.clone() {
                ret_code = -3;
                self.env().emit(TransferEvent {
                    ret_code,
                    from,
                    to,
                    value,
                });
                return ret_code;
            }

            if to_value.clone() + value.clone() < to_value.clone() {
                ret_code = -4;
                self.env().emit(TransferEvent {
                    ret_code,
                    from,
                    to,
                    value,
                });
                return ret_code;
            }

            self.balances
                .insert(from.clone(), from_value - value.clone());

            self.balances
                .insert(to.clone(), to_value.clone() + value.clone());

            self.env().emit(TransferEvent {
                ret_code,
                from,
                to,
                value,
            });
            return ret_code;
        }

        pub fn select(&mut self, account: Address) -> (bool, u128) {
            if self.balances.contains_key(&account) {
                return (true, self.balances[&account]);
            }
            return (false, 0);
        }
    }
}
