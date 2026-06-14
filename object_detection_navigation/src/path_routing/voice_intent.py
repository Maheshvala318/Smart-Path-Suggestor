class VoiceIntentParser:
    """Parses user spoken language to extract desired start and end locations."""

    def __init__(self, known_pois: set):
        self.known_pois = known_pois

    def parse_route(self, speech_text: str):
        """
        Fuzzy match start and end locations from text like 'Take me to Lab 2'
        Returns: (start_location, end_location) or (None, None)
        """
        # Todo: Implement regex or fuzzy matching
        return None, None
