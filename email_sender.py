import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MONTHS_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def _build_html(articles, date_str):
    rows = ""
    for a in articles:
        rows += f"""
        <div style="margin-bottom:28px;padding:16px 20px;border-left:4px solid #c0392b;background:#fafafa;border-radius:0 6px 6px 0;">
          <p style="margin:0 0 4px;font-size:13px;color:#888;">#{a['rank']}</p>
          <h2 style="margin:0 0 8px;font-size:17px;line-height:1.35;">
            <a href="{a['url']}" style="color:#c0392b;text-decoration:none;">{a['title']}</a>
          </h2>
          <p style="margin:0 0 10px;color:#444;font-size:14px;line-height:1.6;">{a['summary']}</p>
          <a href="{a['url']}" style="font-size:12px;color:#888;text-decoration:none;">Leer artículo completo →</a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:30px 0;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;max-width:640px;">
        <!-- Header -->
        <tr>
          <td style="background:#c0392b;padding:24px 32px;">
            <h1 style="margin:0;color:#fff;font-size:22px;letter-spacing:0.5px;">
              📰 Top 10 Noticias &mdash; El Tiempo
            </h1>
            <p style="margin:6px 0 0;color:#f5b7b1;font-size:14px;">{date_str}</p>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:28px 32px;">
            {rows}
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="padding:16px 32px;border-top:1px solid #eee;text-align:center;">
            <p style="margin:0;font-size:12px;color:#aaa;">
              Fuente: <a href="https://www.eltiempo.com" style="color:#c0392b;">El Tiempo</a>
              &nbsp;&bull;&nbsp; Resúmenes generados automáticamente con IA
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _build_plain(articles, date_str):
    lines = [f"TOP 10 NOTICIAS - EL TIEMPO | {date_str}", "=" * 60, ""]
    for a in articles:
        lines.append(f"{a['rank']}. {a['title']}")
        lines.append(a["summary"])
        lines.append(f"   Leer más: {a['url']}")
        lines.append("")
    lines.append("-" * 60)
    lines.append("Fuente: https://www.eltiempo.com | Resúmenes con IA")
    return "\n".join(lines)


def send_email(articles, to_email):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    today = date.today()
    date_str = f"{today.day} de {MONTHS_ES[today.month]} de {today.year}"
    subject = f"📰 Top 10 Noticias El Tiempo – {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_email

    msg.attach(MIMEText(_build_plain(articles, date_str), "plain", "utf-8"))
    msg.attach(MIMEText(_build_html(articles, date_str), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())

    print(f"Email sent to {to_email} — {len(articles)} articles.")
