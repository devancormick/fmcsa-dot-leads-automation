/**
 * PM2 Ecosystem Configuration for FMCSA DOT Leads Automation
 * 
 * Install PM2: npm install -g pm2
 * Start: pm2 start ecosystem.config.js
 * Monitor: pm2 monit
 * Logs: pm2 logs dot-leads-automation
 * Stop: pm2 stop dot-leads-automation
 * Restart: pm2 restart dot-leads-automation
 */

module.exports = {
  apps: [
    {
      name: 'dot-leads-automation',
      script: 'main.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: false, // Don't auto-restart after completion (it's a scheduled job)
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true, // Prepend timestamp to logs
      merge_logs: true,
      // Cron mode - runs daily at 2:00 AM
      cron_restart: '0 2 * * *',
      // Or use exec_mode: 'fork' for one-time execution
      exec_mode: 'fork'
    },
    // Alternative: One-time execution mode (run manually or via external scheduler)
    {
      name: 'dot-leads-automation-once',
      script: 'main.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: false,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      merge_logs: true,
      exec_mode: 'fork'
    }
  ]
};
