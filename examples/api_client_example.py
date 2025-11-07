"""
Example of interacting with the Transcript Chatbot API.
This demonstrates how a mobile app would use the API.
"""
import asyncio
import httpx
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


async def main():
    """Demonstrate API usage."""

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 80)
        print("Transcript Chatbot API - Client Example")
        print("=" * 80)

        # Step 1: Register a user
        print("\n[1] Registering new user...")
        register_data = {
            "email": "demo@example.com",
            "username": "demo_user",
            "password": "secure_password_123",
        }

        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json=register_data,
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✓ User registered! Token expires in {token_data['expires_in']}s")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # User already exists, try login
                print("  User already exists, logging in instead...")
                response = await client.post(
                    f"{API_BASE_URL}/auth/login",
                    json={
                        "email": register_data["email"],
                        "password": register_data["password"],
                    },
                )
                response.raise_for_status()
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✓ Logged in successfully!")
            else:
                raise

        # Set up authorization header
        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Upload a transcript
        print("\n[2] Uploading transcript...")

        transcript_content = """
        Sprint Planning Meeting
        Date: November 5, 2024
        Team: Engineering

        Sarah: Let's plan our next sprint. We have 10 story points available.

        Mike: I suggest we focus on the authentication bug fix. It's affecting users.

        Sarah: Agreed. That's 5 points. What else?

        Mike: The new dashboard feature is ready for implementation. That's another 5 points.

        Sarah: Perfect. Let's commit to:
        1. Fix authentication bug (5 points) - Mike
        2. Implement dashboard (5 points) - Sarah

        Mike: Sounds good. I'll start on the auth bug today.

        Sarah: Great. Sprint ends November 19th.
        """

        # Create a temporary file for upload
        temp_file = Path("/tmp/transcript.txt")
        temp_file.write_text(transcript_content)

        with open(temp_file, "rb") as f:
            files = {"file": ("transcript.txt", f, "text/plain")}
            data = {
                "meeting_title": "Sprint Planning - Nov 2024",
                "participants": "Sarah, Mike",
                "tags": "sprint-planning, engineering",
            }

            response = await client.post(
                f"{API_BASE_URL}/transcripts/upload",
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            upload_result = response.json()
            transcript_id = upload_result["transcript_id"]
            print(f"✓ Transcript uploaded! ID: {transcript_id}")

        # Clean up temp file
        temp_file.unlink()

        # Step 3: Chat with the transcript
        print("\n[3] Chatting with the transcript...")

        # Note: The actual chat endpoint would be at /chat/
        # This is a simplified example - actual Ragbits chat API
        # uses WebSockets or SSE for streaming

        questions = [
            "What tasks were assigned in this meeting?",
            "When does the sprint end?",
            "Who is working on the authentication bug?",
        ]

        for i, question in enumerate(questions, 1):
            print(f"\n  Question {i}: {question}")
            print("  Answer: [This would connect to the chat WebSocket endpoint]")
            print("          In production, your mobile app would use the Ragbits")
            print("          Chat API WebSocket endpoint at ws://localhost:8000/chat/ws")

        print("\n" + "=" * 80)
        print("API Example completed!")
        print("=" * 80)
        print("\nNext steps:")
        print("- Implement WebSocket client for real-time chat")
        print("- Add error handling and retry logic")
        print("- Implement conversation persistence")
        print("- Add support for multiple transcripts per conversation")


if __name__ == "__main__":
    asyncio.run(main())
