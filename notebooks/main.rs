use std::{collections::HashMap, fs, time};

use clap::Parser;
use tfhe::shortint::parameters::PARAM_MESSAGE_8_CARRY_0;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
	iris_codes_path: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
	main_tfhe_hamming_distance();

	// main_tfhe_bitxor();

	Ok(())
}

fn main_authentication() -> Result<(), Box<dyn std::error::Error>> {
	let args = Args::parse();
	println!("Reading iris codes from {}", args.iris_codes_path);
	let iris_codes = fs::read_to_string(args.iris_codes_path)?;

	let api_url = "https://httpbin.org/ip";

	println!("Sending authentication request to {api_url}");

	let client = reqwest::blocking::Client::new();

	let response = client
		.post(api_url)
		.body(iris_codes)
		.header("Content-Type", "application/json")
		.send()?;

	println!("Authentication server response {response:#?}");

	Ok(())
}

fn main_tfhe_generator_accumulator() {
	use tfhe::shortint::prelude::*;
	use tfhe::shortint::Parameters;

	// Generate a set of client/server keys, using the default parameters:
	let (client_key, server_key) = gen_keys(PARAM_MESSAGE_8_CARRY_0);

	let msg1 = 3;
	let msg2 = 2;

	// Encrypt two messages using the (private) client key:
	let ct_1 = client_key.encrypt(msg1);
	let ct_2 = client_key.encrypt(msg2);

	// Homomorphically compute an addition
	let ct_add = server_key.unchecked_add(&ct_1, &ct_2);

	let add = client_key.decrypt(&ct_add);
	println!("add={add}");

	// Define the Hamming weight function
	// f: x -> sum of the bits of x
	let f = |x: u64| x.count_ones() as u64;

	// Generate the accumulator for the function
	let acc = server_key.generate_accumulator(f);

	// Compute the function over the ciphertext using the PBS
	let ct_res = server_key.keyswitch_programmable_bootstrap(&ct_add, &acc);

	// Decrypt the ciphertext using the (private) client key
	let output = client_key.decrypt(&ct_res);
	println!("output={output}");

	assert_eq!(output, f(msg1 + msg2));
}

fn generate_keys() -> (tfhe::shortint::ClientKey, tfhe::shortint::ServerKey) {
	use tfhe::shortint::parameters::PARAM_MESSAGE_4_CARRY_4;

	// Generate the client key and the server key:
	println!("Start generating keys");
	let start = time::Instant::now();
	let (cks, sks) = gen_keys(PARAM_MESSAGE_4_CARRY_4);
	let end = time::Instant::now();

	let bits = (cks.parameters.message_modulus.0 as f32).log2();
	let carry = (cks.parameters.carry_modulus.0 as f32).log2();
	let duration = end - start;
	println!("Generated {bits}-bit and {carry}-bit key in {duration:?}");

	(cks, sks)
}

fn main_tfhe_bitxor() {
	// let (cks, sks) = gen_keys(PARAM_MESSAGE_4_CARRY_0);
	let (cks, sks) = generate_keys();

	let zero = cks.encrypt(0);
	let one = cks.encrypt(1);

	let one_zero = sks.unchecked_bitxor(&one, &zero);

	let one_zero = cks.decrypt(&one_zero);
	println!("one ^ zero = {one_zero}, should be = {}", 1 ^ 0);

	let zero_one = sks.unchecked_bitxor(&zero, &one);

	let zero_one = cks.decrypt(&zero_one);
	println!("zero ^ one = {zero_one}, should be = {}", 0 ^ 1);

	let one_one = sks.unchecked_bitxor(&one, &one);

	let one_one = cks.decrypt(&one_one);
	println!("one ^ one = {one_one}, should be = {}", 1 ^ 1);

	let zero_zero = sks.unchecked_bitxor(&zero, &zero);

	let zero_zero = cks.decrypt(&zero_zero);
	println!("zero ^ zero = {zero_zero}, should be = {}", 0 ^ 0);
}

fn main_tfhe_hamming_distance() {
	let (cks, sks) = generate_keys();

	let a1 = [1, 1, 0, 1];
	let a2 = [0, 1, 1, 1];

	let encrypted_a1 = a1.iter().map(|m| cks.encrypt(*m)).collect::<Vec<_>>();
	let encrypted_a2 = a2.iter().map(|m| cks.encrypt(*m)).collect::<Vec<_>>();

	// Compute homomorphically a hamming distance:
	let ct_res = fhe_hamming_distance(sks, &encrypted_a1, &encrypted_a2).unwrap();

	// Decrypt:
	let res = cks.decrypt(&ct_res);
	println!("res={res}");
}

use tfhe::shortint::prelude::*;

// Server side
fn fhe_hamming_distance(
	sks: ServerKey,
	x: &[Ciphertext],
	y: &[Ciphertext],
) -> Result<Ciphertext, Box<dyn std::error::Error>> {
	// TODO: - use checked_bitxor and checked_add
	// TODO: - don't use unwrap
	Ok(x.iter()
		.zip(y.iter())
		.map(|(l, r)| sks.unchecked_bitxor(l, r))
		.reduce(|l, r| sks.unchecked_add(&l, &r))
		.unwrap())
}

fn fhe_hamming_distance_with_shift(
	sks: ServerKey,
	x: &[Ciphertext],
	y: &[Ciphertext],
	n: usize,
) -> Result<Vec<Ciphertext>, Box<dyn std::error::Error>> {
	let mut x = x.to_vec();
	let mut result: Vec<Ciphertext> = Vec::new();

	result.push(fhe_hamming_distance(sks.clone(), &x, y)?);

	for _ in 1..n {
		x.rotate_right(1);
		result.push(fhe_hamming_distance(sks, &x, y)?);
	}

	// let shifted_left = (1..n).into_iter().map(|i| x.rotate_left(i));
	// let shifted_right = (1..n).into_iter().map(|i| x.rotate_right(i));
	// let shifted = shifted_left.chain(shifted_right);
	// let hs = shifted.map(|x| fhe_hamming_distance(sks, x, y));

	Ok(result)
}
