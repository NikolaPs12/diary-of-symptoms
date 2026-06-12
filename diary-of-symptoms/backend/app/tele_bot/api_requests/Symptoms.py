from api_client.client import BackendAPIError, api_client


async def get_pdf_symptoms(token, user_id, start_date=None, end_date=None):
    pdf_bytes, _filename = await api_client.download_pdf_report(
        user_id=user_id,
        token=token,
        start_date=start_date,
        end_date=end_date,
    )
    return pdf_bytes


async def add_symptom(payload, token):
    try:
        data = await api_client.create_symptom_entry(payload, token=token)
        return {"status": "success", "ai_insights": data.get("ai_insights", "Запись сохранена.")}
    except BackendAPIError as exc:
        return {"status": "error", "message": str(exc)}

