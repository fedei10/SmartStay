from __future__ import annotations

import re


SupportedLanguage = str


ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
FRENCH_HINT_RE = re.compile(
    r"\b(bonjour|salut|voyage|hôtel|r[eé]server|planifier|je veux|"
    r"fran[cç]ais|itin[eé]raire|proche)\b",
    re.IGNORECASE,
)


def detect_language(text: str | None) -> SupportedLanguage:
    value = (text or "").strip()
    normalized = value.lower()

    if any(phrase in normalized for phrase in ("in arabic", "باللغة العربية", "بالعربية")):
        return "ar"
    if any(phrase in normalized for phrase in ("in french", "en français", "en francais", "بالفرنسية")):
        return "fr"
    if any(phrase in normalized for phrase in ("in english", "بالإنجليزية", "بالانجليزية")):
        return "en"
    if ARABIC_RE.search(value):
        return "ar"
    if FRENCH_HINT_RE.search(value):
        return "fr"
    return "en"


def agent_configuration_error(language: SupportedLanguage, provider: str | None = None) -> str:
    provider_name = provider or "AI provider"
    if language == "ar":
        return (
            f"لا أستطيع اختيار الأداة المناسبة الآن لأن اتصال {provider_name} غير مهيأ أو المفتاح غير صالح. "
            "تحقق من مفاتيح المزود ثم حاول مرة أخرى."
        )
    if language == "fr":
        return (
            f"Je ne peux pas choisir le bon outil pour le moment, car la connexion {provider_name} "
            "n'est pas configurée ou la clé est invalide. Vérifiez la clé fournisseur puis réessayez."
        )
    return (
        f"I cannot choose the right travel tool right now because the {provider_name} connection "
        "is not configured or its API key is invalid. Check the provider key and try again."
    )


def provider_runtime_error(
    language: SupportedLanguage,
    provider: str | None = None,
    error_message: str | None = None,
) -> str:
    provider_name = provider or "AI provider"
    details = (error_message or "").lower()

    is_quota_error = any(
        token in details
        for token in (
            "resource_exhausted",
            "quota exceeded",
            "rate limit",
            "rate-limit",
            "too many requests",
            "429",
        )
    )

    if is_quota_error:
        if language == "ar":
            return (
                f"لا يمكنني استخدام {provider_name} الآن لأن حد الاستخدام أو الحصة قد تم تجاوزها. "
                "حاول مرة أخرى بعد قليل."
            )
        if language == "fr":
            return (
                f"Je ne peux pas utiliser {provider_name} pour le moment car le quota ou la limite "
                "de requêtes a été dépassé. Réessayez dans un instant."
            )
        return (
            f"I cannot use {provider_name} right now because its quota or rate limit was exceeded. "
            "Please try again shortly."
        )

    if language == "ar":
        return (
            f"تعذر علي استخدام {provider_name} الآن بسبب خطأ مؤقت من مزود الذكاء الاصطناعي. "
            "حاول مرة أخرى."
        )
    if language == "fr":
        return (
            f"Je ne peux pas utiliser {provider_name} pour le moment à cause d'une erreur temporaire "
            "du fournisseur IA. Réessayez."
        )
    return (
        f"I cannot use {provider_name} right now because of a temporary AI provider error. "
        "Please try again."
    )


def hotel_search_error(language: SupportedLanguage) -> str:
    if language == "ar":
        return "لم أتمكن من البحث عن الفنادق الآن. حاول مرة أخرى."
    if language == "fr":
        return "Je n'ai pas pu rechercher les hôtels pour le moment. Réessayez."
    return "I could not search hotels right now. Please try again."


def no_hotels_found(language: SupportedLanguage) -> str:
    if language == "ar":
        return "لم أجد فنادق لهذه الوجهة."
    if language == "fr":
        return "Je n'ai trouvé aucun hôtel pour cette destination."
    return "I did not find hotels for that destination."


def hotels_intro(city_name: str | None, language: SupportedLanguage) -> str:
    city = city_name or "that destination"
    if language == "ar":
        return f"هذه بعض الفنادق في {city}:"
    if language == "fr":
        return f"Voici des hôtels à {city} :"
    return f"Here are hotels in {city}:"
