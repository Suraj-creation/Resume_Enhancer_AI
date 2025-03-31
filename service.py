async def upload_resume(file: UploadFile):
    # Validate file type
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Invalid file format")
    
    # Enforce size limit
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")