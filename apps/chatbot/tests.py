from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ChatConversation, ChatMessage
from .providers import ChatContext, EchoProvider, get_ai_provider


class EchoProviderTests(TestCase):
    def test_echo_provider_never_needs_a_key(self):
        provider = EchoProvider()
        reply = provider.reply("Help me with fractions", ChatContext(subject="Mathematics", language="en"))
        self.assertIn("Mathematics", reply)

    def test_echo_provider_responds_in_setswana(self):
        provider = EchoProvider()
        reply = provider.reply("Nthuse", ChatContext(language="tn"))
        self.assertTrue(len(reply) > 0)

    @override_settings(AI_PROVIDER="echo")
    def test_factory_returns_echo_by_default(self):
        provider = get_ai_provider()
        self.assertIsInstance(provider, EchoProvider)

    @override_settings(AI_PROVIDER="nonsense")
    def test_factory_falls_back_to_echo_for_unknown_provider(self):
        provider = get_ai_provider()
        self.assertIsInstance(provider, EchoProvider)


class ChatViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="asker", password="pass12345")

    def test_chat_home_requires_login(self):
        response = self.client.get(reverse("chatbot:chat_home"))
        self.assertEqual(response.status_code, 302)

    def test_new_conversation_and_send_message(self):
        self.client.login(username="asker", password="pass12345")
        response = self.client.post(reverse("chatbot:new_conversation"), {"language": "en"})
        self.assertEqual(response.status_code, 302)
        conversation = ChatConversation.objects.get(user=self.user)

        response = self.client.post(
            reverse("chatbot:send_message", args=[conversation.id]),
            {"message": "How do I balance a chemical equation?"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatMessage.objects.filter(conversation=conversation, role="user").count(), 1)
        self.assertEqual(ChatMessage.objects.filter(conversation=conversation, role="assistant").count(), 1)

    def test_cannot_send_to_another_users_conversation(self):
        other = User.objects.create_user(username="other2", password="pass12345")
        conversation = ChatConversation.objects.create(user=other, title="Private")
        self.client.login(username="asker", password="pass12345")
        response = self.client.post(reverse("chatbot:send_message", args=[conversation.id]), {"message": "hi"})
        self.assertEqual(response.status_code, 404)
