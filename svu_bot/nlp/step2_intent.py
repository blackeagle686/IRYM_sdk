class IntentDetector:
    """Step 2: Handled by Member 2 of the NLP team. Categorizes user goals."""
    @staticmethod
    def process(text: str) -> str:
        text = text.lower()
        
        # 1. Greetings
        if any(w in text for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening"]):
            return "GREETING"
        
        # 2. Academic Programs (SVU Specific)
        if any(w in text for w in ["program", "degree", "master", "bait", "bsce", "miq", "mwt", "tic"]):
            return "ACADEMIC_QUERY"
        
        # 3. Exams & Grades
        if any(w in text for w in ["exam", "test", "grade", "mark", "result", "gpa", "quiz"]):
            return "EXAM_INQUIRY"
            
        # 4. Registration & Admission
        if any(w in text for w in ["register", "enroll", "admission", "apply", "application", "fees", "payment"]):
            return "REGISTRATION_INQUIRY"
            
        # 5. Technical Support
        if any(w in text for w in ["login", "password", "access", "error", "website", "lms", "portal"]):
            return "TECH_SUPPORT"
            
        # 6. General Support/Help
        if any(w in text for w in ["help", "support", "contact", "info", "information"]):
            return "GENERAL_HELP"
            
        return "GENERAL_INQUIRY"
