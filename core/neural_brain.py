import math
import re
import os

class ContextMemory:
    """Agentin istifadəçi ilə əvvəlki dialoqunu və konteksti yadda saxlayan qat"""
    def __init__(self):
        self.last_target = "."
        self.last_intent = None
        self.history = []

    def update(self, intent, target=None):
        self.last_intent = intent
        if target and os.path.exists(target):
            self.last_target = target
        self.history.append({"intent": intent, "target": target})


class CognitivePlanner:
    """Qeyri-müəyyən istəkləri çoxlu-addımlı icra planına çevirən neyron zənciri"""
    MACRO_PLANS = {
        "FULL_AUDIT": {
            "keywords": ["tam yoxla", "bütün sistemi skan et", "hər şeyi audit et", "problem var"],
            "steps": ["FIM", "SCAN", "DEEP_SCAN", "LOG"]
        },
        "HARDEN_SECURITY": {
            "keywords": ["sistemi qoru", "təhlükəsizliyi aktiv et", "müdafiə olun", "qorunma"],
            "steps": ["FIM_BASELINE", "HONEYPOT_START"]
        }
    }

    @classmethod
    def resolve_macro_plan(cls, input_text):
        text = input_text.lower()
        for plan_name, plan_data in cls.MACRO_PLANS.items():
            for kw in plan_data["keywords"]:
                if kw in text:
                    return plan_name, plan_data["steps"]
        return None, []


class NeuralBrain:
    """SI-GUARD İstifadəçi Niyyətini Anlayan Neyron Şəbəkəsi"""
    def __init__(self):
        self.memory = ContextMemory()
        self.neurons = {
            "SCAN": ["skan", "scan", "zəiflik", "zeiflik", "vulnerability"],
            "DEEP_SCAN": ["dərin", "derin", "ast", "analiz", "deep", "sintaksis"],
            "HONEYPOT": ["tələ", "tele", "honeypot", "trap", "saxta port"],
            "FIX": ["düzəlt", "duzelt", "fix", "patch", "yamaq"],
            "LEARN": ["öyrən", "oyren", "ingest", "oxu", "yaddaş"],
            "LOG": ["log", "ip", "brute", "attack", "hücum", "giriş"],
            "REPORT": ["hesabat", "report", "html"],
            "FIM": ["fim", "bütövlük", "butovluk", "integrity", "hash", "heş"],
            "KNOWLEDGE_QUERY": ["nədir", "nedir", "necə", "nece", "haqqında", "soru", "axtar"]
        }

    def _extract_target(self, text):
        """Mətndən fayl və ya qovluq yollarını avtomatik çıxarır"""
        words = text.split()
        for word in words:
            clean_word = word.strip(" '\"`")
            if os.path.exists(clean_word):
                return clean_word
        return None

    def evaluate(self, input_text):
        cmd_clean = input_text.lower().strip()
        
        # 1. Anlaşılma: Mətn daxilində hədəf fayl/qovluq var?
        extracted_target = self._extract_target(input_text)
        target = extracted_target if extracted_target else self.memory.last_target

        # 2. Anlaşılma: İstifadəçi genetik/geniş istək vurğulayır? (Macro-Plan)
        plan_name, plan_steps = CognitivePlanner.resolve_macro_plan(cmd_clean)
        if plan_name:
            self.memory.update(plan_name, target)
            thought_chain = [
                f"🧠 [DÜŞÜNCƏ ZƏNCİRİ]: İstifadəçi mürəkkəb niyyət ifadə etdi -> '{input_text}'",
                f"⚡ [KONTEKST ANLAŞILMASI]: Makro-Plan təyin olundu: **{plan_name}**",
                f"📋 [İCRA ZƏNCİRİ]: { ' -> '.join(plan_steps) }"
            ]
            return {
                "intent": "MACRO_PLAN",
                "plan_steps": plan_steps,
                "target": target,
                "thought_chain": "\n".join(thought_chain)
            }

        # 3. Kontekstual İzah: "Bunu skan et", "Bura bax" kimi nisbi istəklər
        if any(pronoun in cmd_clean for pronoun in ["bunu", "bura", "həmin faylı", "o faylı"]):
            target = self.memory.last_target

        # 4. Neyron Activation Scoring
        tokens = cmd_clean.split()
        activations = {intent: 0.0 for intent in self.neurons}

        for token in tokens:
            for intent, keywords in self.neurons.items():
                for kw in keywords:
                    if kw in token:
                        activations[intent] += 1.5 if kw == token else 0.8

        best_intent = max(activations, key=activations.get)
        raw_score = activations[best_intent]
        confidence = 1 / (1 + math.exp(-raw_score)) if raw_score > 0 else 0.0

        if confidence >= 0.5:
            self.memory.update(best_intent, target)
            thought_chain = [
                f"🧠 [DÜŞÜNCƏ ZƏNCİRİ]: Giriş analiz edilir -> '{input_text}'",
                f"🎯 [ANLAŞILAN NİYYƏT]: {best_intent} (Əminlik: {confidence*100:.1f}%)",
                f"📍 [HƏDƏF SUBYEKT]: `{target}`"
            ]
            decision = best_intent
        else:
            thought_chain = [
                f"🧠 [DÜŞÜNCƏ ZƏNCİRİ]: Giriş analiz edilir -> '{input_text}'",
                "⚠️ [NİYYƏT QEYRİ-MƏYYƏNDİR]: Standart əmr tapılmadı, Bilik Bazasına müraciət edilir."
            ]
            decision = "UNKNOWN"

        return {
            "intent": decision,
            "target": target,
            "thought_chain": "\n".join(thought_chain)
        }
