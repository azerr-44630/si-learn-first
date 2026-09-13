import math

class NeuralBrain:
    """SI-GUARD Neyron Düşünmə Sistemi"""
    def __init__(self):
        self.neurons = {
            "SCAN": ["skan", "scan", "zəiflik", "zeiflik", "vulnerability", "audit"],
            "DEEP_SCAN": ["dərin", "derin", "ast", "analiz", "deep", "sintaksis"],
            "HONEYPOT": ["tələ", "tele", "honeypot", "trap", "saxta port"],
            "FIX": ["düzəlt", "duzelt", "fix", "patch", "yamaq"],
            "LEARN": ["öyrən", "oyren", "ingest", "oxu", "yaddaş"],
            "LOG": ["log", "ip", "brute", "attack", "hücum", "giriş"],
            "REPORT": ["hesabat", "report", "html"],
            "FIM": ["fim", "bütövlük", "butovluk", "integrity", "hash", "heş"],
            "KNOWLEDGE_QUERY": ["nədir", "nedir", "necə", "nece", "haqqında", "soru", "axtar"]
        }

    def _sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def evaluate(self, input_text):
        tokens = input_text.lower().split()
        activations = {intent: 0.0 for intent in self.neurons}

        for token in tokens:
            for intent, keywords in self.neurons.items():
                for kw in keywords:
                    if kw in token:
                        activations[intent] += 1.5 if kw == token else 0.8

        best_intent = max(activations, key=activations.get)
        raw_score = activations[best_intent]
        confidence = self._sigmoid(raw_score) if raw_score > 0 else 0.0

        thought_chain = [
            f"🧠 [DÜŞÜNCƏ ZƏNCİRİ]: Daxil olan giriş təhlil edilir -> '{input_text}'",
            f"⚡ [NEYRON AKTİVASİYASI]: Ən yüksək reaksiya: {best_intent} (Səviyyə: {confidence*100:.1f}%)"
        ]

        if confidence < 0.5:
            thought_chain.append("⚠️ [QƏRAR]: Əminlik aşağıdır, daxili yaddaşa müraciət edilir.")
            decision = "UNKNOWN"
        else:
            thought_chain.append(f"🎯 [QƏRAR]: {best_intent} modulu icraya yönləndirilir.")
            decision = best_intent

        return {
            "intent": decision,
            "confidence": confidence,
            "thought_chain": "\n".join(thought_chain)
        }
