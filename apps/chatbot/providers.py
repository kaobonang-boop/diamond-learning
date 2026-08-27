"""
AI provider abstraction layer for Ask Tebogo.

Diamond Learning must be able to switch AI backends (OpenAI, Anthropic, or
none at all) by changing settings/environment variables — never by rewriting
application code. Every provider implements the same BaseAIProvider
interface, so apps/chatbot/views.py only ever talks to `get_ai_provider()`.

Configure via .env:
    AI_PROVIDER=echo        # "echo" (default, no key needed) | "openai" | "anthropic"
    AI_API_KEY=...          # never hardcoded, read from the environment only
    AI_MODEL=gpt-4o-mini

To add a new provider (e.g. a different vendor), subclass BaseAIProvider,
implement `reply()`, and register it in PROVIDER_REGISTRY below.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass

from django.conf import settings


@dataclass
class ChatContext:
    """Everything Tebogo is allowed to use to answer a question."""
    subject: str | None = None
    topic: str | None = None
    language: str = "en"
    history: list[dict] | None = None  # [{"role": "user"|"assistant", "content": str}, ...]


class BaseAIProvider(abc.ABC):
    """Common interface every AI backend must implement."""

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.model = model

    @abc.abstractmethod
    def reply(self, message: str, context: ChatContext) -> str:
        """Return Tebogo's reply to `message`, given the conversation context."""
        raise NotImplementedError


class EchoProvider(BaseAIProvider):
    """
    Zero-dependency fallback provider. Used when AI_PROVIDER is unset/"echo"
    or no API key has been configured yet, so the app is fully runnable out
    of the box without any external AI account. Gives a helpful, deterministic
    "study buddy" style response rather than a real model completion.
    """

    def reply(self, message: str, context: ChatContext) -> str:
        subject_bit = f" on {context.subject}" if context.subject else ""
        topic_bit = f" ({context.topic})" if context.topic else ""
        if context.language == "tn":
            return (
                f"Ke a leboga ka potso ya gago{subject_bit}{topic_bit}. "
                "Ga ke na tokelo ya go dirisa AI e e tseneletseng gone jaanong "
                "(AI_PROVIDER ga e a rulaganngwa), fa e le gore o batla dikarabo "
                "tse di feletseng, kopa morutabana kgotsa sekaseka dinoutswana "
                "le dipampiri tse di rarabolotsweng tsa setlhogo se."
            )
        return (
            f"Thanks for the question{subject_bit}{topic_bit}. Tebogo isn't connected "
            "to a live AI provider yet (AI_PROVIDER is set to 'echo' — this is the "
            "no-key fallback so the app runs out of the box). Once AI_PROVIDER and "
            "AI_API_KEY are set in .env, this same message will go to the real model. "
            "In the meantime, check the Notes and Solved Papers for this topic — "
            "they cover the same ground step by step."
        )


class OpenAIProvider(BaseAIProvider):
    """Routes messages to the OpenAI Chat Completions API."""

    def reply(self, message: str, context: ChatContext) -> str:
        if not self.api_key:
            return EchoProvider().reply(message, context)

        try:
            from openai import OpenAI  # imported lazily so the package is optional
        except ImportError:
            return (
                "The 'openai' package isn't installed. Run "
                "`pip install openai` and set AI_PROVIDER=openai, AI_API_KEY in .env."
            )

        client = OpenAI(api_key=self.api_key)
        system_prompt = _build_system_prompt(context)
        messages = [{"role": "system", "content": system_prompt}]
        for turn in (context.history or [])[-10:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=self.model or "gpt-4o-mini",
            messages=messages,
        )
        return response.choices[0].message.content


class AnthropicProvider(BaseAIProvider):
    """Routes messages to the Anthropic Messages API."""

    def reply(self, message: str, context: ChatContext) -> str:
        if not self.api_key:
            return EchoProvider().reply(message, context)

        try:
            import anthropic  # imported lazily so the package is optional
        except ImportError:
            return (
                "The 'anthropic' package isn't installed. Run "
                "`pip install anthropic` and set AI_PROVIDER=anthropic, AI_API_KEY in .env."
            )

        client = anthropic.Anthropic(api_key=self.api_key)
        system_prompt = _build_system_prompt(context)
        messages = []
        for turn in (context.history or [])[-10:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})

        response = client.messages.create(
            model=self.model or "claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")


def _build_system_prompt(context: ChatContext) -> str:
    lang_line = "Reply in Setswana." if context.language == "tn" else "Reply in English."
    focus = f" The student is studying {context.subject}" if context.subject else ""
    focus += f", topic: {context.topic}." if context.topic else "."
    return (
        "You are Tebogo, the academic assistant for Diamond Learning, a study "
        "platform for Botswana students preparing for PSLE, JCE and BGCSE exams. "
        "Answer step by step, stay encouraging, and ground answers in the official "
        "syllabus for the student's level." + focus + " " + lang_line
    )


PROVIDER_REGISTRY = {
    "echo": EchoProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def get_ai_provider() -> BaseAIProvider:
    """Factory: builds the configured provider from settings/.env."""
    provider_key = (getattr(settings, "AI_PROVIDER", "echo") or "echo").lower()
    provider_cls = PROVIDER_REGISTRY.get(provider_key, EchoProvider)
    return provider_cls(api_key=getattr(settings, "AI_API_KEY", ""), model=getattr(settings, "AI_MODEL", ""))
