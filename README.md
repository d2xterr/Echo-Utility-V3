# Echo Utility V3

A comprehensive Discord bot featuring ticket management, moderation tools, staff applications, Minecraft server integration, and much more.

## Features

### 🎫 Ticket System
- **Multi-category tickets**: Support, Media Applications, Player Reports, and Appeals
- **Claim/unclaim system**: Staff can claim tickets for exclusive handling
- **Auto-transcripts**: Automatic transcript generation when tickets are closed
- **Statistics tracking**: Track ticket closure counts per staff member
- **Permission management**: Automatic role-based permissions for ticket channels

### 🛡️ Moderation Tools
- **Warning system**: Issue warnings with automatic role stripping at 5 warnings
- **Timeout/Mute commands**: Temporary restrictions with duration parsing
- **Kick and ban commands**: Full moderation capabilities with DM notifications
- **Staff reporting**: Anonymous staff reporting system
- **Role management**: Add/remove roles with automatic staff movement logging

### 📊 Server Monitoring
- **Minecraft server status**: Real-time server monitoring with player counts
- **Live stream announcements**: Media team can announce streams with auto-detection
- **AFK system**: Automatic AFK status with nickname changes
- **Level system**: XP-based leveling with role rewards

### 👥 Staff Management
- **Staff applications**: Interactive application system with council approval
- **Leave of Absence (LOA)**: Staff can request time off with approval workflow
- **Performance analysis**: Automated promotion/demotion suggestions based on activity
- **Temporary roles**: Time-limited role assignments
- **Staff statistics**: Comprehensive activity tracking

### 🎮 Community Features
- **Media requirements**: Display content creator application requirements
- **Store integration**: Quick access to server store
- **Report system**: Player reporting with evidence upload
- **Leaderboards**: Ticket and report submission rankings
- **User profiles**: Comprehensive user information with level display

## Commands

### Public Commands
- `/status` - Check Minecraft server status
- `/media` - View media creator requirements
- `/store` - Get store link (requires Community role)
- `/afk <reason> <duration>` - Set AFK status
- `/whois [user]` - Get user information
- `/ticket_check [user]` - View ticket statistics
- `/report_check [user]` - View report statistics

### Staff Commands
- `/close` - Close current ticket
- `/rename <new_name>` - Rename ticket channel
- `/add_user <user>` - Add user to ticket
- `/remove_user <user>` - Remove user from ticket (Admin only)
- `/report <username> <duration> <reason>` - Submit player report
- `/timeout <user> <duration> [reason]` - Timeout a user
- `/mute <user> <duration> [reason]` - Mute a user (alias for timeout)

### Council Commands (Admin)
- `/setup_tickets <channel>` - Setup ticket system
- `/setup_staff_applications <channel>` - Setup application system
- `/warn <user> <reason>` - Warn a user
- `/warnings <user>` - Check user warnings
- `/kick <user> [reason]` - Kick a user
- `/ban <user> [reason] [delete_days]` - Ban a user
- `/untimeout <user> [reason]` - Remove timeout from user
- `/r <user> <role>` - Add/remove role from user
- `/loa <reason> <duration>` - Request leave of absence
- `/temprole <user> <role> <duration>` - Give temporary role
- `/add_ticket <user> <amount>` - Add tickets to user count
- `/remove_ticket <user> <amount>` - Remove tickets from user count
- `/add_report <user> <amount>` - Add reports to user count
- `/remove_report <user> <amount>` - Remove reports from user count
- `/ticket_stats` - View server ticket statistics
- `/promo_demo` - Staff performance analysis
- `/ticket_leaderboard` - Top ticket closers
- `/report_leaderboard` - Top report submitters

### Media Team Commands
- `/live <platform> <url> <title>` - Announce live stream
- `/end_live` - End live stream announcement

### Anonymous Commands
- `/rep` - Submit anonymous staff report (requires Community role)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- discord.py library
- aiohttp library
- mcstatus library (optional, for Minecraft server status)

### Installation
1. Clone this repository
2. Install required dependencies:
```bash
pip install discord.py aiohttp mcstatus
```

3. Configure the bot:
   - Replace `TOKEN` with your Discord bot token
   - Update all channel IDs, role IDs, and server information to match your Discord server
   - Set your Minecraft server IP and port

### Required Permissions
The bot requires the following Discord permissions:
- Manage Channels
- Manage Roles
- Manage Nicknames
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands
- Moderate Members (for timeout/mute)
- Kick Members
- Ban Members

### File Structure
The bot creates several JSON files for data persistence:
- `ticket_data.json` - Active and closed ticket information
- `ticket_counts.json` - Staff ticket closure statistics
- `report_data.json` - Pending evidence submissions
- `report_counts.json` - User report submission counts
- `warnings.json` - User warning records
- `temp_roles.json` - Temporary role assignments
- `afk_data.json` - AFK status tracking
- `level_data.json` - User XP and level data

## Configuration

### Role IDs
Update these constants with your server's role IDs:
```python
COUNCIL_ROLE_ID = 1367958497584480256  # Admin role
TEAM_ROLE_ID = 1351291476193181726     # Staff role
TRIAL_ROLE_ID = 1352661651198967819    # Trial staff
HELPER_ROLE_ID = 1351291474297356338   # Helper role
MOD_ROLE_ID = 1351291471931904163      # Moderator role
# ... and more
```

### Channel IDs
Configure these channel IDs for your server:
```python
TICKET_LOGS_CHANNEL_ID = 1351604371925762168      # Ticket transcripts
EVIDENCE_CHANNEL_ID = 1366446077389307945         # Report evidence
APPLICATIONS_CHANNEL_ID = 1353441083895320811     # Staff applications
LOA_CHANNEL_ID = 1389767774280351864              # Leave requests
# ... and more
```

### Category IDs
Set up ticket categories:
```python
SUPPORT_CATEGORY_ID = 1351607210936897547    # General support
MEDIA_CATEGORY_ID = 1354459512517558364      # Media applications
REPORTS_CATEGORY_ID = 1351604012608131193    # Player reports
APPEALS_CATEGORY_ID = 1351291632871538728    # Ban appeals
```

## Features in Detail

### Ticket System
The ticket system supports four types of tickets, each with its own category and permissions. Staff can claim tickets for exclusive handling, and all tickets generate transcripts when closed.

### Moderation System
Includes a progressive warning system where users are automatically stripped of roles after 5 warnings. All moderation actions send DM notifications to affected users.

### Level System
Users gain XP by sending messages, with different XP rates based on their current level. Special roles are awarded at certain level milestones, including a temporary "Echo" role at level 50.

### Staff Management
Comprehensive staff management with application system, LOA requests, performance tracking, and automated promotion/demotion suggestions based on activity metrics.




## Contributing

When contributing to this project:
1. Never commit Discord tokens or sensitive credentials
2. Test all commands thoroughly before deployment
3. Update documentation for new features
4. Follow Discord.py best practices for bot development

## Support

For support with this bot, please:
1. Check the Discord.py documentation
2. Verify all IDs match your server configuration
3. Ensure the bot has proper permissions
4. Check console output for error messages

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2025 dexter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Attribution

If you use this bot or its code, please provide credit by including:
- A link to this repository
- Mention of the original author
- The MIT License notice above

This helps support open source development and lets others find useful resources.
