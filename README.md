# FMCSA DOT Leads Automation

Automated system that pulls all newly created USDOT numbers in the U.S. every day from FMCSA/DOT Open Data, formats them into a clean lead list, and delivers it automatically via Google Sheets and email.

## Features

- ✅ Daily fetch of new DOT records from FMCSA Socrata API
- ✅ Date-based filtering (ADD_DATE)
- ✅ Automatic deduplication by DOT number
- ✅ Data formatting with required fields
- ✅ Google Sheets integration (new tab per day)
- ✅ CSV backup files
- ✅ Daily email notifications with attachments
- ✅ Error notifications
- ✅ Pagination handling for large datasets
- ✅ Comprehensive logging

## Requirements

- Python 3.9+
- Socrata API access (free, app token recommended)
- Google Sheets API credentials (service account)
- SMTP email credentials (Gmail or other SMTP server)

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd fmcsa-dot-leads-automation
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Socrata API Configuration
SOCRATA_DOMAIN=data.transportation.gov
SOCRATA_DATASET_ID=49yn-d2k2
SOCRATA_APP_TOKEN=your_app_token_here

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient1@example.com,recipient2@example.com

# Output Configuration (optional)
OUTPUT_DIR=output/csv
```

### 3. Get Socrata API Token

1. Go to https://data.transportation.gov/profile/app_tokens
2. Sign up or log in
3. Create a new app token
4. Copy the token to `.env` file

### 4. Set Up Google Sheets API

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Create a new service account
   - Download the JSON key file
   - Save as `service_account.json` in project root
5. Create or open a Google Sheet
6. Share the sheet with the service account email (found in the JSON file)
7. Copy the Sheet ID from the URL (the long string between `/d/` and `/edit`)
8. Add the Sheet ID to `.env`

### 5. Set Up Email (Gmail Example)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
   - Use this password in `.env` (not your regular password)

### 6. Test the Script

Test with a specific date:

```bash
python main.py --date 2024-01-15
```

Run for yesterday's date (default):

```bash
python main.py
```

## Output Format

The script extracts the following fields:

- DOT Number
- Legal Company Name
- DBA Name
- City
- State
- ZIP Code
- Phone (if available)
- ADD_DATE
- Date Pulled

## Scheduling

### GitHub Actions (Recommended)

The project includes a GitHub Actions workflow that runs daily. To enable:

1. Push code to GitHub repository
2. Add all environment variables as GitHub Secrets:
   - Go to repository Settings > Secrets and variables > Actions
   - Add each environment variable as a secret
3. The workflow will run daily at the scheduled time

### Cron (Local Server)

Add to crontab:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/fmcsa-dot-leads-automation && /usr/bin/python3 main.py >> /var/log/dot_leads.log 2>&1
```

### AWS Lambda / Cloud Functions

Wrap `main.py` in a Lambda handler or cloud function and schedule using EventBridge/Cloud Scheduler.

## File Structure

```
fmcsa-dot-leads-automation/
├── .github/
│   └── workflows/
│       └── daily_dot_fetch.yml    # GitHub Actions workflow
├── main.py                         # Main entry point
├── config.py                       # Configuration management
├── dot_fetcher.py                  # Socrata API client
├── data_processor.py               # Data processing logic
├── google_sheets_handler.py        # Google Sheets integration
├── csv_handler.py                  # CSV file handling
├── email_handler.py                # Email notifications
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env                            # Environment variables (not in git)
├── service_account.json            # Google credentials (not in git)
└── output/                         # CSV output directory (not in git)
    └── csv/
```

## Troubleshooting

### No records found
- Verify the date format (YYYY-MM-DD)
- Check if records exist for that date on data.transportation.gov
- Review Socrata API logs

### Google Sheets errors
- Verify service account JSON file exists and is valid
- Ensure the sheet is shared with the service account email
- Check that Sheet ID is correct

### Email errors
- Verify SMTP credentials are correct
- For Gmail, use App Password (not regular password)
- Check firewall/network settings

### API rate limits
- Socrata API has rate limits; the script includes pagination to handle this
- If you hit limits, wait a few minutes and retry

## Logging

Logs are written to:
- Console output
- `dot_leads_automation.log` file

## License

This project is provided as-is for the specified automation task.
