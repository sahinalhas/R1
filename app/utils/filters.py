def register_filters(app):
    """Register custom template filters with the Flask app"""
    
    @app.template_filter('format_time')
    def format_time(value, format="%H:%M"):
        if value and hasattr(value, 'strftime'):
            return value.strftime(format)
        return value

    @app.template_filter('format_date')
    def format_date(value, format="%d.%m.%Y"):
        if value and hasattr(value, 'strftime'):
            return value.strftime(format)
        return value
        
    @app.template_filter('format_phone')
    def format_phone(phone_number):
        """Format a phone number to a readable format: (535) 652 65 28"""
        if not phone_number:
            return ""
            
        # Sadece rakamları al
        digits = ''.join(c for c in str(phone_number) if c.isdigit())
        
        if len(digits) == 10:  # Türkiye standart 10 haneli numara (5xx) xxx xx xx
            return f"({digits[0:3]}) {digits[3:6]} {digits[6:8]} {digits[8:10]}"
        elif len(digits) == 11 and digits.startswith('0'):  # 0 ile başlayan 11 haneli numara
            return f"({digits[1:4]}) {digits[4:7]} {digits[7:9]} {digits[9:11]}"
        else:
            # Diğer formatlar için basit gruplandırma
            chunks = [digits[i:i+3] for i in range(0, len(digits), 3)]
            return ' '.join(chunks)
            
    @app.template_filter('nl2br')
    def nl2br(value):
        """Convert newlines to HTML line breaks"""
        if not value:
            return ""
        
        from markupsafe import Markup
        result = Markup('<br>').join(value.splitlines())
        return result