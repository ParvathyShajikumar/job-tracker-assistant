import imaplib
import email
from email.header import decode_header
from database import init_db, add_application
import os
import json
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env
import re


# Gmail IMAP server
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Load keywords from JSON file
with open("keywords.json", "r") as f:
    KEYWORDS = json.load(f)

def extract_company(subject, body, sender):
    text = (subject or "") + " " + (body or "")

    # Look for "interest in X" or "at X"
    match = re.search(r"(interest in|at)\s+([A-Z][a-zA-Z]+)", text)
    if match:
        return match.group(2)

    # If sender has a domain, use that
    if sender and "@" in sender:
        domain = sender.split("@")[1].split(".")[0]
        return domain.capitalize()

    # Fallback: look for known company names in subject/body
    known_companies = ["Google", "Amazon", "Microsoft", "Deel", "Cognizant", "IBS"]
    for company in known_companies:
        if company.lower() in text.lower():
            return company

    return "Unknown"



def clean_subject(subject):
    """Decode subject line into readable text"""
    decoded, encoding = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding if encoding else "utf-8")
    return decoded

def classify_email(subject, body):
    """Classify email into status based on keywords + fallback"""
    text = (subject or "") + " " + (body or "")
    text = text.lower()

    # Check keyword sets
    for status, words in KEYWORDS.items():
        if any(word in text for word in words):
            return status

    # Fallback logic:
    # If "application" appears but no rejection/offer/interview keywords → Applied
    if "application" in text and not any(word in text for word in KEYWORDS["Rejected"] + KEYWORDS["Interview"] + KEYWORDS["Offer"]):
        return "Applied"

    return "Unclassified"
def extract_role(subject, body):
    text = (subject or "") + " " + (body or "")

    # Look for "position of X"
    match = re.search(r"position of ([A-Za-z ]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Look for "role: X"
    match = re.search(r"role[:\-]\s*([A-Za-z ]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: common job titles in subject
    job_titles = ["Engineer", "Developer", "Analyst", "Manager", "Intern", "Consultant"]
    for title in job_titles:
        if title.lower() in subject.lower():
            return title

    return "Unknown"


def read_emails():
    init_db()  # ensure database exists

    # Connect to Gmail IMAP
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(EMAIL_ACCOUNT, APP_PASSWORD)

    # Select inbox
    imap.select("inbox")

    # Search all emails
    status, messages = imap.search(None, "ALL")
    email_ids = messages[0].split()

    print(f"Found {len(email_ids)} emails.")

    # Read the last 10 emails
    for eid in email_ids[-10:]:
        status, msg_data = imap.fetch(eid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = clean_subject(msg["Subject"])
        date = msg["Date"]
        sender = msg["From"]

        # Extract body text
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        
        # Classify email
        status = classify_email(subject, body)

        # Extract company name
        company = extract_company(subject, body, sender)
        # Extract role
        role = extract_role(subject, body)
        unique_key = f"{company}_{role}_{date}"
        if status in ["Applied", "Interview", "Offer", "Rejected"]:
            # Save to database
            add_application(
                company=company,
                role=role,
                subject=subject,
                date_applied=date,
                status=status,
                unique_key=unique_key
            )
            print(f"Saved: {subject} → {status}")
        else:
            print(f"Skipped non-job mail: {subject}")

        # print(f"Subject: {subject}")
        # print(f"Date: {date}")
        # print(f"From: {sender}")
        # print(f"Company: {company}")
        # print(f"Role: {role}")
        # print(f"Status: {status}")
        # print("-" * 40)

    # Close connection
    imap.close()
    imap.logout()



if __name__ == "__main__":
    read_emails()
