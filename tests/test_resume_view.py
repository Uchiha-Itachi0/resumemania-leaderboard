from ui.resume_view import resume_html

REDACTED = """[name] [name]
Android Developer · Kotlin
Kolkata · [phone] · [email] · [link]
Summary
Android developer with 2 apps on the Play Store.
Experience
Android Intern · Yatri Rides · Jan 2026 – Jun 2026
• Shipped push notifications for driver arrival; 2-star reviews about missed pickups fell
by half.
• Added offline caching with Room.
Skills
Android: Kotlin, Jetpack Compose
"""


def test_resume_html_structures_the_resume():
    out = resume_html(REDACTED, "ishita-codes-android")
    assert "@ishita-codes-android" in out
    assert "Contact details removed" in out
    assert "[name]" not in out and "[phone]" not in out
    assert "<div class='rm-cv-h'>Experience</div>" in out
    assert "<li>Shipped push notifications for driver arrival; 2-star reviews about missed pickups fell by half.</li>" in out
    assert "<strong>Android:</strong>" in out


def test_resume_html_escapes_text():
    out = resume_html("Skills\n• <script>alert(1)</script>", "x")
    assert "<script>" not in out and "&lt;script&gt;" in out
