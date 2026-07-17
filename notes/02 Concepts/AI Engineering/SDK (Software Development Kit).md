---
type: concept
status: learning
week: 1
tags:
  - python
  - api
  - development
category: "    Software & AI Engineering"
---
## Definition

A Software Development Kit (SDK) is a collection of tools, libraries and documentation that allows developers to interact with a platform or service without having to build everything from scratch.

An SDK wraps the underlying API, making it easier and safer to use.

---

## Why it matters

Without an SDK, you would have to manually create HTTP requests, handle authentication, parse JSON responses and manage errors.

The SDK does this for you, allowing you to focus on building your application.

---

## Example

Instead of writing:

```python
# Manually send an HTTP request to the OpenAI API
```

You can use the OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

The SDK handles:
- Authentication
- Sending the request
- Receiving the response
- Converting the JSON into Python objects

---

## Analogy

Think of an API as a restaurant kitchen.

You *could* walk into the kitchen and cook the meal yourself.

The SDK is the waiter.

You simply place your order, and the waiter communicates with the kitchen and brings back your food.

---

## Related Concepts

- [[API]]
- [[HTTP Request]]
- [[JSON]]
- [[OpenAI API]]

---

## Used In

- [[Analytics Insight Generator]]

---

## Interview Answer

An SDK is a collection of libraries and tools that simplifies interacting with an API. It abstracts away low-level details such as authentication, request formatting and response parsing, allowing developers to integrate a service more efficiently.

---

## My Notes

Today I used the OpenAI Python SDK.

Instead of constructing HTTP requests myself, I created an `OpenAI` client and called:

`client.chat.completions.create(...)`

The SDK translated that into an API request and returned a Python object containing the model's response.