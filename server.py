import hashlib

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

EMAIL = "24f3003806@ds.study.iitm.ac.in"

mcp = FastMCP(
    name="Exam Challenge MCP Server",
    instructions="Returns the required SHA-256 answer for an exam challenge header."
)


@mcp.tool
def solve_challenge() -> str:
    """
    Reads the exam challenge from HTTP request headers and returns
    the first 16 lowercase hex characters of SHA-256(challenge:email).
    """
    headers = get_http_headers()

    challenge = headers.get("x-exam-challenge")
    timestamp = headers.get("x-exam-timestamp")
    signature = headers.get("x-exam-signature")

    if not challenge:
        raise ValueError("Missing required header: X-Exam-Challenge")

    challenge = challenge.strip()

    if len(challenge) != 32:
        raise ValueError("X-Exam-Challenge must contain exactly 32 characters")

    try:
        int(challenge, 16)
    except ValueError:
        raise ValueError("X-Exam-Challenge must be hexadecimal")

    if challenge != challenge.lower():
        raise ValueError("X-Exam-Challenge must be lowercase hexadecimal")

    normalized_email = EMAIL.strip().lower()

    value_to_hash = f"{challenge}:{normalized_email}"
    digest = hashlib.sha256(value_to_hash.encode("utf-8")).hexdigest()

    return digest[:16]


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )