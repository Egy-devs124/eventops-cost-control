from rest_framework.views import exception_handler


MESSAGE_TRANSLATIONS = {
    "This field is required.": "هذا الحقل مطلوب.",
    "This field may not be null.": "هذا الحقل مطلوب.",
    "This field may not be blank.": "هذا الحقل مطلوب.",
    "Invalid choice.": "خيار غير صالح.",
    "You do not have permission to perform this action.": "ليس لديك صلاحية لتنفيذ هذا الإجراء.",
    "Authentication credentials were not provided.": "يجب تسجيل الدخول أولاً.",
    "No active account found with the given credentials": "اسم المستخدم أو كلمة المرور غير صحيحة.",
    "End date must be after start date.": "يجب أن يكون تاريخ النهاية بعد تاريخ البداية.",
    "Quotation event_start_at and event_end_at are required.": "يجب إدخال تاريخ بداية ونهاية الفعالية لعرض السعر.",
    "start_at and end_at are required.": "يجب إدخال تاريخ البداية والنهاية.",
    "Payroll must be approved before payment.": "يجب اعتماد الرواتب قبل الدفع.",
    "You do not have permission to view profitability.": "ليس لديك صلاحية لعرض الربحية.",
}


def wants_arabic(request):
    if not request:
        return False
    language = (request.headers.get("Accept-Language") or request.GET.get("lang") or "").lower()
    return language.startswith("ar")


def localized_message(request, english, arabic):
    return arabic if wants_arabic(request) else english


def translate_value(value):
    text = str(value)
    if text in MESSAGE_TRANSLATIONS:
        return MESSAGE_TRANSLATIONS[text]
    if "is not a valid choice" in text:
        return "خيار غير صالح."
    return value


def translate_errors(data):
    if isinstance(data, list):
        return [translate_errors(item) for item in data]
    if isinstance(data, dict):
        return {key: translate_errors(value) for key, value in data.items()}
    return translate_value(data)


def localized_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and wants_arabic(context.get("request")):
        response.data = translate_errors(response.data)
    return response
