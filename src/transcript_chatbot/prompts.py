"""
Prompts for the Transcript Chatbot system.
"""
from collections.abc import Iterable
from pydantic import BaseModel
from ragbits.core.prompt import Prompt
from ragbits.document_search.documents.element import Element


class TranscriptQuestionInput(BaseModel):
    """Input for transcript question answering."""

    question: str
    context: Iterable[Element]
    transcript_metadata: str = ""  # Optional metadata about the transcripts being queried


class TranscriptQuestionPrompt(Prompt[TranscriptQuestionInput, str]):
    """
    Prompt for answering questions about meeting transcripts.
    """

    system_prompt = """
    You are an intelligent assistant helping users understand and analyze their meeting transcripts.
    Your role is to provide accurate, helpful answers based on the transcript content provided.

    Guidelines:
    - Answer questions based ONLY on the information in the provided transcript context
    - If the context doesn't contain enough information, clearly state that
    - Be concise but comprehensive in your answers
    - When relevant, reference specific parts of the conversation
    - If asked about action items, decisions, or key points, structure your response clearly
    - Maintain a professional and helpful tone
    - If asked about specific people mentioned, ensure you accurately attribute statements
    """

    user_prompt = """
    {% if transcript_metadata %}
    Transcript Information:
    {{ transcript_metadata }}
    {% endif %}

    Question: {{ question }}

    Relevant Transcript Context:
    {% for chunk in context %}
    ---
    {{ chunk.text_representation }}
    {% endfor %}
    ---

    Please provide a clear and accurate answer based on the transcript context above.
    """


class TranscriptSummaryInput(BaseModel):
    """Input for generating transcript summaries."""

    transcript_content: str
    meeting_title: str = "Meeting"
    focus_areas: list[str] = []  # e.g., ["decisions", "action items", "key topics"]


class TranscriptSummaryOutput(BaseModel):
    """Structured output for transcript summary."""

    summary: str
    key_points: list[str]
    action_items: list[str]
    decisions_made: list[str]
    participants_mentioned: list[str]


class TranscriptSummaryPrompt(Prompt[TranscriptSummaryInput, TranscriptSummaryOutput]):
    """
    Prompt for generating structured summaries of meeting transcripts.
    """

    system_prompt = """
    You are an expert at analyzing and summarizing meeting transcripts.
    Your task is to create comprehensive, actionable summaries that help users
    quickly understand what happened in their meetings.
    """

    user_prompt = """
    Meeting: {{ meeting_title }}

    {% if focus_areas %}
    Please pay special attention to: {{ focus_areas | join(", ") }}
    {% endif %}

    Transcript:
    {{ transcript_content }}

    Please provide a structured summary including:
    1. A concise overall summary
    2. Key points discussed
    3. Action items identified
    4. Decisions made
    5. Participants mentioned
    """


class ChatHistoryInput(BaseModel):
    """Input for chat with history context."""

    question: str
    context: Iterable[Element]
    conversation_history: list[dict[str, str]] = []  # Previous messages in format [{"role": "user", "content": "..."}]


class ChatWithHistoryPrompt(Prompt[ChatHistoryInput, str]):
    """
    Prompt for answering questions with conversation history.
    Enables follow-up questions and contextual understanding.
    """

    system_prompt = """
    You are a helpful AI assistant specializing in meeting transcript analysis.
    You maintain context from previous messages in the conversation to provide
    coherent and relevant responses.

    Remember:
    - Reference previous questions and answers when relevant
    - If the user refers to "it", "they", "that meeting", etc., use conversation history to understand the reference
    - Always ground your answers in the provided transcript context
    - Be conversational while remaining professional and accurate
    """

    user_prompt = """
    {% if conversation_history %}
    Previous Conversation:
    {% for msg in conversation_history %}
    {{ msg.role }}: {{ msg.content }}
    {% endfor %}
    {% endif %}

    Current Question: {{ question }}

    Relevant Transcript Context:
    {% for chunk in context %}
    ---
    {{ chunk.text_representation }}
    {% endfor %}
    ---

    Please answer the current question, taking into account the conversation history and transcript context.
    """
