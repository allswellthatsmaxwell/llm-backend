mod openai_api;

#[macro_use]
extern crate rocket;


use std::env;

use rocket::{Rocket, Build, post, data::Data, http::ContentType};
use reqwest::Client;
use std::io::Read;

#[post("/chat", data = "<data>", format = "application/json")]
async fn chat(data: Data<'_>,
              content_type: &ContentType,
              client: &rocket::State<Client>) -> reqwest::Response {
    // Convert the incoming data stream to a String
    let body = data.to_string().await.unwrap();

    // Forward the request to OpenAI
    let response = client.post("https://api.openai.com/v1/chat/completions")
        .header("Content-Type", content_type.to_string())
        .body(body)
        .send()
        .await
        .unwrap();

    response
}


#[get("/")]
fn index() -> &'static str {
    "Hello, world!"
}

#[launch]
fn rocket() -> Rocket<Build> {
    let api_key = openai_api::get_openai_api_key();
    let client = Client::new();
    rocket::build()
        .manage(client)
        .mount("/", routes![chat])
}

