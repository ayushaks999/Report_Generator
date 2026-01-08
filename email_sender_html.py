"""
Enhanced email sending with HTML templates and embedded images
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from datetime import datetime
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
from html_email_template import create_html_email
import os


def send_html_email_with_charts(report_files, chart_files):
    """Send beautiful HTML email with embedded charts and report attachments"""
    
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Error: Email credentials not configured!")
        return False
    
    today = datetime.now().strftime("%B %d, %Y")
    subject = f"📊 Daily Sales & Marketing Report - {today}"
    
    try:
        # Create message
        msg = MIMEMultipart('related')
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        
        # Create alternative part for HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Plain text version (fallback)
        text_body = f"""Daily Sales & Marketing Report - {today}

Hello,

Please find attached your daily sales and marketing reports with comprehensive visualizations.

Reports included:
"""
        for report_file in report_files:
            text_body += f"- {os.path.basename(report_file)}\n"
        
        text_body += """
Best regards,
Automated Report System
"""
        
        msg_alternative.attach(MIMEText(text_body, 'plain'))
        
        # HTML version with charts
        html_body = create_html_email({})
        msg_alternative.attach(MIMEText(html_body, 'html'))
        
        # Embed chart images
        chart_mapping = {
            'sales_by_region.png': 'sales_by_region',
            'quarterly_performance.png': 'quarterly_performance',
            'product_performance.png': 'product_performance',
            'marketing_roi.png': 'marketing_roi',
            'channel_performance.png': 'channel_performance'
        }
        
        for chart_file in chart_files:
            if os.path.exists(chart_file):
                filename = os.path.basename(chart_file)
                with open(chart_file, 'rb') as f:
                    img = MIMEImage(f.read())
                    cid = chart_mapping.get(filename, filename.replace('.png', ''))
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=filename)
                    msg.attach(img)
                print(f"✓ Embedded chart: {filename}")
        
        # Attach report files
        for report_file in report_files:
            if os.path.exists(report_file):
                with open(report_file, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="txt")
                    attach.add_header('Content-Disposition', 'attachment', 
                                    filename=os.path.basename(report_file))
                    msg.attach(attach)
                print(f"✓ Attached report: {os.path.basename(report_file)}")
        
        # Send email via Gmail SMTP
        app_password = GMAIL_APP_PASSWORD.replace(" ", "")
        
        print("\nConnecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Logging in...")
        server.login(GMAIL_USER, app_password)
        
        print("Sending beautiful HTML email...")
        server.send_message(msg)
        server.quit()
        
        print(f"\n✓ Beautiful HTML email sent successfully to {RECIPIENT_EMAIL}!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing HTML email with visualizations...")
    
    # Test with existing demo reports
    report_files = [
        "demo_sales_north_america.txt",
        "demo_marketing_q2_2024.txt",
        "demo_product_cloud_storage.txt"
    ]
    
    # Generate charts first
    from visualizations import generate_all_charts
    chart_files = generate_all_charts()
    
    # Send email
    send_html_email_with_charts(report_files, chart_files)

