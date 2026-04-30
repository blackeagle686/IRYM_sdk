class SVUUIConfig:
    """
    Manages UI/Frontend configuration for the SVU Bot.
    Enables the 8-member team to customize the look and feel without touching HTML.
    """
    THEME_COLORS = {
        "primary": "#38bdf8",
        "background": "#0f172a",
        "bot_bubble": "#334155",
        "user_bubble": "#0369a1"
    }
    
    WELCOME_MESSAGE = "Welcome to SVU Bot! I'm here to help you with your academic inquiries."
    
    NAV_LINKS = [
        {"name": "Programs", "url": "https://www.svuonline.org/en/programs"},
        {"name": "Support", "url": "https://www.svuonline.org/en/support"}
    ]

    @classmethod
    def get_ui_bundle(cls):
        return {
            "colors": cls.THEME_COLORS,
            "welcome": cls.WELCOME_MESSAGE,
            "nav": cls.NAV_LINKS
        }
