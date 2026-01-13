# FMCSA DOT Leads Automation

Automated system that pulls all newly created USDOT numbers in the U.S. every day from FMCSA/DOT Open Data, formats them into a clean lead list, and delivers it automatically via Google Sheets and email.

## Quick Start (Docker - Recommended)

**Production Mode - Single command to start and run continuously:**

```bash
./start.sh
```

This will:
- Build the Docker container
- Start the container in the background
- Keep it running continuously
- Execute tasks daily at 2:00 AM automatically
- Continue running until you stop it with `docker-compose down`

**Test Mode - Run every 5 minutes for testing:**

```bash
./start-test.sh
```

This will:
- Build the Docker container
- Start in TEST MODE
- Execute tasks every 5 minutes (instead of daily)
- Perfect for testing and development
- Same functionality as production mode

**Stop the container:**

```bash
./stop.sh
```

This will:
- Stop and remove the Docker container
- Clean up resources
- Show status and restart instructions

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

The project supports multiple scheduling options:

### 1. GitHub Actions (Recommended for GitHub-hosted projects)

The project includes a GitHub Actions workflow that runs daily. To enable:

1. Push code to GitHub repository
2. Add all environment variables as GitHub Secrets:
   - Go to repository Settings > Secrets and variables > Actions
   - Add each environment variable as a secret:
     - `SOCRATA_APP_TOKEN`
     - `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON content)
     - `GOOGLE_SHEET_ID`
     - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
     - `EMAIL_FROM`, `EMAIL_TO`
3. The workflow will run daily at 2:00 AM UTC
4. You can also trigger manually from the Actions tab

**Workflow file:** `.github/workflows/daily_dot_fetch.yml`

### 2. Cron (Local Server / VPS)

For running on a local server or VPS:

**Option A: Use the setup script (recommended)**
```bash
./setup_cron.sh
```

**Option B: Manual setup**
```bash
# Edit crontab
crontab -e

# Add this line (adjust path and time as needed):
0 2 * * * cd /path/to/fmcsa-dot-leads-automation && /usr/bin/python3 main.py >> /var/log/dot_leads_automation.log 2>&1
```

**Logs:** Check `/var/log/dot_leads_automation.log` for execution logs

### 3. AWS Lambda

Deploy as an AWS Lambda function with EventBridge (CloudWatch Events) scheduling:

**Steps:**
1. Package the project:
   ```bash
   zip -r lambda_function.zip . -x "*.git*" -x "output/*" -x "*.log"
   ```

2. Create Lambda function:
   - Runtime: Python 3.9+
   - Handler: `lambda_handler.lambda_handler`
   - Upload `lambda_function.zip`

3. Set environment variables in Lambda configuration

4. Create EventBridge rule:
   - Schedule: `cron(0 2 * * ? *)` (daily at 2 AM UTC)
   - Target: Your Lambda function

**Handler file:** `lambda_handler.py`

### 4. Google Cloud Functions

Deploy as a Google Cloud Function with Cloud Scheduler:

**Steps:**
1. Deploy the function:
   ```bash
   gcloud functions deploy dot-leads-automation \
     --runtime python39 \
     --trigger-http \
     --entry-point cloud_function_handler \
     --set-env-vars SOCRATA_APP_TOKEN=xxx,GOOGLE_SHEET_ID=xxx,...
   ```

2. Create Cloud Scheduler job:
   ```bash
   gcloud scheduler jobs create http dot-leads-daily \
     --schedule="0 2 * * *" \
     --uri="https://REGION-PROJECT.cloudfunctions.net/dot-leads-automation" \
     --http-method=POST
   ```

**Handler file:** `cloud_function_handler.py`

### 5. Azure Functions

Similar to AWS Lambda, deploy as an Azure Function with Timer trigger.

### 6. PM2 Process Manager

PM2 is a process manager that can manage your Python script with monitoring, logging, and auto-restart capabilities.

**Prerequisites:**
- Node.js installed (PM2 requires Node.js)
- Install PM2: `npm install -g pm2`

**Option A: Use the setup script (recommended)**
```bash
./setup_pm2.sh
```

**Option B: Manual setup**
```bash
# Start with PM2
pm2 start ecosystem.config.js

# Or start the one-time execution version
pm2 start ecosystem.config.js --only dot-leads-automation-once

# Save PM2 process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
pm2 save
```

**PM2 Features:**
- Process monitoring and auto-restart
- Log management (rotated logs)
- Memory/CPU monitoring
- Built-in cron scheduling (via `cron_restart`)
- Web dashboard: `pm2 web`

**Useful PM2 Commands:**
```bash
pm2 list                          # List all processes
pm2 logs dot-leads-automation     # View logs
pm2 monit                         # Monitor processes
pm2 stop dot-leads-automation     # Stop the process
pm2 restart dot-leads-automation  # Restart the process
pm2 delete dot-leads-automation   # Remove from PM2
```

**For scheduled execution:**
- Use `cron_restart` in `ecosystem.config.js` (runs daily at 2 AM)
- Or combine with cron: `0 2 * * * pm2 restart dot-leads-automation-once`

**Configuration file:** `ecosystem.config.js`

### 7. Docker (Containerized Deployment) - **RECOMMENDED**

Docker provides a consistent environment and the easiest way to run the automation continuously.

**Prerequisites:**
- Docker installed: https://docs.docker.com/get-docker/
- Docker Compose installed (usually included with Docker Desktop)

**🚀 Quick Start - Production Mode:**
```bash
./start.sh
```

This single command will:
- Build the Docker container
- Start it in the background
- Keep it running continuously
- Execute tasks daily at 2:00 AM automatically
- Continue running until stopped

**🧪 Test Mode - Run every 5 minutes:**
```bash
./start-test.sh
```

Test mode features:
- Runs every 5 minutes (instead of daily)
- Perfect for testing and development
- Same functionality as production mode
- Easy to verify the system is working

**Stop the container:**
```bash
./stop.sh
```

Or manually:
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Switch between modes:**
```bash
# Stop current mode
docker-compose down

# Start production mode (daily at 2 AM)
./start.sh

# OR start test mode (every 5 minutes)
./start-test.sh
```

**Manual Docker Commands:**

**Build and start:**
```bash
docker-compose up --build -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Check status:**
```bash
docker-compose ps
```

**Stop:**
```bash
docker-compose down
```

**Restart:**
```bash
docker-compose restart
```

**How it works:**
- The container runs `scheduler.py` which keeps the container alive
- **Production mode**: Scheduler executes `main.py` daily at 2:00 AM UTC
- **Test mode**: Scheduler executes `main.py` every 5 minutes (configurable)
- Container runs continuously until explicitly stopped
- All logs are saved to `./logs/` directory
- CSV files are saved to `./output/csv/` directory

**Test Mode Configuration:**
You can customize the test interval by setting environment variables:
```bash
# Run every 10 minutes instead of 5
TEST_MODE=true TEST_INTERVAL_MINUTES=10 docker-compose up -d

# Or edit docker-compose.yml and set:
# TEST_INTERVAL_MINUTES=10
```

**Docker Features:**
- ✅ Runs continuously with a single command
- ✅ Automatic scheduled execution (daily at 2 AM)
- ✅ Consistent environment across systems
- ✅ Easy deployment and scaling
- ✅ Isolated dependencies
- ✅ Volume mounting for data persistence
- ✅ Health checks included
- ✅ Auto-restart on failure

**Files:**
- `Dockerfile` - Container definition
- `docker-compose.yml` - Container orchestration
- `scheduler.py` - Continuous scheduler that keeps container running
- `start.sh` - Single command startup script (production mode)
- `start-test.sh` - Test mode startup script (runs every 5 minutes)
- `stop.sh` - Stop script to shutdown the container
- `.dockerignore` - Files excluded from build

**Useful Commands:**
```bash
./start.sh                      # Start production mode (single command)
./start-test.sh                 # Start test mode (every 5 minutes)
./stop.sh                       # Stop container (single command)
docker-compose logs -f          # View logs (follow mode)
docker-compose ps               # Check status
docker-compose restart          # Restart container
docker-compose exec dot-leads-automation bash  # Enter container
```

**Useful Docker Commands:**
```bash
docker-compose up -d              # Start in background
docker-compose down               # Stop containers
docker-compose logs -f            # View logs
docker-compose ps                  # List containers
docker-compose restart            # Restart containers
docker-compose exec dot-leads-automation bash  # Enter container
docker build -t dot-leads-automation:latest .   # Build image
```

### Comparison

| Method | Pros | Cons |
|--------|------|------|
| GitHub Actions | Free, easy setup, integrated with repo | Limited to GitHub repos |
| Cron | Full control, no external dependencies | Requires always-on server |
| PM2 | Process monitoring, logging, auto-restart | Requires Node.js |
| Docker | Consistent environment, easy deployment | Requires Docker installation |
| AWS Lambda | Serverless, scalable, pay-per-use | AWS account required |
| Cloud Functions | Serverless, integrated with GCP | GCP account required |

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
