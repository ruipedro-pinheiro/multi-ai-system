#!/usr/bin/env python3
"""Send welcome emails to waitlist signups"""
import resend
import json

resend.api_key = "re_hdzbj2E6_MPrJKHfWUeK2z3tF88CjFiap"

# Les 2 personnes qui ont signup
signups = [
    "pedroyverdon@gmail.com",
    "krystian.momot90@wp.pl"
]

for email in signups:
    try:
        params = {
            "from": "CHIKA <onboarding@resend.dev>",
            "to": [email],
            "subject": "Welcome to CHIKA Beta! 🚀",
            "html": f"""
            <html>
            <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #6366f1;">Welcome to CHIKA Beta! 🎉</h2>
                
                <p>Hey there!</p>
                
                <p>You're officially on the <strong>CHIKA beta waitlist</strong>! We're launching in <strong>December 2025</strong> with limited spots.</p>
                
                <h3>What happens next?</h3>
                <ul>
                    <li>We'll email you when beta launches (December 2025)</li>
                    <li>You'll get early access before public release</li>
                    <li>Special pricing for early testers</li>
                </ul>
                
                <h3>Want to help shape CHIKA?</h3>
                <p>Reply to this email with feedback, feature requests, or just to say hi! We're building in public and love hearing from early supporters.</p>
                
                <p style="margin-top: 40px; color: #666;">
                    - Pedro, Founder<br>
                    <a href="https://github.com/ruipedro-pinheiro/CHIKA">Follow us on GitHub</a>
                </p>
                
                <p style="font-size: 12px; color: #999; margin-top: 40px;">
                    You received this because you signed up on ruipedro-pinheiro.github.io/CHIKA. 
                </p>
            </body>
            </html>
            """
        }
        
        result = resend.Emails.send(params)
        print(f"✅ Email sent to {email} (ID: {result['id']})")
        
    except Exception as e:
        print(f"❌ Failed for {email}: {e}")

print("\n🎉 Done! Check your inbox!")
