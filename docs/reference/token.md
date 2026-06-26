# Token
Short, human-friendly share tokens used for sharing data between clients.
Tokens are designed to be easy to read and type aloud, while also being cryptographically random and hard to guess.

## Design
To reduce transcription errors, the alphabet excludes visually ambiguous characters:
- The letters `I`, `O`, and `L` are excluded.
- The digits `0` and `1` are excluded.


- Tokens are **case-insensitive**. They are normalized to uppercase on creation.
- Leading and trailing whitespace is stripped on creation.
- A token with an invalid length or characters raises `ValueError`.

## Usage
| Method                         | Description                                     |
|--------------------------------|-------------------------------------------------|
| `Token(value: str)`            | Creates a `Token` from an existing string.      |
| `Token.generate()`             | Generates a new cryptographically random token. |
| `str(token)` / `token.value()` | Returns the token value as a plain string. |