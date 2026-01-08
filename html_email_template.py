"""
Beautiful HTML email template for reports
"""
from datetime import datetime


def create_html_email(charts_data):
    """Create a beautiful HTML email with embedded charts"""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Sales & Marketing Report</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
    
    <!-- Email Container -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                
                <!-- Main Content -->
                <table width="700" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                                📊 Daily Sales & Marketing Report
                            </h1>
                            <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 18px;">
                                {today}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Welcome Message -->
                    <tr>
                        <td style="padding: 40px 30px 30px 30px;">
                            <h2 style="color: #2C3E50; margin: 0 0 15px 0; font-size: 24px;">
                                Hello! 👋
                            </h2>
                            <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0;">
                                Here's your comprehensive daily report with AI-powered insights and beautiful visualizations of your sales and marketing performance.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 0 30px;">
                            <div style="height: 2px; background: linear-gradient(to right, #667eea, #764ba2);"></div>
                        </td>
                    </tr>
                    
                    <!-- Sales Section -->
                    <tr>
                        <td style="padding: 40px 30px 20px 30px;">
                            <h2 style="color: #667eea; margin: 0 0 10px 0; font-size: 26px; display: flex; align-items: center;">
                                <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 20px;">💰</span>
                                Sales Performance
                            </h2>
                            <p style="color: #666; font-size: 15px; margin: 0 0 25px 55px; line-height: 1.5;">
                                Regional breakdown and quarterly trends
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Sales by Region Chart -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #e9ecef;">
                                <img src="cid:sales_by_region" alt="Sales by Region" style="width: 100%; height: auto; display: block; border-radius: 5px;">
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Quarterly Performance Chart -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #e9ecef;">
                                <img src="cid:quarterly_performance" alt="Quarterly Performance" style="width: 100%; height: auto; display: block; border-radius: 5px;">
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Product Performance Chart -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #e9ecef;">
                                <img src="cid:product_performance" alt="Product Performance" style="width: 100%; height: auto; display: block; border-radius: 5px;">
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Divider -->
                    <tr>
                        <td style="padding: 0 30px;">
                            <div style="height: 2px; background: linear-gradient(to right, #667eea, #764ba2);"></div>
                        </td>
                    </tr>
                    
                    <!-- Marketing Section -->
                    <tr>
                        <td style="padding: 40px 30px 20px 30px;">
                            <h2 style="color: #764ba2; margin: 0 0 10px 0; font-size: 26px;">
                                <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 20px;">📈</span>
                                Marketing Performance
                            </h2>
                            <p style="color: #666; font-size: 15px; margin: 0 0 25px 55px; line-height: 1.5;">
                                Campaign ROI and channel effectiveness
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Marketing ROI Chart -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #e9ecef;">
                                <img src="cid:marketing_roi" alt="Marketing ROI" style="width: 100%; height: auto; display: block; border-radius: 5px;">
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Channel Performance Chart -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 2px solid #e9ecef;">
                                <img src="cid:channel_performance" alt="Channel Performance" style="width: 100%; height: auto; display: block; border-radius: 5px;">
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Key Metrics Summary -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white;">
                                <h3 style="margin: 0 0 20px 0; font-size: 22px; text-align: center;">
                                    📌 Key Highlights
                                </h3>
                                <table width="100%" cellpadding="10" cellspacing="0">
                                    <tr>
                                        <td width="50%" style="padding: 10px;">
                                            <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; text-align: center;">
                                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Total Revenue</div>
                                                <div style="font-size: 28px; font-weight: bold;">$423K</div>
                                            </div>
                                        </td>
                                        <td width="50%" style="padding: 10px;">
                                            <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; text-align: center;">
                                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Total Conversions</div>
                                                <div style="font-size: 28px; font-weight: bold;">1,100+</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td width="50%" style="padding: 10px;">
                                            <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; text-align: center;">
                                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Best Region</div>
                                                <div style="font-size: 28px; font-weight: bold;">North America</div>
                                            </div>
                                        </td>
                                        <td width="50%" style="padding: 10px;">
                                            <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; text-align: center;">
                                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Top Channel</div>
                                                <div style="font-size: 28px; font-weight: bold;">Digital Ads</div>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Attachments Notice -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #FFF3CD; border-left: 4px solid #FFC107; padding: 20px; border-radius: 5px;">
                                <p style="margin: 0; color: #856404; font-size: 15px;">
                                    <strong>📎 Detailed Reports Attached:</strong><br>
                                    • Sales Performance Report<br>
                                    • Marketing Campaign Report<br>
                                    • Executive Summary
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #2C3E50; padding: 30px; text-align: center;">
                            <p style="color: #ecf0f1; margin: 0 0 10px 0; font-size: 14px;">
                                <strong>Automated Report System</strong><br>
                                Powered by AI • Generated with ❤️
                            </p>
                            <p style="color: #95a5a6; margin: 0; font-size: 12px;">
                                Daily reports delivered at 9:00 AM IST<br>
                                © 2024 Your Company. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    html = create_html_email({})
    with open("email_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Email template preview saved to email_preview.html")

