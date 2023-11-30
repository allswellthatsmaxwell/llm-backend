use std::env;

pub fn get_openai_api_key() -> String {
    match env::var("OPENAI_API_KEY") {
        Ok(val) => val,
        Err(e) => panic!("Failed to read OPENAI_API_KEY from environment: {}", e),
    }
}
