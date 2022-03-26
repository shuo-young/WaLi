#![cfg_attr(not(feature = "std"), no_std)]

use liquid::storage;
use liquid_lang as liquid;

#[liquid::contract]
mod map {

    use super::*;

    #[liquid(storage)]
    struct Map {
        owner: storage::Value<Address>,
        map: storage::Value<Vec<u256>>,
    }

    #[liquid(methods)]
    impl Map {
        pub fn new(&mut self) {}

        pub fn set(&mut self, key: u32, value: u256) {
            if self.map.len() <= key as usize {
                self.map.push(0.into());
            }
            // <yes> <report> ACCESS_CONTROL
            self.map[key as usize] = value;
        }

        pub fn get(&mut self, key: u32) -> u256{
            self.map[key as usize].clone()
        }

        pub fn withdraw(&mut self) {
            if self.owner == self.env().get_caller() {
                // self.env().get_caller().transfer(balance);
            }
        }
    }
}
